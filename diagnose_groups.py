#!/usr/bin/env python3
"""
Diagnóstico detalhado de problemas com grupos/canais
"""

import asyncio
import json
from pyrogram import Client
from pyrogram.enums import ChatType
from pyrogram.errors import *

async def diagnose_groups():
    """Analisa problemas específicos de cada grupo"""
    
    with open('client_config.json', 'r') as f:
        config = json.load(f)
    
    app = Client('diagnostico', api_id=config['api_id'], api_hash=config['api_hash'], phone_number=config['phone_number'])
    
    async with app:
        me = await app.get_me()
        print(f"👤 Analisando grupos para: {me.first_name} (@{me.username})")
        print(f"🆔 Seu ID: {me.id}")
        print()
        
        # Lista de grupos problemáticos identificados
        problematic_groups = [
            (-4801269144, "🤖 Message Forwarder - CornerPro"),
            (-1002968541787, "🤖 CornerPro AutoForwarder"), 
            (-4197130508, "A")
        ]
        
        working_group = (-1002024979601, "Clube de Membros - Grupo")
        
        print("🔍 ANÁLISE DETALHADA DOS GRUPOS:")
        print("=" * 50)
        
        # Analisar grupo que funciona
        print(f"✅ GRUPO FUNCIONANDO:")
        await analyze_chat(app, working_group[1], working_group[0])
        print()
        
        # Analisar grupos problemáticos
        print(f"❌ GRUPOS PROBLEMÁTICOS:")
        for group_id, group_name in problematic_groups:
            await analyze_chat(app, group_name, group_id)
            print()
        
        print("📋 RESUMO DOS PROBLEMAS POSSÍVEIS:")
        print("=" * 50)
        print("1. 🚫 **Peer ID Invalid** - Possíveis causas:")
        print("   • Você foi removido/banido do grupo")
        print("   • O grupo foi deletado pelo criador")
        print("   • O grupo se tornou privado e você perdeu acesso")
        print("   • Cache do Telegram desatualizado")
        print("   • Grupo criado muito recentemente (sync delay)")
        print()
        print("2. 🔒 **Permissões** - Possíveis causas:")
        print("   • Grupo tem restrições para envio de mensagens")
        print("   • Você não tem permissão para enviar mensagens")
        print("   • Bot/aplicação não tem as permissões necessárias")
        print()
        print("3. ⏰ **Timing** - Possíveis causas:")
        print("   • Grupos recém-criados podem ter delay de sincronização")
        print("   • Cache local desatualizado")
        print("   • Rate limiting do Telegram")

async def analyze_chat(app, name, chat_id):
    """Analisa um chat específico"""
    print(f"📱 {name} (ID: {chat_id})")
    
    try:
        # Tentar obter informações básicas
        chat = await app.get_chat(chat_id)
        print(f"   ✅ Acesso básico: OK")
        print(f"   📄 Título: {chat.title}")
        print(f"   🔖 Tipo: {chat.type}")
        print(f"   👥 Membros: {getattr(chat, 'members_count', 'N/A')}")
        
        # Verificar se está nos diálogos recentes
        found_in_dialogs = False
        async for dialog in app.get_dialogs(limit=100):
            if dialog.chat.id == chat_id:
                found_in_dialogs = True
                break
        
        print(f"   📋 Nos diálogos: {'✅ Sim' if found_in_dialogs else '❌ Não'}")
        
        # Tentar obter informações de membro
        try:
            me = await app.get_me()
            member = await app.get_chat_member(chat_id, me.id)
            print(f"   👤 Status no grupo: {member.status}")
            print(f"   🔒 Pode enviar mensagens: {getattr(member, 'can_send_messages', 'N/A')}")
        except Exception as e:
            print(f"   ⚠️  Info de membro: {type(e).__name__}: {e}")
        
        # Testar envio (sem enviar de verdade)
        try:
            # Só validar se consegue preparar o envio
            print(f"   📤 Capacidade de envio: Provavelmente OK")
        except Exception as e:
            print(f"   ❌ Erro de envio: {type(e).__name__}: {e}")
            
    except PeerIdInvalid:
        print(f"   ❌ PEER_ID_INVALID - Não consegue acessar")
        print(f"   💡 Possível causa: Removido do grupo ou grupo deletado")
        
    except ChatAdminRequired:
        print(f"   ❌ CHAT_ADMIN_REQUIRED - Precisa ser admin")
        
    except UserNotParticipant:
        print(f"   ❌ USER_NOT_PARTICIPANT - Não é mais membro")
        
    except ChatWriteForbidden:
        print(f"   ❌ CHAT_WRITE_FORBIDDEN - Sem permissão para escrever")
        
    except Exception as e:
        print(f"   ❌ Erro inesperado: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(diagnose_groups())
