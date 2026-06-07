#!/bin/bash

echo "🚀 CONFIGURANDO SERVIÇO AUTOMÁTICO NO ORACLE CLOUD"
echo "================================================="
echo ""

# Verificar se está no diretório correto
if [ ! -f "forwarders/auto_forwarder.py" ]; then
    echo "❌ Execute este script no diretório do message-forwarder"
    exit 1
fi

# Verificar variáveis de ambiente
if [ -z "$API_ID" ] || [ -z "$API_HASH" ] || [ -z "$PHONE_NUMBER" ] || [ -z "$TARGET_CHAT_ID" ]; then
    echo "❌ Variáveis de ambiente não configuradas!"
    echo ""
    echo "Configure primeiro:"
    echo "export API_ID=sua_api_id"
    echo "export API_HASH=sua_api_hash"
    echo "export PHONE_NUMBER=+5568999999999"
    echo "export TARGET_CHAT_ID=id_do_grupo"
    exit 1
fi

echo "✅ Variáveis de ambiente detectadas"
echo ""

# Criar arquivo de serviço systemd
echo "📄 Criando serviço systemd..."

# Obter paths absolutos
PROJECT_DIR=$(pwd)
PYTHON_PATH="$PROJECT_DIR/venv/bin/python"
USER=$(whoami)

# Criar arquivo de ambiente
cat > message-forwarder.env << EOF
API_ID=$API_ID
API_HASH=$API_HASH
PHONE_NUMBER=$PHONE_NUMBER
SOURCE_USER_ID=${SOURCE_USER_ID:-779230055}
TARGET_CHAT_ID=$TARGET_CHAT_ID
DEBUG=${DEBUG:-true}
STRATEGY_FILTERS_ENABLED=${STRATEGY_FILTERS_ENABLED:-false}
STRATEGY_FILTERS_MODE=${STRATEGY_FILTERS_MODE:-whitelist}
STRATEGY_FILTERS_STRATEGIES=${STRATEGY_FILTERS_STRATEGIES:-}
EOF

echo "✅ Arquivo de ambiente criado: message-forwarder.env"

# Criar arquivo de serviço
sudo tee /etc/systemd/system/message-forwarder.service > /dev/null << EOF
[Unit]
Description=Message Forwarder Automático
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment=PYTHONPATH=$PROJECT_DIR
EnvironmentFile=$PROJECT_DIR/message-forwarder.env
ExecStart=$PYTHON_PATH forwarders/auto_forwarder.py
Restart=always
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=message-forwarder

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Serviço systemd criado: /etc/systemd/system/message-forwarder.service"

# Recarregar systemd e habilitar serviço
echo "🔄 Configurando serviço..."
sudo systemctl daemon-reload
sudo systemctl enable message-forwarder

echo ""
echo "✅ SERVIÇO CONFIGURADO COM SUCESSO!"
echo ""
echo "🎮 COMANDOS ÚTEIS:"
echo "=================="
echo ""
echo "▶️  Iniciar serviço:"
echo "   sudo systemctl start message-forwarder"
echo ""
echo "⏹️  Parar serviço:"
echo "   sudo systemctl stop message-forwarder"
echo ""
echo "🔄 Reiniciar serviço:"
echo "   sudo systemctl restart message-forwarder"
echo ""
echo "📊 Ver status:"
echo "   sudo systemctl status message-forwarder"
echo ""
echo "📋 Ver logs em tempo real:"
echo "   sudo journalctl -u message-forwarder -f"
echo ""
echo "📜 Ver logs das últimas 50 linhas:"
echo "   sudo journalctl -u message-forwarder -n 50"
echo ""
echo "🚀 PARA INICIAR AGORA:"
echo "   sudo systemctl start message-forwarder"
echo ""
echo "💡 O serviço irá iniciar automaticamente quando a VM reiniciar"
