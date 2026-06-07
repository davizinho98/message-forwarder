#!/bin/bash

echo "🏆 ORACLE CLOUD - MESSAGE FORWARDER SETUP"
echo "========================================"
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir com cor
print_color() {
    printf "${2}${1}${NC}\n"
}

print_color "📋 Este script irá configurar o Message Forwarder na sua VM Oracle Cloud" "$BLUE"
echo ""

# 1. Atualizar sistema
print_color "📦 Atualizando sistema Ubuntu..." "$YELLOW"
sudo apt update -y

# 2. Instalar dependências básicas
print_color "🛠️  Instalando dependências..." "$YELLOW"
sudo apt install -y python3 python3-pip python3-venv git curl wget screen

# 3. Clonar repositório
print_color "📁 Baixando projeto..." "$YELLOW"
if [ -d "message-forwarder" ]; then
    print_color "⚠️  Diretório já existe, atualizando..." "$YELLOW"
    cd message-forwarder
    git pull
else
    git clone https://github.com/davizinho98/message-forwarder.git
    cd message-forwarder
fi

# 4. Configurar ambiente Python
print_color "🐍 Configurando ambiente Python..." "$YELLOW"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Tornar scripts executáveis
chmod +x *.sh
chmod +x *.py

print_color "✅ INSTALAÇÃO CONCLUÍDA!" "$GREEN"
echo ""
print_color "🎯 AGORA VOCÊ PRECISA CONFIGURAR AS CREDENCIAIS" "$BLUE"
echo ""
echo "Execute os comandos abaixo substituindo pelos seus dados:"
echo ""
print_color "export API_ID=28238305" "$YELLOW"
print_color "export API_HASH=4d2305b78a6921ee43145cccf2ea2477" "$YELLOW"
print_color "export PHONE_NUMBER=+5568999941197" "$YELLOW"
print_color "export SOURCE_USER_ID=779230055" "$YELLOW"
print_color "export TARGET_CHAT_ID=-4197130508" "$YELLOW"
print_color "export DEBUG=true" "$YELLOW"
echo ""
print_color "🎯 PARA CONFIGURAR FILTROS (OPCIONAL):" "$BLUE"
print_color "export STRATEGY_FILTERS_ENABLED=true" "$YELLOW"
print_color "export STRATEGY_FILTERS_MODE=whitelist" "$YELLOW"
print_color "export STRATEGY_FILTERS_STRATEGIES=over,under,corner" "$YELLOW"
echo ""
print_color "🧪 APÓS CONFIGURAR, TESTE COM:" "$BLUE"
print_color "source venv/bin/activate" "$YELLOW"
print_color "python3 forwarders/auto_forwarder.py" "$YELLOW"
echo ""
print_color "🚀 PARA CONFIGURAR SERVIÇO AUTOMÁTICO:" "$BLUE"
print_color "./configure_service.sh" "$YELLOW"
echo ""
print_color "💡 DICA: Use 'screen' para manter rodando em background:" "$BLUE"
print_color "screen -S forwarder" "$YELLOW"
print_color "python3 forwarders/auto_forwarder.py" "$YELLOW"
print_color "# Pressione Ctrl+A depois D para desanexar" "$YELLOW"
print_color "# Para reconectar: screen -r forwarder" "$YELLOW"
