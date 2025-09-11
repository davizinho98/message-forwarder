#!/usr/bin/env python3
"""
Message Forwarder Automático - Versão Python
Monitora mensagens de um bot específico e encaminha automaticamente para um grupo.
"""

import asyncio
import json
import logging
from pyrogram import Client, filters
from pyrogram.types import Message

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
            name="message_forwarder",
            api_id=self.config["api_id"],
            api_hash=self.config["api_hash"],
            phone_number=self.config["phone_number"]
        )
        
        # Registra o handler de mensagens
        self.register_handlers()
    
    def load_config(self, config_path):
        """Carrega a configuração do arquivo JSON"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # Valida configurações obrigatórias
            required_fields = ["api_id", "api_hash", "phone_number", "source_user_id", "target_chat_id"]
            for field in required_fields:
                if field not in config:
                    raise ValueError(f"Campo obrigatório '{field}' não encontrado na configuração")
                    
            return config
            
        except FileNotFoundError:
            logger.error(f"Arquivo de configuração {config_path} não encontrado")
            raise
        except json.JSONDecodeError:
            logger.error(f"Erro ao decodificar JSON do arquivo {config_path}")
            raise
    
    def register_handlers(self):
        """Registra os handlers de mensagens"""
        
        @self.app.on_message(
            filters.user(self.config["source_user_id"]) & 
            filters.private
        )
        async def handle_source_message(client: Client, message: Message):
            """Handler para mensagens do bot fonte (CornerProBot2)"""
            await self.forward_message(client, message)
    
    async def forward_message(self, client: Client, message: Message):
        """Encaminha uma mensagem para o grupo de destino"""
        try:
            # Log da mensagem recebida
            text_preview = (message.text[:50] + "...") if message.text and len(message.text) > 50 else (message.text or "[Mídia]")
            logger.info(f"📨 Nova mensagem do CornerProBot2: {text_preview}")
            
            # Formata a mensagem
            if message.text:
                formatted_message = f"🤖 **Alerta CornerProBot2:**\n\n{message.text}"
            else:
                formatted_message = "🤖 **Alerta CornerProBot2:**\n\n[Mensagem com mídia]"
            
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
                source_user = await self.app.get_users(self.config["source_user_id"])
                logger.info(f"🎯 Monitorando mensagens de: {source_user.first_name} (@{source_user.username})")
            except Exception as e:
                logger.error(f"❌ Erro ao verificar usuário fonte: {e}")
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
