#!/usr/bin/env python3
"""
Teste específico para entender diferenças de acesso
"""

import asyncio
import json
from pyrogram import Client
from pyrogram.enums import ChatType

async def test_access_methods():
    """Testa diferentes métodos de acesso ao mesmo grupo"""
    
    with open('client_config.json', 'r') as f:
        config = json.load(f)
    
    # Usar a mesma sessão
    app = Client('message_forwarder_main', api_id=config['api_id'], api_hash=config['api_hash'], phone_number=config['phone_number'])
    
    async with app:
        target_id = -4197130508  # Grupo A
        
        print(f"🧪 Testando acesso ao grupo A (ID: {target_id})")
        print()
        
        # Método 1: get_chat direto
        print("1️⃣ Método get_chat() direto:")
        try:
            chat = await app.get_chat(target_id)
            print(f"   ✅ Sucesso: {chat.title}")
        except Exception as e:
            print(f"   ❌ Erro: {type(e).__name__}: {e}")
        
        # Método 2: Buscar nos diálogos primeiro
        print("\\n2️⃣ Método via get_dialogs():")
        found = False
        try:
            async for dialog in app.get_dialogs():
                if dialog.chat.id == target_id:
                    print(f"   ✅ Encontrado nos diálogos: {dialog.chat.title}")
                    found = True
                    
                    # Agora tentar get_chat
                    try:
                        chat = await app.get_chat(target_id)
                        print(f"   ✅ get_chat após dialogs: OK")
                    except Exception as e:
                        print(f"   ❌ get_chat falhou: {e}")
                    break
                    
            if not found:
                print(f"   ❌ Não encontrado nos diálogos")
        except Exception as e:
            print(f"   ❌ Erro nos diálogos: {e}")
        
        # Método 3: Testar send_message direto
        print("\\n3️⃣ Método send_message() direto:")
        try:
            await app.send_message(target_id, "🧪 Teste de acesso direto")
            print(f"   ✅ Envio direto: OK")
        except Exception as e:
            print(f"   ❌ Envio falhou: {type(e).__name__}: {e}")
            
        # Método 4: Tentar com get_users se for private
        print("\\n4️⃣ Método get_users() (se for user):")
        try:
            if target_id > 0:  # ID positivo = usuário
                user = await app.get_users(target_id)
                print(f"   ✅ Usuário: {user.first_name}")
            else:
                print(f"   ℹ️  ID negativo - é grupo/canal")
        except Exception as e:
            print(f"   ❌ Erro: {e}")

if __name__ == "__main__":
    asyncio.run(test_access_methods())
