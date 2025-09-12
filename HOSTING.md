# 🌐 Guia Completo de Hospedagem Gratuita

## 🎯 **Melhores Opções Gratuitas**

### 1. 🏆 **Oracle Cloud Always Free** (RECOMENDADO)

- ✅ **100% Gratuito para sempre**
- ✅ **Recursos**: 2 VMs com 1GB RAM cada
- ✅ **Uptime**: 24/7 real
- ✅ **Tráfego**: 10TB/mês

**Setup:**

```bash
# 1. Criar conta em oracle.com/cloud
# 2. Criar VM Ubuntu
# 3. Conectar via SSH
wget https://raw.githubusercontent.com/SEU_USUARIO/message-forwarder/main/setup_oracle_cloud.sh
chmod +x setup_oracle_cloud.sh
./setup_oracle_cloud.sh
```

### 2. 📱 **Termux (Android)**

- ✅ **Totalmente grátis**
- ✅ **Seu próprio dispositivo**
- ⚠️ **Precisa ficar carregando**

**Setup:**

```bash
# 1. Instalar Termux da F-Droid ou Google Play
# 2. No Termux:
curl -o setup_termux.sh https://raw.githubusercontent.com/SEU_USUARIO/message-forwarder/main/setup_termux.sh
bash setup_termux.sh
```

### 3. 🚂 **Railway.app**

- ✅ **$5 grátis/mês**
- ✅ **Deploy automático**
- ⚠️ **~21 dias/mês**

**Setup:**

```bash
# 1. Fork este repositório no GitHub
# 2. Conectar Railway ao GitHub
# 3. Deploy automático via Dockerfile
# 4. Configurar variáveis de ambiente no painel
```

### 4. 🌊 **Fly.io**

- ✅ **3 VMs gratuitas**
- ✅ **256MB RAM cada**
- ⚠️ **160 horas/mês**

**Setup:**

```bash
# 1. Instalar Fly CLI
# 2. fly auth signup
# 3. fly launch (usa fly.toml)
# 4. fly secrets set API_ID=... API_HASH=...
```

### 5. 🎓 **GitHub Codespaces**

- ✅ **120 horas/mês grátis**
- ✅ **Direto no browser**
- ⚠️ **Para desenvolvimento/testes**

**Setup:**

```bash
# 1. Abrir repositório no GitHub
# 2. Code > Codespaces > Create
# 3. Terminal automático com ambiente pronto
```

## 🔧 **Configuração de Variáveis de Ambiente**

Para plataformas em nuvem, use variáveis de ambiente ao invés do arquivo JSON:

```bash
# Definir variáveis:
export API_ID=seu_api_id
export API_HASH=sua_api_hash
export PHONE_NUMBER=seu_numero
export SOURCE_USER_ID=779230055
export TARGET_CHAT_ID=id_do_grupo
```

## 🛠️ **Comandos Úteis**

### **Oracle Cloud:**

```bash
# Ver logs do serviço
sudo journalctl -u message-forwarder -f

# Parar/iniciar serviço
sudo systemctl stop message-forwarder
sudo systemctl start message-forwarder

# Status do serviço
sudo systemctl status message-forwarder
```

### **Termux:**

```bash
# Rodar em background
pkg install screen
screen -S forwarder
./start_termux.sh
# Ctrl+A, D para desanexar

# Reconectar
screen -r forwarder
```

### **Railway/Fly.io:**

```bash
# Railway
railway logs

# Fly.io
fly logs
fly status
```

## ⚠️ **Considerações Importantes**

### **Segurança:**

- 🔒 Nunca commite `client_config.json` no Git
- 🔐 Use variáveis de ambiente em produção
- 🚫 Não compartilhe arquivos `.session`

### **Confiabilidade:**

- 🔄 Oracle Cloud: Mais estável para 24/7
- 📱 Termux: Depende da bateria/conexão
- ☁️ Outras: Limitações de tempo/recursos

### **Monitoramento:**

- 📊 Configure logs para debug
- 🔔 Use `debug: true` no config
- 📱 Monitore se as mensagens estão chegando

## 🎯 **Configuração de Filtros na Nuvem**

### **📝 Geração Automática de Variáveis**

Use o gerador para criar as variáveis de ambiente:

```bash
# Gerar variáveis baseadas na configuração local
python3 generate_env.py
```

### **🎛️ Variáveis de Ambiente dos Filtros**

**Básicas:**

```env
API_ID=sua_api_id
API_HASH=sua_api_hash
PHONE_NUMBER=+5511999999999
SOURCE_USER_ID=779230055
TARGET_CHAT_ID=-4197130508
DEBUG=true
```

**Filtros de Estratégia:**

```env
STRATEGY_FILTERS_ENABLED=true
STRATEGY_FILTERS_MODE=whitelist
STRATEGY_FILTERS_STRATEGIES=over,under,corner
```

### **🚀 Configuração por Plataforma**

**Railway:**

```bash
railway variables set \
  STRATEGY_FILTERS_ENABLED=true \
  STRATEGY_FILTERS_MODE=whitelist \
  STRATEGY_FILTERS_STRATEGIES=over,under,corner
```

**Fly.io:**

```bash
fly secrets set STRATEGY_FILTERS_ENABLED=true
fly secrets set STRATEGY_FILTERS_MODE=whitelist
fly secrets set STRATEGY_FILTERS_STRATEGIES=over,under,corner
```

**Render/Heroku:**

- Configure via painel web
- Uma variável por linha

### **💡 Exemplos de Filtros na Nuvem**

**Apenas Over/Under:**

```env
STRATEGY_FILTERS_ENABLED=true
STRATEGY_FILTERS_MODE=whitelist
STRATEGY_FILTERS_STRATEGIES=over,under
```

**Bloquear Lay/Handicap:**

```env
STRATEGY_FILTERS_ENABLED=true
STRATEGY_FILTERS_MODE=blacklist
STRATEGY_FILTERS_STRATEGIES=lay,handicap
```

**Desabilitar Filtros:**

```env
STRATEGY_FILTERS_ENABLED=false
```

## 🎯 **Recomendação Final**

**Para uso sério 24/7:** Oracle Cloud Always Free  
**Para testes/desenvolvimento:** GitHub Codespaces  
**Para simplicidade:** Termux no Android  
**Para deploy rápido:** Railway.app
