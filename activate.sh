#!/bin/bash

# 🚀 Script de ativação rápida do Message Forwarder
# Use: ./activate.sh

echo "🔧 Ativando ambiente virtual..."

# Verificar se venv existe
if [ ! -d "venv" ]; then
    echo "❌ Ambiente virtual não encontrado!"
    echo "🚀 Execute primeiro: ./setup_venv.sh"
    exit 1
fi

# Ativar ambiente virtual
source venv/bin/activate

echo "✅ Ambiente virtual ativado!"
echo ""
echo "📋 Comandos disponíveis:"
echo "   python forwarders/auto_forwarder.py    # Executar o forwarder"
echo "   deactivate                  # Desativar ambiente virtual"
echo ""

# Verificar se config existe
if [ ! -f "client_config.json" ]; then
    echo "⚠️  Arquivo client_config.json não encontrado!"
    echo "📝 Execute: cp client_config.example.json client_config.json"
    echo "   E configure suas credenciais do Telegram"
    echo ""
fi

# Manter shell ativo com ambiente virtual
exec bash
