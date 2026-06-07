#!/bin/bash

# 🚀 Script para configurar Message Forwarder no Oracle Cloud Always Free

echo "🐧 Configurando Message Forwarder no Oracle Cloud..."

# Atualizar sistema
echo "📦 Atualizando sistema..."
sudo apt update && sudo apt upgrade -y

# Instalar dependências
echo "🐍 Instalando Python e dependências..."
sudo apt install -y python3 python3-pip python3-venv git curl

# Clonar repositório
echo "📥 Clonando repositório..."
cd ~
git clone https://github.com/SEU_USUARIO/message-forwarder.git
cd message-forwarder

# Configurar ambiente virtual
echo "🔧 Configurando ambiente virtual..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configurar arquivo de configuração
echo "⚙️ Configurando credenciais..."
cp client_config.example.json client_config.json

echo "📝 IMPORTANTE: Edite o arquivo client_config.json com suas credenciais:"
echo "   nano client_config.json"
echo ""
echo "🔑 Você precisa configurar:"
echo "   - api_id (obtido em https://my.telegram.org)"
echo "   - api_hash (obtido em https://my.telegram.org)"
echo "   - phone_number (seu número com código do país)"
echo ""

# Criar script de inicialização
cat > start_forwarder.sh << 'EOF'
#!/bin/bash
cd ~/message-forwarder
source venv/bin/activate
python forwarders/auto_forwarder.py
EOF

chmod +x start_forwarder.sh

# Criar service do systemd para rodar automaticamente
echo "🔄 Criando serviço do sistema..."
sudo tee /etc/systemd/system/message-forwarder.service > /dev/null << EOF
[Unit]
Description=Message Forwarder Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/message-forwarder
ExecStart=/home/$USER/message-forwarder/venv/bin/python forwarders/auto_forwarder.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Setup concluído!"
echo ""
echo "📋 Próximos passos:"
echo "1. Configure suas credenciais:"
echo "   nano client_config.json"
echo ""
echo "2. Teste manualmente:"
echo "   cd ~/message-forwarder"
echo "   source venv/bin/activate"
echo "   python forwarders/auto_forwarder.py"
echo ""
echo "3. Para rodar automaticamente (após testar):"
echo "   sudo systemctl enable message-forwarder"
echo "   sudo systemctl start message-forwarder"
echo ""
echo "4. Ver logs do serviço:"
echo "   sudo journalctl -u message-forwarder -f"
