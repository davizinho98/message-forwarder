#!/bin/bash

echo "🚀 Configurando Message Forwarder Automático..."

# Verifica se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Instale o Python3 primeiro."
    exit 1
fi

# Verifica se pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 não encontrado. Instale o pip3 primeiro."
    exit 1
fi

echo "📦 Instalando pyrogram..."
pip3 install pyrogram

echo "✅ Dependências instaladas com sucesso!"
echo ""
echo "📋 Próximos passos:"
echo "1. Obtenha suas credenciais da API do Telegram:"
echo "   - Vá para https://my.telegram.org"
echo "   - Faça login com seu número de telefone"
echo "   - Vá em 'API development tools'"
echo "   - Crie um novo app e anote API_ID e API_HASH"
echo ""
echo "2. Configure o arquivo client_config.json:"
echo "   cp client_config.example.json client_config.json"
echo "   # Edite client_config.json com suas informações"
echo ""
echo "3. Execute o forwarder:"
echo "   python3 auto_forwarder.py"
echo ""
echo "🎯 Lembre-se:"
echo "   - source_user_id: 779230055 (CornerProBot2)"
echo "   - target_chat_id: -4197130508 (seu grupo)"
echo "   - Use seu número de telefone no formato internacional (+5511999999999)"
