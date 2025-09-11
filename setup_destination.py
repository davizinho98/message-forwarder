#!/usr/bin/env python3
"""
Script alternativo para criar grupo usando método mais simples
"""

import asyncio
import json
from pyrogram import Client
from pyrogram.enums import ChatType

async def create_simple_group():
    """Cria grupo de forma mais direta"""
    
    with open('client_config.json', 'r') as f:
        config = json.load(f)
    
    app = Client('message_forwarder_main', api_id=config['api_id'], api_hash=config['api_hash'], phone_number=config['phone_number'])
    
    async with app:
        me = await app.get_me()
        print(f"👤 Usuário: {me.first_name} (@{me.username})")
        print()
        
        # Opções de destino
        print("📋 Opções de destino para as mensagens:")
        print("1. 💾 Mensagens Salvas (atual) - Privado, sempre funciona")
        print("2. 📱 Criar novo grupo")
        print("3. 📺 Criar novo canal")
        print("4. 🔍 Escolher grupo/canal existente")
        print()
        
        choice = input("Escolha uma opção (1-4): ").strip()
        
        if choice == "1":
            print("✅ Usando Mensagens Salvas (configuração atual)")
            return
            
        elif choice == "2":
            # Criar grupo
            group_name = input("Nome do grupo: ").strip() or "🤖 CornerPro Messages"
            try:
                # Método alternativo de criação
                new_group = await app.create_group(group_name, [me.id])
                print(f"✅ Grupo criado: {new_group.title} (ID: {new_group.id})")
                
                # Atualizar config
                config['target_chat_id'] = new_group.id
                with open('client_config.json', 'w') as f:
                    json.dump(config, f, indent=2)
                
                await app.send_message(new_group.id, "🎉 Grupo configurado para receber mensagens do CornerProBot2!")
                print("✅ Configuração atualizada!")
                
            except Exception as e:
                print(f"❌ Erro ao criar grupo: {e}")
                
        elif choice == "3":
            # Criar canal
            channel_name = input("Nome do canal: ").strip() or "🤖 CornerPro AutoForwarder"
            try:
                new_channel = await app.create_channel(channel_name)
                print(f"✅ Canal criado: {new_channel.title} (ID: {new_channel.id})")
                
                # Atualizar config
                config['target_chat_id'] = new_channel.id
                with open('client_config.json', 'w') as f:
                    json.dump(config, f, indent=2)
                
                await app.send_message(new_channel.id, "🎉 Canal configurado para receber mensagens do CornerProBot2!")
                print("✅ Configuração atualizada!")
                
            except Exception as e:
                print(f"❌ Erro ao criar canal: {e}")
                
        elif choice == "4":
            # Listar chats existentes
            print("📋 Grupos/canais disponíveis:")
            chats = []
            
            async for dialog in app.get_dialogs(limit=30):
                if dialog.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL]:
                    chats.append(dialog.chat)
            
            for i, chat in enumerate(chats[:10], 1):
                print(f"{i:2d}. {chat.title} (ID: {chat.id})")
            
            if chats:
                try:
                    idx = int(input("\\nEscolha o número do chat: ")) - 1
                    if 0 <= idx < len(chats):
                        chosen_chat = chats[idx]
                        config['target_chat_id'] = chosen_chat.id
                        
                        with open('client_config.json', 'w') as f:
                            json.dump(config, f, indent=2)
                        
                        print(f"✅ Configurado para: {chosen_chat.title}")
                    else:
                        print("❌ Número inválido")
                except ValueError:
                    print("❌ Entrada inválida")
            else:
                print("❌ Nenhum grupo/canal encontrado")

if __name__ == "__main__":
    asyncio.run(create_simple_group())
