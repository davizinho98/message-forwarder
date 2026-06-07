#!/bin/bash

# 🐍 Setup do Ambiente Virtual Python para Message Forwarder
# Este script configura um ambiente virtual Python e instala todas as dependências

echo "🚀 Configurando ambiente virtual Python para Message Forwarder..."

# Verificar se Python3 está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Instale o Python3 primeiro:"
    echo "   sudo apt update && sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

# Verificar se pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 não encontrado. Instalando..."
    sudo apt install python3-pip
fi

# Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
    echo "✅ Ambiente virtual criado!"
else
    echo "✅ Ambiente virtual já existe!"
fi

# Ativar ambiente virtual
echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

# Atualizar pip
echo "📦 Atualizando pip..."
pip install --upgrade pip

# Instalar dependências
echo "📦 Instalando dependências do projeto..."
pip install -r requirements.txt

echo ""
echo "🎉 Setup concluído com sucesso!"
echo ""
echo "📋 Para usar o projeto:"
echo "   1. Ative o ambiente virtual:"
echo "      source venv/bin/activate"
echo ""
echo "   2. Configure suas credenciais:"
echo "      cp client_config.example.json client_config.json"
echo "      # Edite client_config.json com suas credenciais"
echo ""
echo "   3. Execute o forwarder:"
echo "      python forwarders/auto_forwarder.py"
echo ""
echo "💡 Para desativar o ambiente virtual:"
echo "   deactivate"
echo ""
echo "🔄 Para reativar depois:"
echo "   source venv/bin/activate"
