#!/usr/bin/env python3
"""
Script para criar um novo grupo para receber mensagens do Message Forwarder
"""

import asyncio
import json
import sys
from pyrogram import Client
from pyrogram.types import Chat
from pyrogram.enums import ChatType

async def create_new_group():
    """Cria um novo grupo para o Message Forwarder"""
    
    print("🚀 Criando novo grupo para Message Forwarder...")
    print()
    
    # Carregar configuração
    try:
        with open('client_config.json', 'r') as f:
            config = json.load(f)
        print("✅ Configuração carregada")
    except FileNotFoundError:
        print("❌ Arquivo client_config.json não encontrado!")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Erro no arquivo JSON: {e}")
        return False

    # Criar cliente
    app = Client(
        'group_creator',
        api_id=config['api_id'],
        api_hash=config['api_hash'],
        phone_number=config['phone_number']
    )
    
    async with app:
        print("✅ Conectado ao Telegram")
        
        # Informações do usuário
        me = await app.get_me()
        print(f"👤 Logado como: {me.first_name} (@{me.username})")
        print()
        
        # Criar o grupo
        try:
            group_name = "🤖 Message Forwarder - CornerPro"
            group_description = "Grupo automático para receber mensagens do CornerProBot2"
            
            print(f"📱 Criando grupo: {group_name}")
            
            # Criar grupo básico
            new_group = await app.create_group(
                title=group_name,
                users=[me.id]  # Apenas você no grupo inicialmente
            )
            
            print(f"✅ Grupo criado com sucesso!")
            print(f"   ID: {new_group.id}")
            print(f"   Título: {new_group.title}")
            print(f"   Tipo: {new_group.type}")
            print()
            
            # Atualizar configuração
            config['target_chat_id'] = new_group.id
            
            with open('client_config.json', 'w') as f:
                json.dump(config, f, indent=2)
            
            print("✅ Configuração atualizada!")
            print(f"   Novo target_chat_id: {new_group.id}")
            print()
            
            # Enviar mensagem de boas-vindas
            welcome_message = f"""🎉 **Grupo Message Forwarder Criado!**

🤖 Este grupo foi criado automaticamente para receber mensagens do **CornerProBot2**.

⚙️ **Configuração:**
• **Bot fonte**: CornerProBot2 (@cornerpro2_bot)
• **ID do grupo**: `{new_group.id}`
• **Monitoramento**: Automático 24/7

🚀 **Para ativar:**
```bash
python auto_forwarder.py
```

✅ **Todas as mensagens do CornerProBot2 aparecerão aqui automaticamente!**"""
            
            await app.send_message(new_group.id, welcome_message)
            print("✅ Mensagem de boas-vindas enviada!")
            print()
            
            print("🎯 **Próximos passos:**")
            print("   1. Execute: python auto_forwarder.py")
            print("   2. Envie uma mensagem para @cornerpro2_bot para testar")
            print("   3. A mensagem deve aparecer neste grupo automaticamente!")
            print()
            print(f"📱 **Link do grupo**: https://t.me/c/{str(new_group.id)[4:]}/1")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar grupo: {e}")
            
            # Tentar criar supergrupo se grupo normal falhar
            print("🔄 Tentando criar como canal/supergrupo...")
            try:
                new_channel = await app.create_channel(
                    title=group_name,
                    description=group_description
                )
                
                print(f"✅ Canal criado com sucesso!")
                print(f"   ID: {new_channel.id}")
                print(f"   Título: {new_channel.title}")
                print(f"   Tipo: {new_channel.type}")
                
                # Atualizar configuração
                config['target_chat_id'] = new_channel.id
                
                with open('client_config.json', 'w') as f:
                    json.dump(config, f, indent=2)
                
                print("✅ Configuração atualizada com canal!")
                return True
                
            except Exception as e2:
                print(f"❌ Erro ao criar canal: {e2}")
                return False

if __name__ == "__main__":
    success = asyncio.run(create_new_group())
    if not success:
        sys.exit(1)
