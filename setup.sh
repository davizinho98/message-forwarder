#!/bin/bash

echo "🚀 Configurando Message Forwarder Automático (Python)..."

# Verifica se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Instalando..."
    sudo apt update && sudo apt install -y python3 python3-pip
fi

# Verifica se pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 não encontrado. Instalando..."
    sudo apt install -y python3-pip
fi

echo "📦 Instalando pyrogram..."
pip3 install pyrogram

echo "✅ Dependências instaladas com sucesso!"
echo ""
echo "🎯 Configuração automática do Message Forwarder:"
echo ""
echo "📋 Próximos passos:"
echo "1. Obtenha suas credenciais da API do Telegram:"
echo "   🌐 Vá para: https://my.telegram.org"
echo "   📱 Faça login com seu número de telefone"
echo "   ⚙️  Vá em 'API development tools'"
echo "   🆕 Crie um novo app e anote API_ID e API_HASH"
echo ""
echo "2. Configure o arquivo de configuração:"
echo "   📁 cp client_config.example.json client_config.json"
echo "   ✏️  # Edite client_config.json com suas informações"
echo ""
echo "3. Execute o forwarder automático:"
echo "   🐍 python3 forwarders/auto_forwarder.py"
echo ""
echo "🎯 Lembre-se das configurações:"
echo "   📱 phone_number: Seu número no formato internacional (+5511999999999)"
echo "   🤖 source_user_id: 779230055 (CornerProBot2)"
echo "   👥 target_chat_id: -4197130508 (seu grupo)"
echo ""
echo "🔥 Este sistema irá monitorar AUTOMATICAMENTE as mensagens"
echo "   do CornerProBot2 e encaminhar para seu grupo em tempo real!"
