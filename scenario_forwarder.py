#!/usr/bin/env python3
"""
Scenario-based Telegram message forwarder.
"""

import asyncio
import json
import logging
import os
import secrets

import requests
from pyrogram import Client, filters, raw
from pyrogram.types import Message

from scenario_classifier import (
    SCENARIO_NAMES,
    parse_and_classify,
    should_forward_strategy,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class ScenarioMessageForwarder:
    def __init__(self, config_path="client_config.json"):
        self.config = self.load_config(config_path)

        if self.config.get("bot_token") and self.config.get("phone_number"):
            logger.info("🔄 Modo HÍBRIDO ativado: Usuário lê + Bot envia")
            self.user_app = Client(
                name="scenario_forwarder_user",
                api_id=self.config["api_id"],
                api_hash=self.config["api_hash"],
                phone_number=self.config["phone_number"],
            )
            self.bot_app = Client(
                name="scenario_forwarder_bot",
                api_id=self.config["api_id"],
                api_hash=self.config["api_hash"],
                bot_token=self.config["bot_token"],
            )
            self.app = self.user_app
            self.send_app = self.bot_app
            self.hybrid_mode = True
        elif self.config.get("bot_token"):
            logger.info("🤖 Modo BOT puro ativado")
            self.app = Client(
                name="scenario_forwarder_bot",
                api_id=self.config["api_id"],
                api_hash=self.config["api_hash"],
                bot_token=self.config["bot_token"],
            )
            self.send_app = self.app
            self.hybrid_mode = False
        else:
            logger.info("👤 Modo USUÁRIO puro ativado")
            self.app = Client(
                name="scenario_forwarder",
                api_id=self.config["api_id"],
                api_hash=self.config["api_hash"],
                phone_number=self.config["phone_number"],
            )
            self.send_app = self.app
            self.hybrid_mode = False

        self.register_handlers()

    def load_config(self, config_path):
        if os.getenv("API_ID"):
            logger.info("📡 Usando configuração via variáveis de ambiente")
            config = {
                "api_id": int(os.getenv("API_ID")),
                "api_hash": os.getenv("API_HASH"),
                "debug": os.getenv("DEBUG", "true").lower() == "true",
            }
            if os.getenv("BOT_TOKEN"):
                config["bot_token"] = os.getenv("BOT_TOKEN")
            if os.getenv("PHONE_NUMBER"):
                config["phone_number"] = os.getenv("PHONE_NUMBER")

            if os.getenv("SCENARIO_SOURCE_CHAT_ID") and os.getenv("SCENARIO_FORUM_CHAT_ID"):
                config["scenario_forwarders"] = [{
                    "source_chat_id": int(os.getenv("SCENARIO_SOURCE_CHAT_ID")),
                    "forum_chat_id": int(os.getenv("SCENARIO_FORUM_CHAT_ID")),
                    "strategy_filters": {
                        "enabled": os.getenv("STRATEGY_FILTERS_ENABLED", "false").lower() == "true",
                        "mode": os.getenv("STRATEGY_FILTERS_MODE", "whitelist"),
                        "strategies": [
                            item.strip()
                            for item in os.getenv("STRATEGY_FILTERS_STRATEGIES", "").split(",")
                            if item.strip()
                        ],
                    },
                    "scenario_topics": self._load_scenario_topics_from_env(),
                }]
        else:
            logger.info("📄 Usando configuração via arquivo JSON")
            with open(config_path, "r", encoding="utf-8") as file:
                config = json.load(file)

        for field in ["api_id", "api_hash"]:
            if field not in config or config[field] is None:
                raise ValueError(f"Campo obrigatório '{field}' não encontrado na configuração")

        if not config.get("bot_token") and not config.get("phone_number"):
            raise ValueError("Configure 'bot_token', 'phone_number' ou ambos")

        if not config.get("scenario_forwarders"):
            raise ValueError("Campo 'scenario_forwarders' não encontrado ou vazio na configuração")

        for index, forwarder in enumerate(config["scenario_forwarders"], 1):
            if "source_chat_id" not in forwarder:
                raise ValueError(f"Forwarder {index}: campo 'source_chat_id' é obrigatório")
            if "forum_chat_id" not in forwarder:
                raise ValueError(f"Forwarder {index}: campo 'forum_chat_id' é obrigatório")

            forwarder.setdefault("strategy_filters", {
                "enabled": False,
                "mode": "whitelist",
                "strategies": [],
            })
            forwarder.setdefault("scenario_topics", {})

            missing_topics = [
                scenario
                for scenario in SCENARIO_NAMES
                if not self._get_topic_reference(forwarder["scenario_topics"], scenario)
            ]
            if missing_topics:
                logger.warning(
                    "⚠️  Forwarder %s tem %s tópico(s) ausente(s). "
                    "Mensagens nesses cenários serão ignoradas.",
                    index,
                    len(missing_topics),
                )

            logger.info(
                "🎯 Scenario forwarder %s: %s → %s",
                index,
                forwarder["source_chat_id"],
                forwarder["forum_chat_id"],
            )

        return config

    def register_handlers(self):
        source_chat_ids = list({
            forwarder["source_chat_id"]
            for forwarder in self.config["scenario_forwarders"]
        })

        @self.app.on_message(filters.chat(source_chat_ids))
        async def handle_source_message(client: Client, message: Message):
            await self.process_message(client, message)

    def get_forwarder_configs(self, source_chat_id):
        return [
            forwarder
            for forwarder in self.config["scenario_forwarders"]
            if forwarder["source_chat_id"] == source_chat_id
        ]

    async def process_message(self, client: Client, message: Message):
        source_chat_id = message.chat.id
        message_text = message.text or message.caption

        if not message_text:
            logger.info(f"🚫 [{source_chat_id}] Mensagem sem texto ignorada")
            return

        parsed = parse_and_classify(message_text)
        if not parsed:
            logger.info(f"🚫 [{source_chat_id}] Mensagem não bate com o padrão de alerta")
            return

        alert, scenario_result = parsed
        forwarder_configs = self.get_forwarder_configs(source_chat_id)

        if not forwarder_configs:
            logger.warning(f"⚠️  Nenhuma configuração encontrada para source_chat_id: {source_chat_id}")
            return

        logger.info(
            "📨 [%s] Estratégia '%s' classificada como '%s' (%s)",
            source_chat_id,
            alert.strategy,
            scenario_result.scenario,
            scenario_result.general_scenario,
        )

        for forwarder_config in forwarder_configs:
            forum_chat_id = forwarder_config["forum_chat_id"]

            try:
                if not should_forward_strategy(alert.strategy, forwarder_config.get("strategy_filters", {})):
                    logger.info(
                        "🚫 [%s→%s] Estratégia '%s' bloqueada pelos filtros",
                        source_chat_id,
                        forum_chat_id,
                        alert.strategy,
                    )
                    continue

                topic_ref = self._get_topic_reference(
                    forwarder_config.get("scenario_topics", {}),
                    scenario_result.scenario,
                )
                if not topic_ref:
                    logger.warning(
                        "⚠️  [%s→%s] Tópico não configurado para cenário '%s'",
                        source_chat_id,
                        forum_chat_id,
                        scenario_result.scenario,
                    )
                    continue

                sender_label = await self.send_text_to_topic(
                    chat_id=forum_chat_id,
                    topic_ref=topic_ref,
                    text=message_text,
                )
                logger.info(
                    "✅ [%s→%s/%s] Mensagem enviada para '%s' via %s",
                    source_chat_id,
                    forum_chat_id,
                    topic_ref["message_thread_id"],
                    scenario_result.scenario,
                    sender_label,
                )
            except Exception as error:
                logger.error(
                    "❌ [%s→%s] Erro ao enviar mensagem: %s",
                    source_chat_id,
                    forum_chat_id,
                    error,
                )

    async def send_text_to_topic(self, chat_id, topic_ref, text):
        if self.config.get("bot_token"):
            try:
                await self.send_text_to_topic_with_bot_api(
                    chat_id,
                    topic_ref["message_thread_id"],
                    text,
                )
                return "bot api"
            except Exception as bot_api_error:
                logger.warning(
                    "⚠️  Bot API falhou ao enviar para %s/%s (%s).",
                    chat_id,
                    topic_ref["message_thread_id"],
                    bot_api_error,
                )

        try:
            await self.send_text_to_topic_with_client(
                self.send_app,
                chat_id,
                topic_ref["top_msg_id"],
                text,
            )
            return "bot" if self.hybrid_mode else "cliente"
        except Exception as send_error:
            if not self.hybrid_mode:
                raise send_error

            logger.warning(
                "⚠️  Envio pelo bot falhou para %s/%s (%s). Tentando pelo usuário.",
                chat_id,
                topic_ref["top_msg_id"],
                send_error,
            )
            await self.send_text_to_topic_with_client(
                self.user_app,
                chat_id,
                topic_ref["top_msg_id"],
                text,
            )
            return "usuário"

    async def send_text_to_topic_with_client(self, sender_app, chat_id, top_msg_id, text):
        peer = await sender_app.resolve_peer(chat_id)
        random_id = sender_app.rnd_id() if hasattr(sender_app, "rnd_id") else secrets.randbits(63)

        await sender_app.invoke(
            raw.functions.messages.SendMessage(
                peer=peer,
                message=text,
                random_id=random_id,
                top_msg_id=int(top_msg_id),
            )
        )

    async def send_text_to_topic_with_bot_api(self, chat_id, top_msg_id, text):
        await self.call_bot_api("sendMessage", {
            "chat_id": chat_id,
            "message_thread_id": int(top_msg_id),
            "text": text,
        })

    async def call_bot_api(self, method, payload):
        token = self.config.get("bot_token")
        if not token:
            raise ValueError("bot_token não configurado")

        url = f"https://api.telegram.org/bot{token}/{method}"
        response_data = await asyncio.to_thread(self._post_bot_api, url, payload)
        if not response_data.get("ok"):
            description = response_data.get("description", "erro desconhecido")
            raise RuntimeError(description)
        return response_data.get("result", {})

    async def start(self):
        logger.info("🚀 Iniciando Scenario Forwarder...")

        if self.hybrid_mode:
            async with self.user_app, self.bot_app:
                await self._log_accounts()
                await self._warm_dialog_cache()
                await self._verify_forwarders()
                logger.info("👂 Aguardando alertas dos grupos source... (Ctrl+C para parar)")
                await asyncio.Event().wait()
        else:
            async with self.app:
                await self._log_accounts()
                await self._warm_dialog_cache()
                await self._verify_forwarders()
                logger.info("👂 Aguardando alertas dos grupos source... (Ctrl+C para parar)")
                await asyncio.Event().wait()

    async def _log_accounts(self):
        if self.hybrid_mode:
            user = await self.user_app.get_me()
            bot = await self.bot_app.get_me()
            logger.info(f"👤 Usuário (leitura): {user.first_name} (@{user.username or 'sem_username'})")
            logger.info(f"🤖 Bot (envio): {bot.first_name} (@{bot.username or 'sem_username'})")
        else:
            account = await self.app.get_me()
            logger.info(f"👤 Logado como: {account.first_name} (@{account.username or 'sem_username'})")

    async def _warm_dialog_cache(self):
        dialog_count = 0
        async for _dialog in self.app.get_dialogs(limit=100):
            dialog_count += 1
        logger.info(f"✅ Cache de diálogos carregado com {dialog_count} diálogos")

    async def _verify_forwarders(self):
        logger.info(f"📋 Configurados {len(self.config['scenario_forwarders'])} scenario forwarder(s)")

        for index, forwarder in enumerate(self.config["scenario_forwarders"], 1):
            source_chat_id = forwarder["source_chat_id"]
            forum_chat_id = forwarder["forum_chat_id"]

            try:
                source_chat = await self.app.get_chat(source_chat_id)
                source_name = getattr(source_chat, "title", None) or getattr(source_chat, "first_name", source_chat_id)
                logger.info(f"✅ Fonte {index}: {source_name} ({source_chat_id})")
            except Exception as error:
                logger.error(f"❌ Fonte {index} inválida ({source_chat_id}): {error}")

            try:
                forum_name, sender_label = await self.get_forum_access_label(forum_chat_id)
                logger.info(f"✅ Fórum {index}: {forum_name} ({forum_chat_id}) via {sender_label}")
            except Exception as error:
                logger.error(f"❌ Fórum {index} inválido ({forum_chat_id}): {error}")

    async def get_forum_access_label(self, chat_id):
        try:
            chat = await self.send_app.get_chat(chat_id)
            chat_name = getattr(chat, "title", chat_id)
            return chat_name, "bot" if self.hybrid_mode else "cliente"
        except Exception as send_error:
            if self.config.get("bot_token"):
                chat_data = await self.call_bot_api("getChat", {"chat_id": chat_id})
                return chat_data.get("title", chat_id), "bot api"

            if self.hybrid_mode:
                chat = await self.user_app.get_chat(chat_id)
                chat_name = getattr(chat, "title", chat_id)
                return chat_name, "usuário"

            raise send_error

    @staticmethod
    def _get_topic_reference(scenario_topics, scenario):
        configured_value = scenario_topics.get(scenario)
        scenario_lower = scenario.lower()
        if not configured_value:
            for configured_scenario, topic_value in scenario_topics.items():
                if configured_scenario.lower() == scenario_lower and topic_value:
                    configured_value = topic_value
                    break

        if not configured_value:
            return None

        if isinstance(configured_value, dict):
            message_thread_id = configured_value.get("message_thread_id") or configured_value.get("id")
            top_msg_id = configured_value.get("top_msg_id") or configured_value.get("top_message") or message_thread_id
            if not message_thread_id or not top_msg_id:
                return None
            return {
                "message_thread_id": int(message_thread_id),
                "top_msg_id": int(top_msg_id),
            }

        topic_id = int(configured_value)
        return {
            "message_thread_id": topic_id,
            "top_msg_id": topic_id,
        }

    @staticmethod
    def _get_topic_id(scenario_topics, scenario):
        topic_ref = ScenarioMessageForwarder._get_topic_reference(scenario_topics, scenario)
        if not topic_ref:
            return None
        return topic_ref["message_thread_id"]

    @staticmethod
    def _load_scenario_topics_from_env():
        raw_topics = os.getenv("SCENARIO_TOPICS_JSON")
        if not raw_topics:
            return {}
        try:
            return json.loads(raw_topics)
        except json.JSONDecodeError:
            logger.error("❌ SCENARIO_TOPICS_JSON não é um JSON válido")
            return {}

    @staticmethod
    def _post_bot_api(url, payload):
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()


async def main():
    try:
        forwarder = ScenarioMessageForwarder()
        await forwarder.start()
    except KeyboardInterrupt:
        logger.info("🛑 Parando o Scenario Forwarder...")
    except Exception as error:
        logger.error(f"❌ Erro fatal: {error}")


if __name__ == "__main__":
    asyncio.run(main())
