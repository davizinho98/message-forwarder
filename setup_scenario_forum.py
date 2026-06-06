#!/usr/bin/env python3
"""
Create a Telegram forum and topics for scenario-based forwarding.
"""

import asyncio
import json
from pathlib import Path

from pyrogram import Client, raw
from pyrogram.errors import FloodWait
from pyrogram.types import ChatPrivileges

from scenario_classifier import SCENARIO_NAMES


CONFIG_PATH = Path("client_config.json")
TOPIC_ICON_COLORS = [
    0x6FB9F0,
    0xFFD67E,
    0xCB86DB,
    0x8EEE98,
    0xFF93B2,
    0xFB6F5F,
]


async def setup_scenario_forum():
    config = load_config()

    if not config.get("phone_number"):
        print("❌ O setup automático precisa de phone_number para criar o supergrupo como usuário.")
        return False

    group_title = input("Nome do supergrupo/fórum [📊 Alertas por Cenário]: ").strip()
    if not group_title:
        group_title = "📊 Alertas por Cenário"

    group_description = "Alertas classificados automaticamente por cenário."
    source_chat_id_raw = input("ID do grupo source que será monitorado: ").strip()
    if not source_chat_id_raw:
        print("❌ source_chat_id é obrigatório para atualizar o client_config.json.")
        return False

    try:
        source_chat_id = int(source_chat_id_raw)
    except ValueError:
        print("❌ source_chat_id precisa ser um número.")
        return False

    app = Client(
        "scenario_forum_setup_user",
        api_id=config["api_id"],
        api_hash=config["api_hash"],
        phone_number=config["phone_number"],
    )

    async with app:
        me = await app.get_me()
        print(f"👤 Logado como: {me.first_name} (@{me.username or 'sem_username'})")

        forum_chat = await app.create_supergroup(group_title, group_description)
        forum_chat_id = forum_chat.id
        print(f"✅ Supergrupo criado: {forum_chat.title} ({forum_chat_id})")

        forum_peer = await app.resolve_peer(forum_chat_id)
        input_channel = to_input_channel(forum_peer)

        await app.invoke(
            raw.functions.channels.ToggleForum(
                channel=input_channel,
                enabled=True,
            )
        )
        print("✅ Fórum/tópicos ativados")

        for index, scenario_name in enumerate(SCENARIO_NAMES):
            await create_topic(app, input_channel, scenario_name, index)

        scenario_topics = await fetch_scenario_topics(app, input_channel)

        missing_topics = [name for name in SCENARIO_NAMES if name not in scenario_topics]
        if missing_topics:
            print(f"⚠️  {len(missing_topics)} tópico(s) não foram encontrados após criação:")
            for topic_name in missing_topics:
                print(f"   - {topic_name}")
        else:
            print("✅ Todos os 24 tópicos foram criados e mapeados")

        await try_add_bot_to_forum(app, config, forum_chat_id)

    update_config(config, source_chat_id, forum_chat_id, scenario_topics)
    print("✅ client_config.json atualizado com scenario_forwarders")
    print()
    print("🚀 Para iniciar o novo serviço:")
    print("   python3 scenario_forwarder.py")
    return True


async def create_topic(app, input_channel, scenario_name, index):
    color = TOPIC_ICON_COLORS[index % len(TOPIC_ICON_COLORS)]
    try:
        await app.invoke(
            raw.functions.channels.CreateForumTopic(
                channel=input_channel,
                title=scenario_name,
                random_id=app.rnd_id(),
                icon_color=color,
            )
        )
        print(f"✅ Tópico criado: {scenario_name}")
        await asyncio.sleep(0.25)
    except FloodWait as error:
        print(f"⏳ FloodWait: aguardando {error.value}s para criar '{scenario_name}'")
        await asyncio.sleep(error.value)
        await create_topic(app, input_channel, scenario_name, index)


async def fetch_scenario_topics(app, input_channel):
    result = await app.invoke(
        raw.functions.channels.GetForumTopics(
            channel=input_channel,
            offset_date=0,
            offset_id=0,
            offset_topic=0,
            limit=100,
        )
    )

    scenario_topics = {}
    for topic in getattr(result, "topics", []):
        title = getattr(topic, "title", "")
        if title in SCENARIO_NAMES:
            scenario_topics[title] = {
                "message_thread_id": int(topic.id),
                "top_msg_id": int(getattr(topic, "top_message", None) or topic.id),
            }
    return scenario_topics


async def try_add_bot_to_forum(user_app, config, forum_chat_id):
    if not config.get("bot_token"):
        print("ℹ️  Sem bot_token no config; o envio será feito pelo usuário se você usar modo usuário puro.")
        return

    bot_app = Client(
        "scenario_forum_setup_bot",
        api_id=config["api_id"],
        api_hash=config["api_hash"],
        bot_token=config["bot_token"],
    )

    try:
        async with bot_app:
            bot_user = await bot_app.get_me()
            bot_identifier = f"@{bot_user.username}" if bot_user.username else bot_user.id

        try:
            await user_app.add_chat_members(forum_chat_id, bot_identifier)
            print(f"✅ Bot adicionado ao fórum: {bot_identifier}")
        except Exception as error:
            print(f"⚠️  Não consegui adicionar o bot automaticamente: {error}")
            print(f"   Adicione manualmente {bot_identifier} ao grupo {forum_chat_id}.")
            return

        try:
            await user_app.promote_chat_member(
                forum_chat_id,
                bot_user.id,
                privileges=ChatPrivileges(
                    can_manage_chat=True,
                    can_invite_users=True,
                ),
            )
            print("✅ Bot promovido com permissões administrativas básicas")
        except Exception as error:
            print(f"⚠️  Não consegui promover o bot automaticamente: {error}")
            print("   Se o envio falhar, promova o bot manualmente ou libere envio de mensagens no grupo.")
    except Exception as error:
        print(f"⚠️  Não consegui verificar o bot_token: {error}")


def update_config(config, source_chat_id, forum_chat_id, scenario_topics):
    config.setdefault("scenario_forwarders", [])
    config["scenario_forwarders"].append({
        "source_chat_id": source_chat_id,
        "forum_chat_id": forum_chat_id,
        "source_name": "Grupo Source",
        "forum_name": "Alertas por Cenário",
        "strategy_filters": {
            "enabled": True,
            "mode": "whitelist",
            "strategies": ["mapa-de-calor"],
        },
        "scenario_topics": scenario_topics,
    })

    with CONFIG_PATH.open("w", encoding="utf-8") as file:
        json.dump(config, file, indent=2, ensure_ascii=False)


def to_input_channel(peer):
    if isinstance(peer, raw.types.InputPeerChannel):
        return raw.types.InputChannel(
            channel_id=peer.channel_id,
            access_hash=peer.access_hash,
        )
    if isinstance(peer, raw.types.InputChannel):
        return peer
    raise ValueError(f"Peer não é um canal/supergrupo: {type(peer).__name__}")


def load_config():
    if not CONFIG_PATH.exists():
        raise FileNotFoundError("client_config.json não encontrado")

    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


if __name__ == "__main__":
    success = asyncio.run(setup_scenario_forum())
    if not success:
        raise SystemExit(1)
