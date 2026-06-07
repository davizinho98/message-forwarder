#!/bin/bash

# 📱 Script para configurar Message Forwarder no Termux (Android)

echo "📱 Configurando Message Forwarder no Termux..."

# Atualizar Termux
echo "📦 Atualizando Termux..."
pkg update && pkg upgrade -y

# Instalar dependências
echo "🐍 Instalando dependências..."
pkg install -y python git

# Clonar repositório
echo "📥 Clonando repositório..."
cd ~
git clone https://github.com/SEU_USUARIO/message-forwarder.git
cd message-forwarder

# Instalar dependências Python
echo "📦 Instalando bibliotecas Python..."
pip install -r requirements.txt

# Configurar arquivo de configuração
echo "⚙️ Configurando credenciais..."
cp client_config.example.json client_config.json

echo "📝 IMPORTANTE: Configure suas credenciais:"
echo "   nano client_config.json"
echo ""

# Criar script de inicialização
cat > start_termux.sh << 'EOF'
#!/bin/bash
cd ~/message-forwarder
python forwarders/auto_forwarder.py
EOF

chmod +x start_termux.sh

echo "✅ Setup concluído!"
echo ""
echo "📋 Próximos passos:"
echo "1. Configure suas credenciais:"
echo "   nano client_config.json"
echo ""
echo "2. Execute o bot:"
echo "   ./start_termux.sh"
echo ""
echo "💡 Dicas para Termux:"
echo "   • Mantenha o celular carregando"
echo "   • Desative otimização de bateria para Termux"
echo "   • Use 'screen' para rodar em background:"
echo "     pkg install screen"
echo "     screen -S forwarder"
echo "     ./start_termux.sh"
echo "     # Ctrl+A, D para desanexar"
echo "     # screen -r forwarder para anexar novamente"
