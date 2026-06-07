#!/bin/bash
# Script de instalação do Daily Matchday Fetcher

echo "🚀 Instalando Daily Matchday Fetcher..."
echo ""

# Verificar se está no diretório correto
if [ ! -f "tools/daily_matchday_fetcher.py" ]; then
    echo "❌ Erro: Execute este script no diretório do projeto"
    exit 1
fi

# Ativar ambiente virtual se existir
if [ -d "venv" ]; then
    echo "📦 Ativando ambiente virtual..."
    source venv/bin/activate
else
    echo "⚠️  Ambiente virtual não encontrado. Criando..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Instalar dependências
echo "📦 Instalando dependências..."
pip install -q --upgrade pip
pip install -q requests schedule pytz

# Tornar script executável
echo "🔧 Configurando permissões..."
chmod +x tools/daily_matchday_fetcher.py

# Criar diretório de dados
echo "📁 Criando diretório de dados..."
mkdir -p matchday_data

echo ""
echo "✅ Instalação concluída!"
echo ""
echo "📋 Opções de execução:"
echo ""
echo "1️⃣  Executar manualmente:"
echo "   python tools/daily_matchday_fetcher.py"
echo ""
echo "2️⃣  Executar como serviço systemd (recomendado para servidor):"
echo "   sudo cp matchday-fetcher.service /etc/systemd/system/"
echo "   sudo systemctl daemon-reload"
echo "   sudo systemctl enable matchday-fetcher"
echo "   sudo systemctl start matchday-fetcher"
echo "   sudo systemctl status matchday-fetcher"
echo ""
echo "3️⃣  Executar em background com nohup:"
echo "   nohup python tools/daily_matchday_fetcher.py > matchday_fetcher.log 2>&1 &"
echo ""
echo "📊 Ver logs (se usando systemd):"
echo "   sudo journalctl -u matchday-fetcher -f"
echo ""
