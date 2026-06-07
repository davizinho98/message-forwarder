#!/bin/bash
"""
🏆 GUIA COMPLETO: DEPLOY NO ORACLE CLOUD
========================================

Você está conectado via SSH na VM Ubuntu do Oracle Cloud.
Siga estes passos para configurar o Message Forwarder:
"""

echo "🏆 ORACLE CLOUD - SETUP DO MESSAGE FORWARDER"
echo "============================================="
echo ""

echo "📋 PASSOS PARA CONFIGURAÇÃO:"
echo "----------------------------"
echo "1. 📦 Baixar e configurar o projeto"
echo "2. 🐍 Instalar Python e dependências"
echo "3. ⚙️  Configurar credenciais via variáveis de ambiente"
echo "4. 🧪 Testar o sistema"
echo "5. 🚀 Configurar serviço automático"
echo ""

echo "🚀 INICIANDO CONFIGURAÇÃO..."
echo ""

# 1. Atualizar sistema
echo "📦 1. Atualizando sistema Ubuntu..."
sudo apt update && sudo apt upgrade -y

# 2. Instalar dependências
echo "🐍 2. Instalando Python e ferramentas..."
sudo apt install -y python3 python3-pip python3-venv git curl wget

# 3. Baixar projeto
echo "📁 3. Baixando projeto do GitHub..."
if [ -d "message-forwarder" ]; then
    echo "⚠️  Diretório já existe, atualizando..."
    cd message-forwarder
    git pull
else
    git clone https://github.com/davizinho98/message-forwarder.git
    cd message-forwarder
fi

# 4. Criar ambiente virtual
echo "🐍 4. Criando ambiente virtual Python..."
python3 -m venv venv
source venv/bin/activate

# 5. Instalar dependências Python
echo "📦 5. Instalando dependências Python..."
pip install -r requirements.txt

echo ""
echo "✅ CONFIGURAÇÃO BASE CONCLUÍDA!"
echo ""
echo "🎯 PRÓXIMOS PASSOS:"
echo "=================="
echo ""
echo "📝 1. CONFIGURAR VARIÁVEIS DE AMBIENTE:"
echo "   Execute no terminal da VM:"
echo ""
echo "   export API_ID=sua_api_id"
echo "   export API_HASH=sua_api_hash"
echo "   export PHONE_NUMBER=+5568999999999"
echo "   export SOURCE_USER_ID=779230055"
echo "   export TARGET_CHAT_ID=id_do_seu_grupo"
echo "   export DEBUG=true"
echo ""
echo "📝 2. CONFIGURAR FILTROS (OPCIONAL):"
echo "   export STRATEGY_FILTERS_ENABLED=true"
echo "   export STRATEGY_FILTERS_MODE=whitelist"
echo "   export STRATEGY_FILTERS_STRATEGIES=over,under,corner"
echo ""
echo "🧪 3. TESTAR O SISTEMA:"
echo "   source venv/bin/activate"
echo "   python3 forwarders/auto_forwarder.py"
echo ""
echo "🚀 4. CONFIGURAR SERVIÇO AUTOMÁTICO:"
echo "   ./configure_service.sh"
echo ""
echo "💡 DICAS:"
echo "   • Use 'screen' para manter rodando: screen -S forwarder"
echo "   • Para logs: tail -f ~/.local/share/message-forwarder/logs"
echo "   • Para parar: Ctrl+C no terminal ou systemctl stop message-forwarder"
echo ""
