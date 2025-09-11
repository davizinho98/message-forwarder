#!/usr/bin/env python3
"""
Script de inicialização e verificação do Message Forwarder
"""

import asyncio
import json
import sys
from pyrogram import Client
from pyrogram.errors import PeerIdInvalid
from pyrogram.enums import ChatType

async def initialize_forwarder():
    """Inicializa e verifica todas as conexões"""
    
    print("🚀 Inicializando Message Forwarder...")
    print()
    
    # Carregar configuração
    try:
        with open('client_config.json', 'r') as f:
            config = json.load(f)
        print("✅ Configuração carregada")
    except FileNotFoundError:
        print("❌ Arquivo client_config.json não encontrado!")
        print("💡 Execute: cp client_config.example.json client_config.json")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Erro no arquivo JSON: {e}")
        return False

    # Criar cliente
    app = Client(
        'message_forwarder_main',
        api_id=config['api_id'],
        api_hash=config['api_hash'],
        phone_number=config['phone_number']
    )
    
    async with app:
        print("✅ Conectado ao Telegram")
        
        # Verificar conta
        me = await app.get_me()
        print(f"👤 Logado como: {me.first_name} (@{me.username})")
        print()
        
        # Verificar bot fonte
        print("🔍 Verificando bot fonte...")
        try:
            # Tentar pelo username primeiro
            source_user = await app.get_users('@cornerpro2_bot')
            print(f"✅ Bot encontrado: {source_user.first_name} (@{source_user.username})")
            print(f"   ID: {source_user.id}")
            
            # Atualizar config se necessário
            if config['source_user_id'] != source_user.id:
                print(f"🔄 Atualizando ID no config: {config['source_user_id']} → {source_user.id}")
                config['source_user_id'] = source_user.id
                
        except Exception as e:
            print(f"⚠️  Erro ao buscar por username: {e}")
            print("💡 Tentando usar ID direto...")
            try:
                source_user = await app.get_chat(config['source_user_id'])
                print(f"✅ Bot encontrado por ID: {source_user.first_name}")
            except Exception as e2:
                print(f"❌ Não foi possível encontrar o bot: {e2}")
                print("💡 Certifique-se de ter conversado com @cornerpro2_bot pelo menos uma vez")
                return False
        
        # Verificar grupo destino
        print()
        print("🔍 Verificando grupo de destino...")
        try:
            # Primeiro buscar nos diálogos (para carregar cache)
            target_found = False
            async for dialog in app.get_dialogs():
                if dialog.chat.id == config['target_chat_id']:
                    target_found = True
                    print(f"✅ Encontrado nos diálogos: {dialog.chat.title}")
                    break
            
            if target_found:
                # Agora tentar acesso direto
                target_chat = await app.get_chat(config['target_chat_id'])
                print(f"✅ Grupo encontrado: {target_chat.title}")
                print(f"   ID: {target_chat.id}")
                print(f"   Tipo: {target_chat.type}")
            else:
                print(f"❌ Grupo não encontrado nos diálogos")
                print(f"💡 Tentando acesso direto mesmo assim...")
                target_chat = await app.get_chat(config['target_chat_id'])
                print(f"✅ Acesso direto funcionou: {target_chat.title}")
                
        except Exception as e:
            print(f"❌ Erro ao acessar grupo: {e}")
            print("💡 Verifique se você é membro do grupo e se o ID está correto")
            return False
        
        # Verificar histórico recente do bot
        print()
        print("📜 Verificando mensagens recentes...")
        try:
            message_count = 0
            async for message in app.get_chat_history(source_user.id, limit=5):
                if message_count == 0:
                    print(f"✅ Última mensagem: {message.date}")
                message_count += 1
            
            if message_count == 0:
                print("⚠️  Nenhuma mensagem encontrada")
                print("💡 Envie /start para @cornerpro2_bot primeiro")
            else:
                print(f"✅ Encontradas {message_count} mensagens recentes")
                
        except Exception as e:
            print(f"⚠️  Erro ao verificar histórico: {e}")
        
        # Salvar configuração atualizada
        with open('client_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print()
        print("🎯 Verificação concluída!")
        print()
        print("📋 Próximos passos:")
        print("   1. Se não há mensagens recentes, envie /start para @cornerpro2_bot")
        print("   2. Execute: python auto_forwarder.py")
        print("   3. O sistema ficará monitorando automaticamente")
        
        return True

if __name__ == "__main__":
    success = asyncio.run(initialize_forwarder())
    if not success:
        sys.exit(1)
