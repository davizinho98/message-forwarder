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
        
        # Cria o cliente Telegram
        self.app = Client(
            name="message_forwarder_main",
            api_id=self.config["api_id"],
            api_hash=self.config["api_hash"],
            phone_number=self.config["phone_number"]
        )
        
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
                "phone_number": os.getenv('PHONE_NUMBER'),
                "source_user_id": int(os.getenv('SOURCE_USER_ID', 779230055)),
                "target_chat_id": int(os.getenv('TARGET_CHAT_ID')),
                "debug": os.getenv('DEBUG', 'true').lower() == 'true',
                "strategy_filters": {
                    "enabled": os.getenv('STRATEGY_FILTERS_ENABLED', 'false').lower() == 'true',
                    "mode": os.getenv('STRATEGY_FILTERS_MODE', 'whitelist'),
                    "strategies": os.getenv('STRATEGY_FILTERS_STRATEGIES', '').split(',') if os.getenv('STRATEGY_FILTERS_STRATEGIES') else []
                }
            }
        else:
            # Senão usa arquivo JSON (desenvolvimento local)
            try:
                logger.info("📄 Usando configuração via arquivo JSON")
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except FileNotFoundError:
                logger.error(f"❌ Arquivo {config_path} não encontrado e variáveis de ambiente não configuradas")
                logger.error("💡 Configure as variáveis: API_ID, API_HASH, PHONE_NUMBER, TARGET_CHAT_ID")
                raise
            except json.JSONDecodeError:
                logger.error(f"❌ Erro ao decodificar JSON do arquivo {config_path}")
                raise
                
        # Valida configurações obrigatórias
        required_fields = ["api_id", "api_hash", "phone_number", "source_user_id", "target_chat_id"]
        for field in required_fields:
            if field not in config or config[field] is None:
                raise ValueError(f"Campo obrigatório '{field}' não encontrado na configuração")
        
        # Configurar filtros de estratégia padrão se não existirem
        if "strategy_filters" not in config:
            config["strategy_filters"] = {
                "enabled": False,
                "mode": "whitelist", 
                "strategies": []
            }
        
        # Log da configuração de filtros
        strategy_config = config["strategy_filters"]
        if strategy_config.get("enabled", False):
            mode = strategy_config.get("mode", "whitelist")
            strategies = strategy_config.get("strategies", [])
            logger.info(f"🎯 Filtros de estratégia HABILITADOS ({mode}): {', '.join(strategies)}")
        else:
            logger.info("🎯 Filtros de estratégia DESABILITADOS - Todas as mensagens serão encaminhadas")
                
        return config
    
    def register_handlers(self):
        """Registra os handlers de mensagens"""
        
        @self.app.on_message(
            filters.user(self.config["source_user_id"]) & 
            filters.private
        )
        async def handle_source_message(client: Client, message: Message):
            """Handler para mensagens do bot fonte (CornerProBot2)"""
            await self.forward_message(client, message)
    
    def should_forward_message(self, message_text: str) -> bool:
        """Verifica se a mensagem deve ser encaminhada baseado nos filtros de estratégia"""
        
        # Se filtros não estão habilitados, encaminhar tudo
        strategy_config = self.config.get("strategy_filters", {})
        if not strategy_config.get("enabled", False):
            return True
        
        # Se não há texto, não encaminhar
        if not message_text:
            return False
        
        # Extrair primeira linha (onde está a estratégia)
        first_line = message_text.split('\n')[0].lower().strip()
        
        if self.config.get("debug", False):
            logger.info(f"🔍 Analisando primeira linha: '{first_line}'")
        
        # Lista de estratégias configuradas
        strategies = strategy_config.get("strategies", [])
        mode = strategy_config.get("mode", "whitelist")
        
        # Verificar se alguma estratégia está presente na primeira linha
        strategy_found = False
        matched_strategy = None
        
        for strategy in strategies:
            if strategy.lower() in first_line:
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
            status = "✅ APROVADA" if should_forward else "❌ BLOQUEADA"
            if matched_strategy:
                logger.info(f"🎯 Estratégia encontrada: '{matched_strategy}' - {status}")
            else:
                logger.info(f"🎯 Nenhuma estratégia reconhecida - {status}")
        
        return should_forward
    
    async def forward_message(self, client: Client, message: Message):
        """Encaminha uma mensagem para o grupo de destino"""
        try:
            # Log da mensagem recebida
            text_preview = (message.text[:50] + "...") if message.text and len(message.text) > 50 else (message.text or "[Mídia]")
            logger.info(f"📨 Nova mensagem do CornerProBot2: {text_preview}")
            
            # Verificar filtros de estratégia
            if not self.should_forward_message(message.text):
                logger.info("🚫 Mensagem bloqueada pelos filtros de estratégia")
                return
            
            # Formata a mensagem
            if message.text:
                formatted_message = f"{message.text}"
            else:
                formatted_message = "[Mensagem com mídia]"
            
            # Encaminha para o grupo de destino
            await client.send_message(
                chat_id=self.config["target_chat_id"],
                text=formatted_message
            )
            
            logger.info("✅ Mensagem encaminhada automaticamente para o grupo!")
            
        except Exception as e:
            logger.error(f"❌ Erro ao encaminhar mensagem: {e}")
    
    async def start(self):
        """Inicia o cliente e o monitoramento"""
        logger.info("🚀 Iniciando Message Forwarder Automático...")
        
        async with self.app:
            # Obtém informações do usuário
            me = await self.app.get_me()
            logger.info(f"👤 Logado como: {me.first_name} {me.last_name or ''} (@{me.username or 'sem_username'})")
            
            # Verifica se o usuário fonte existe
            try:
                # Primeiro tenta pelo username
                source_user = await self.app.get_users('@cornerpro2_bot')
                logger.info(f"🎯 Monitorando mensagens de: {source_user.first_name} (@{source_user.username})")
            except Exception:
                try:
                    # Se falhar, tenta pelo ID como chat
                    source_user = await self.app.get_chat(self.config["source_user_id"])
                    logger.info(f"🎯 Monitorando mensagens de: {source_user.first_name}")
                except Exception as e:
                    logger.error(f"❌ Erro ao verificar usuário fonte: {e}")
                    logger.error("💡 Certifique-se de ter conversado com @cornerpro2_bot pelo menos uma vez")
                    return
            
            # Verifica se o chat de destino existe
            try:
                target_chat = await self.app.get_chat(self.config["target_chat_id"])
                logger.info(f"📤 Encaminhando para: {target_chat.title}")
            except Exception as e:
                logger.error(f"❌ Erro ao verificar chat de destino: {e}")
                return
            
            logger.info("👂 Aguardando mensagens... (Pressione Ctrl+C para parar)")
            
            # Mantém o cliente rodando
            await asyncio.Event().wait()

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
