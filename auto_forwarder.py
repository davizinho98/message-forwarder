#!/usr/bin/env python3
"""
Message Forwarder Automático - Versão Python
Monitora mensagens de um bot específico e encaminha automaticamente para um grupo.
"""

import asyncio
import json
import logging
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatType

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AutoMessageForwarder:
    def __init__(self, config_path="client_config.json"):
        """Inicializa o forwarder automático"""
        self.config = self.load_config(config_path)
        
        # Modo híbrido: Usuário lê, Bot envia
        if self.config.get("bot_token") and self.config.get("phone_number"):
            logger.info("🔄 Modo HÍBRIDO ativado: Usuário lê + Bot envia")
            
            # Cliente USUÁRIO para ler mensagens
            self.user_app = Client(
                name="multi_forwarder_user",
                api_id=self.config["api_id"],
                api_hash=self.config["api_hash"],
                phone_number=self.config["phone_number"]
            )
            
            # Cliente BOT para enviar mensagens
            self.bot_app = Client(
                name="multi_forwarder_bot",
                api_id=self.config["api_id"],
                api_hash=self.config["api_hash"],
                bot_token=self.config["bot_token"]
            )
            
            # App principal é o usuário (para handlers)
            self.app = self.user_app
            self.send_app = self.bot_app  # App para enviar mensagens
            self.hybrid_mode = True
            
        elif self.config.get("bot_token"):
            # Modo BOT puro (apenas bot)
            logger.info("🤖 Modo BOT puro ativado")
            self.app = Client(
                name="multi_forwarder_bot",
                api_id=self.config["api_id"],
                api_hash=self.config["api_hash"],
                bot_token=self.config["bot_token"]
            )
            self.send_app = self.app
            self.hybrid_mode = False
            
        else:
            # Modo USUÁRIO puro (compatibilidade com versão antiga)
            logger.info("👤 Modo USUÁRIO puro ativado")
            self.app = Client(
                name="multi_forwarder",
                api_id=self.config["api_id"],
                api_hash=self.config["api_hash"],
                phone_number=self.config["phone_number"]
            )
            self.send_app = self.app
            self.hybrid_mode = False
        
        # Registra o handler de mensagens
        self.register_handlers()
    
    def load_config(self, config_path):
        """Carrega a configuração do arquivo JSON ou variáveis de ambiente"""
        
        # Primeiro tenta variáveis de ambiente (para deploy em nuvem)
        if os.getenv('API_ID'):
            logger.info("📡 Usando configuração via variáveis de ambiente")
            config = {
                "api_id": int(os.getenv('API_ID')),
                "api_hash": os.getenv('API_HASH'),
                "debug": os.getenv('DEBUG', 'true').lower() == 'true',
            }
            
            # Suporte para bot_token ou phone_number
            if os.getenv('BOT_TOKEN'):
                config["bot_token"] = os.getenv('BOT_TOKEN')
            else:
                config["phone_number"] = os.getenv('PHONE_NUMBER')
            
            # Suporte para configuração antiga (backwards compatibility)
            if os.getenv('SOURCE_USER_ID') and os.getenv('TARGET_CHAT_ID'):
                config["forwarders"] = [{
                    "source_user_id": int(os.getenv('SOURCE_USER_ID')),
                    "target_chat_id": int(os.getenv('TARGET_CHAT_ID')),
                    "strategy_filters": {
                        "enabled": os.getenv('STRATEGY_FILTERS_ENABLED', 'false').lower() == 'true',
                        "mode": os.getenv('STRATEGY_FILTERS_MODE', 'whitelist'),
                        "strategies": os.getenv('STRATEGY_FILTERS_STRATEGIES', '').split(',') if os.getenv('STRATEGY_FILTERS_STRATEGIES') else []
                    }
                }]
        else:
            # Senão usa arquivo JSON (desenvolvimento local)
            try:
                logger.info("📄 Usando configuração via arquivo JSON")
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except FileNotFoundError:
                logger.error(f"❌ Arquivo {config_path} não encontrado e variáveis de ambiente não configuradas")
                logger.error("💡 Configure as variáveis: API_ID, API_HASH, PHONE_NUMBER")
                raise
            except json.JSONDecodeError:
                logger.error(f"❌ Erro ao decodificar JSON do arquivo {config_path}")
                raise
        
        # Converte configuração antiga para nova estrutura se necessário
        if "source_user_id" in config and "target_chat_id" in config:
            logger.info("🔄 Convertendo configuração antiga para nova estrutura multi-fonte")
            old_config = {
                "source_user_id": config.pop("source_user_id"),
                "target_chat_id": config.pop("target_chat_id"),
                "strategy_filters": config.pop("strategy_filters", {
                    "enabled": False,
                    "mode": "whitelist",
                    "strategies": []
                })
            }
            config["forwarders"] = [old_config]
        
        # Valida configurações obrigatórias
        required_fields = ["api_id", "api_hash"]
        for field in required_fields:
            if field not in config or config[field] is None:
                raise ValueError(f"Campo obrigatório '{field}' não encontrado na configuração")
        
        # Valida que tem bot_token OU phone_number (ou ambos para modo híbrido)
        if not config.get("bot_token") and not config.get("phone_number"):
            raise ValueError("É necessário configurar 'bot_token' (para bot) ou 'phone_number' (para usuário) ou ambos (modo híbrido)")
        
        # Valida estrutura de forwarders
        if "forwarders" not in config or not config["forwarders"]:
            raise ValueError("Campo 'forwarders' não encontrado ou vazio na configuração")
        
        # Configura filtros padrão para cada forwarder se necessário
        for i, forwarder in enumerate(config["forwarders"]):
            if "strategy_filters" not in forwarder:
                forwarder["strategy_filters"] = {
                    "enabled": False,
                    "mode": "whitelist",
                    "strategies": []
                }
            
            # Log da configuração de cada forwarder
            strategy_config = forwarder["strategy_filters"]
            source_id = forwarder["source_user_id"]
            target_id = forwarder["target_chat_id"]
            
            if strategy_config.get("enabled", False):
                mode = strategy_config.get("mode", "whitelist")
                strategies = strategy_config.get("strategies", [])
                logger.info(f"🎯 Forwarder {i+1} ({source_id} → {target_id}): Filtros HABILITADOS ({mode}): {', '.join(strategies)}")
            else:
                logger.info(f"🎯 Forwarder {i+1} ({source_id} → {target_id}): Filtros DESABILITADOS")
                
        return config
    
    def register_handlers(self):
        """Registra os handlers de mensagens para todas as fontes configuradas"""
        
        # Separar fontes por tipo (usuários/bots vs grupos/canais)
        user_sources = []
        chat_sources = []
        
        for forwarder in self.config["forwarders"]:
            source_id = forwarder["source_user_id"]
            if source_id > 0:
                # ID positivo = usuário/bot
                user_sources.append(source_id)
            else:
                # ID negativo = grupo/canal
                chat_sources.append(source_id)
        
        # Handler para mensagens privadas de usuários/bots
        if user_sources:
            @self.app.on_message(
                filters.user(user_sources) & 
                filters.private
            )
            async def handle_user_message(client: Client, message: Message):
                """Handler para mensagens de usuários/bots"""
                await self.forward_message(client, message)
        
        # Handler para mensagens de grupos/canais
        if chat_sources:
            @self.app.on_message(
                filters.chat(chat_sources)
            )
            async def handle_chat_message(client: Client, message: Message):
                """Handler para mensagens de grupos/canais"""
                await self.forward_message(client, message)
    
    def should_forward_message(self, message_text: str, forwarder_config: dict) -> bool:
        """Verifica se a mensagem deve ser encaminhada baseado nos filtros de estratégia"""
        
        # Se filtros não estão habilitados, encaminhar tudo
        strategy_config = forwarder_config.get("strategy_filters", {})
        if not strategy_config.get("enabled", False):
            return True
        
        # Se não há texto, não encaminhar
        if not message_text:
            return False
        
        # Extrair primeira e segunda linha (onde está a estratégia)
        first_line = message_text.split('\n')[0].lower().strip()
        second_line = message_text.split('\n')[1].lower().strip() if len(message_text.split('\n')) > 1 else ""
        
        if self.config.get("debug", False):
            source_id = forwarder_config["source_user_id"]
            logger.info(f"🔍 [{source_id}] Analisando primeira linha: '{first_line}'\n Segunda linha: '{second_line}'")
        
        # Lista de estratégias configuradas
        strategies = strategy_config.get("strategies", [])
        mode = strategy_config.get("mode", "whitelist")
        
        # Verificar se alguma estratégia está presente na primeira linha
        strategy_found = False
        matched_strategy = None
        
        for strategy in strategies:
            if strategy.lower() in first_line.lower():
                strategy_found = True
                matched_strategy = strategy
                break
            if strategy.lower() in second_line.lower():
                strategy_found = True
                matched_strategy = strategy
                break
        
        # Aplicar lógica de whitelist ou blacklist
        if mode == "whitelist":
            # Whitelist: só encaminhar se a estratégia estiver na lista
            should_forward = strategy_found
        else:
            # Blacklist: encaminhar tudo EXCETO se a estratégia estiver na lista
            should_forward = not strategy_found
        
        if self.config.get("debug", False):
            source_id = forwarder_config["source_user_id"]
            status = "✅ APROVADA" if should_forward else "❌ BLOQUEADA"
            if matched_strategy:
                logger.info(f"🎯 [{source_id}] Estratégia encontrada: '{matched_strategy}' - {status}")
            else:
                logger.info(f"🎯 [{source_id}] Nenhuma estratégia reconhecida - {status}")
        
        return should_forward
    
    def get_forwarder_config(self, source_user_id: int) -> dict:
        """Encontra a configuração do forwarder para um source_user_id específico"""
        for forwarder in self.config["forwarders"]:
            if forwarder["source_user_id"] == source_user_id:
                return forwarder
        return None
    
    async def forward_message(self, client: Client, message: Message):
        """Encaminha uma mensagem para o grupo de destino apropriado"""
        try:
            # Determinar ID da fonte baseado no tipo de mensagem

                # Mensagem de grupo/canal
            source_id = message.chat.id

            logger.debug(f"📩 Mensagem recebida de {source_id}: {message.text or '[Mídia]'}")
            
            # Encontrar configuração do forwarder para esta fonte
            forwarder_config = self.get_forwarder_config(source_id)
            if not forwarder_config:
                logger.warning(f"⚠️  Nenhuma configuração encontrada para source_id: {source_id}")
                return
            
            # Log da mensagem recebida
            text_preview = (message.text[:50] + "...") if message.text and len(message.text) > 50 else (message.text or "[Mídia]")
            target_id = forwarder_config["target_chat_id"]
            logger.info(f"📨 [{source_id}→{target_id}] Nova mensagem: {text_preview}")
            
            # Verificar filtros de estratégia para este forwarder específico
            if not self.should_forward_message(message.text, forwarder_config):
                logger.info(f"🚫 [{source_id}→{target_id}] Mensagem bloqueada pelos filtros de estratégia")
                return
            
            # Formata a mensagem
            if message.text:
                formatted_message = f"{message.text}"
            else:
                formatted_message = "[Mensagem com mídia]"
            
            # Encaminha para o grupo de destino específico usando o cliente apropriado
            await self.send_app.send_message(
                chat_id=forwarder_config["target_chat_id"],
                text=formatted_message
            )
            
            logger.info(f"✅ [{source_id}→{target_id}] Mensagem encaminhada automaticamente!")
            
        except Exception as e:
            logger.error(f"❌ Erro ao encaminhar mensagem: {e}")
    
    async def start(self):
        """Inicia o cliente e o monitoramento"""
        logger.info("🚀 Iniciando Message Forwarder Automático Multi-Fonte...")
        
        # No modo híbrido, precisamos iniciar ambos os clientes
        if self.hybrid_mode:
            async with self.user_app, self.bot_app:
                # Obtém informações do usuário (para leitura)
                me_user = await self.user_app.get_me()
                logger.info(f"👤 Usuário (leitura): {me_user.first_name} {me_user.last_name or ''} (@{me_user.username or 'sem_username'})")
                
                # Obtém informações do bot (para envio)
                me_bot = await self.bot_app.get_me()
                logger.info(f"🤖 Bot (envio): {me_bot.first_name} (@{me_bot.username or 'sem_username'})")
                
                # Carregar diálogos para popular cache de peers (apenas usuário)
                logger.info("🔄 Carregando cache de diálogos...")
                dialog_count = 0
                async for dialog in self.user_app.get_dialogs(limit=100):
                    dialog_count += 1
                logger.info(f"✅ Cache carregado com {dialog_count} diálogos")
                
                await self._verify_forwarders()
                
                logger.info("👂 Aguardando mensagens de todas as fontes configuradas... (Pressione Ctrl+C para parar)")
                
                # Mantém o cliente rodando
                await asyncio.Event().wait()
        else:
            # Modo normal (apenas um cliente)
            async with self.app:
                # Obtém informações do usuário/bot
                me = await self.app.get_me()
                logger.info(f"👤 Logado como: {me.first_name} {me.last_name or ''} (@{me.username or 'sem_username'})")
                
                # Carregar diálogos para popular cache de peers
                logger.info("🔄 Carregando cache de diálogos...")
                dialog_count = 0
                async for dialog in self.app.get_dialogs(limit=100):
                    dialog_count += 1
                logger.info(f"✅ Cache carregado com {dialog_count} diálogos")
                
                await self._verify_forwarders()
                
                logger.info("👂 Aguardando mensagens de todas as fontes configuradas... (Pressione Ctrl+C para parar)")
                
                # Mantém o cliente rodando
                await asyncio.Event().wait()
    
    async def _verify_forwarders(self):
        """Verifica as configurações de forwarders"""
        logger.info(f"📋 Configurados {len(self.config['forwarders'])} forwarder(s):")
        
        # Verifica cada configuração de forwarder
        for i, forwarder in enumerate(self.config["forwarders"], 1):
            source_id = forwarder["source_user_id"]
            target_id = forwarder["target_chat_id"]
            
            logger.info(f"🔄 Verificando Forwarder {i}: {source_id} → {target_id}")
            
            # Verifica se o usuário fonte existe
            try:
                if source_id == 779230055:  # CornerProBot2
                    try:
                        source_user = await self.app.get_users('@cornerpro2_bot')
                        logger.info(f"✅ Fonte {i}: {source_user.first_name} (@{source_user.username})")
                    except:
                        source_user = await self.app.get_chat(source_id)
                        logger.info(f"✅ Fonte {i}: {source_user.first_name} (ID: {source_id})")
                else:
                    source_user = await self.app.get_chat(source_id)
                    source_name = getattr(source_user, 'title', None) or getattr(source_user, 'first_name', f'ID:{source_id}')
                    logger.info(f"✅ Fonte {i}: {source_name} (ID: {source_id})")
                    

            except Exception as e:
                logger.error(f"❌ Erro ao verificar fonte {i} (ID: {source_id}): {e}")
                logger.error(f"💡 Certifique-se de estar no chat/canal ou ter conversado com o usuário")
                continue
            
            # Verifica se o chat de destino existe (usando send_app para verificar permissões)
            try:
                target_chat = await self.send_app.get_chat(target_id)
                target_name = getattr(target_chat, 'title', f'ID:{target_id}')
                logger.info(f"✅ Destino {i}: {target_name} (ID: {target_id})")
            except Exception as e:
                logger.error(f"❌ Erro ao verificar destino {i} (ID: {target_id}): {e}")
                logger.error(f"💡 Certifique-se de que o bot está no grupo/canal de destino com permissões")
                continue

async def main():
    """Função principal"""
    try:
        forwarder = AutoMessageForwarder()
        await forwarder.start()
    except KeyboardInterrupt:
        logger.info("🛑 Parando o Message Forwarder...")
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")

if __name__ == "__main__":
    asyncio.run(main())
