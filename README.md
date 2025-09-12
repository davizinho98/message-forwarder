# 🤖 Message Forwarder Automático

**Automação completa para encaminhar mensagens do Telegram usando Python.**

Sistema que monitora automaticamente mensagens do **CornerProBot2** e as encaminha em tempo real para um grupo específico, sem qualquer intervenção manual.

## 🎯 **Como Funciona**

```
CornerProBot2 → Seu Usuário (monitoramento automático) → Grupo de Destino
```

**100% Automático - Zero Intervenção Manual!**

## ✨ **Características**

- 🔄 **Monitoramento em tempo real** de mensagens do CornerProBot2
- 🚀 **Encaminhamento automático** para grupo configurado
- 🎯 **Filtros de estratégia inteligentes** - escolha quais tipos de mensagem encaminhar
- 📱 **Usa sua própria conta** do Telegram (não precisa de bot)
- 🛡️ **Seguro** - usa biblioteca oficial Pyrogram
- ⚡ **Instantâneo** - mensagens aparecem no grupo imediatamente
- 🔍 **Logs detalhados** de toda atividade

## 📋 **Requisitos**

- Python 3.7+
- Conta do Telegram
- Credenciais da API do Telegram (API_ID e API_HASH)

## 🚀 **Instalação Rápida**

### **Método 1: Ambiente Virtual (Recomendado)**

```bash
# Setup completo com ambiente virtual
./setup_venv.sh

# Ativar ambiente virtual para uso
source venv/bin/activate

# OU usar script de ativação rápida
./activate.sh
```

### **Método 2: Script Automático Simples**

```bash
chmod +x setup.sh
./setup.sh
```

### **Método 3: Manual**

```bash
# 1. Criar ambiente virtual (opcional mas recomendado)
python3 -m venv venv
source venv/bin/activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar
cp client_config.example.json client_config.json
# Edite client_config.json com suas credenciais

# 4. Executar
python auto_forwarder.py
```

## ⚙️ **Configuração**

### **1. Obter Credenciais da API do Telegram**

1. 🌐 Acesse: https://my.telegram.org
2. 📱 Faça login com seu número de telefone
3. ⚙️ Vá em **"API development tools"**
4. 🆕 Clique em **"Create new application"**
5. 📝 Preencha os dados:
   - **App title**: Message Forwarder
   - **Short name**: msg-forwarder
   - **Platform**: Desktop
6. 🔑 Anote o **API_ID** e **API_HASH** gerados

### **2. Configurar o Arquivo**

Edite `client_config.json`:

```json
{
  "api_id": 1234567,
  "api_hash": "abcdef1234567890abcdef1234567890",
  "phone_number": "+5511999999999",
  "source_user_id": 779230055,
  "target_chat_id": -4197130508,
  "debug": true,
  "strategy_filters": {
    "enabled": false,
    "mode": "whitelist",
    "strategies": ["over", "under", "corner"]
  }
}
```

**Campos:**

- `api_id`: ID da aplicação (número)
- `api_hash`: Hash da aplicação (string)
- `phone_number`: Seu número no formato internacional
- `source_user_id`: ID do CornerProBot2 (779230055)
- `target_chat_id`: ID do seu grupo (-4197130508)
- `debug`: Logs detalhados (true/false)
- `strategy_filters`: Configuração de filtros de estratégia (veja seção abaixo)

## 🎯 **Filtros de Estratégia**

**Novo recurso!** Filtre automaticamente quais tipos de mensagem são encaminhadas baseado na estratégia mencionada.

### **🔧 Configuração Manual**

```json
{
  "strategy_filters": {
    "enabled": true,
    "mode": "whitelist",
    "strategies": ["over", "under", "corner", "gol"]
  }
}
```

**Parâmetros:**

- `enabled`: `true` para ativar filtros, `false` para encaminhar tudo
- `mode`:
  - `"whitelist"`: Só encaminha mensagens com estratégias da lista
  - `"blacklist"`: Encaminha tudo EXCETO mensagens com estratégias da lista
- `strategies`: Array com estratégias para filtrar

### **📖 Exemplos de Uso**

**Exemplo 1: Apenas Over/Under**

```json
{
  "enabled": true,
  "mode": "whitelist",
  "strategies": ["over", "under"]
}
```

→ Só encaminha mensagens que contenham "over" ou "under" na primeira linha

**Exemplo 2: Bloquear Lay**

```json
{
  "enabled": true,
  "mode": "blacklist",
  "strategies": ["lay", "handicap"]
}
```

→ Encaminha tudo EXCETO mensagens com "lay" ou "handicap"

**Exemplo 3: Só Escanteios**

```json
{
  "enabled": true,
  "mode": "whitelist",
  "strategies": ["corner", "escanteio"]
}
```

→ Apenas estratégias relacionadas a escanteios

### **🔍 Como Funciona a Detecção**

- 📝 Analisa apenas a **primeira linha** da mensagem
- 🔤 Não diferencia maiúsculas/minúsculas
- 🔍 Busca parcial: "over" encontra "over 2.5", "OVER", etc.
- ⚡ Decisão instantânea para cada mensagem

**Estratégias Comuns:**

- `over`, `under` - Apostas em totais
- `corner`, `escanteio` - Escanteios
- `gol`, `btts` - Mercados de gols
- `lay`, `back` - Tipos de aposta
- `handicap` - Apostas com handicap
- `cartão` - Cartões

## 🎮 **Execução**

```bash
python3 auto_forwarder.py
```

### **Primeira Execução:**

1. 📱 Será solicitado o **código SMS** enviado para seu telefone
2. 🔐 Se tiver verificação em duas etapas, digite a senha
3. ✅ Após autenticação, o sistema ficará monitorando automaticamente

- 🔄 Executa automaticamente sem pedir códigos (sessão salva)

## 🌐 **Deploy na Nuvem**

### **🚀 Preparação para Deploy**

Gere as variáveis de ambiente automaticamente:

```bash
python3 generate_env.py
```

### **☁️ Plataformas Suportadas**

**🏆 Oracle Cloud (Gratuito 24/7):**

```bash
./setup_oracle_cloud.sh
```

**🚂 Railway (Deploy automático):**

1. Fork o repositório no GitHub
2. Conecte Railway ao GitHub
3. Configure as variáveis de ambiente
4. Deploy automático via Dockerfile

**🌊 Fly.io:**

```bash
fly secrets set API_ID=sua_api_id
fly secrets set STRATEGY_FILTERS_ENABLED=true
fly secrets set STRATEGY_FILTERS_STRATEGIES=over,under,corner
```

### **🎯 Filtros na Nuvem**

Os filtros funcionam via **variáveis de ambiente**:

```env
# Habilitar filtros whitelist para Over/Under
STRATEGY_FILTERS_ENABLED=true
STRATEGY_FILTERS_MODE=whitelist
STRATEGY_FILTERS_STRATEGIES=over,under

# Bloquear estratégias específicas
STRATEGY_FILTERS_ENABLED=true
STRATEGY_FILTERS_MODE=blacklist
STRATEGY_FILTERS_STRATEGIES=lay,handicap

# Desabilitar filtros
STRATEGY_FILTERS_ENABLED=false
```

📖 **Guia completo:** [HOSTING.md](HOSTING.md)

### **Execuções Seguintes:**

- 🔄 Executa automaticamente sem pedir códigos (sessão salva)

## 📊 **Logs do Sistema**

```
🚀 Iniciando Message Forwarder Automático...
👤 Logado como: Seu Nome (@seu_username)
🎯 Monitorando mensagens de: CornerProBot2 (@cornerpro2_bot)
📤 Encaminhando para: Nome do Grupo
👂 Aguardando mensagens... (Pressione Ctrl+C para parar)

📨 Nova mensagem do CornerProBot2: 📣 Alerta Estratégia: botteste...
✅ Mensagem encaminhada automaticamente para o grupo!
```

## 🔧 **Estrutura do Projeto**

```
message-forwarder/
├── auto_forwarder.py              # 🤖 Sistema principal
├── setup_filters.py               # 🎯 Configurador de filtros de estratégia
├── test_filters.py                # 🧪 Testador de filtros
├── generate_env.py                # 🌐 Gerador de variáveis de ambiente
├── client_config.example.json     # 📝 Exemplo de configuração
├── client_config.json             # ⚙️ Sua configuração (criar)
├── requirements.txt               # 📦 Dependências Python
├── setup_venv.sh                  # 🐍 Setup ambiente virtual
├── setup_oracle_cloud.sh          # ☁️ Setup Oracle Cloud
├── setup_termux.sh                # 📱 Setup Termux (Android)
├── Dockerfile                     # 🐳 Para deploy em nuvem
├── railway.toml                   # 🚂 Config Railway
├── fly.toml                       # 🌊 Config Fly.io
├── HOSTING.md                     # 📖 Guia completo de hospedagem
├── README.md                      # 📋 Esta documentação
├── .gitignore                     # 🔒 Arquivos ignorados
└── *.session                      # 🔐 Sessões Telegram (auto-gerado)
```

## 🛡️ **Segurança**

- 🔒 **Credenciais protegidas**: `client_config.json` está no `.gitignore`
- 🔐 **Sessões seguras**: Arquivos `.session` são criptografados
- 🚫 **Não compartilhe**: Nunca compartilhe API_HASH ou arquivos .session

## 🐛 **Troubleshooting**

### **Erro de autenticação**

- ✅ Verifique se API_ID e API_HASH estão corretos
- ✅ Confirme se o número de telefone está no formato internacional

### **Usuário fonte não encontrado**

- ✅ Verifique se o `source_user_id` está correto (779230055)
- ✅ Certifique-se de que o CornerProBot2 já enviou pelo menos uma mensagem

### **Chat de destino não encontrado**

- ✅ Verifique se o `target_chat_id` está correto
- ✅ Certifique-se de que você está no grupo de destino

### **Código SMS não chega**

- ✅ Aguarde alguns minutos
- ✅ Verifique se o número está correto
- ✅ Tente novamente

## 🔄 **Como Parar**

```bash
Ctrl + C  # Para parar o monitoramento
```

## ☁️ **Hospedagem Gratuita**

### **Opções para rodar 24/7 gratuitamente:**

#### **1. 🐧 VPS Gratuito - Oracle Cloud (Recomendado)**

- ✅ **Always Free**: 2 VMs gratuitas para sempre
- ✅ **24/7**: Sem limite de tempo
- ✅ **Recursos**: 1GB RAM, 1 vCPU cada VM
- 📝 **Setup**: Ubuntu + Python + systemd service

```bash
# No servidor Oracle:
git clone https://github.com/seu-usuario/message-forwarder
cd message-forwarder
./setup_venv.sh
# Configurar client_config.json
# Criar service do systemd
```

#### **2. 🎁 GitHub Codespaces**

- ✅ **Gratuito**: 120 horas/mês
- ✅ **Fácil**: Diretamente no browser
- ⚠️ **Limitação**: Apenas 60 horas consecutivas

#### **3. 🚀 Railway.app**

- ✅ **Gratuito**: $5 créditos/mês
- ✅ **Deploy automático**: Via GitHub
- ⚠️ **Limitação**: ~21 dias/mês rodando

```dockerfile
# Dockerfile para Railway
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "auto_forwarder.py"]
```

#### **4. 📱 Termux (Android)**

- ✅ **Grátis**: No seu próprio celular
- ✅ **24/7**: Se deixar carregando
- 📝 **Setup**: Instalar Termux + Python

```bash
# No Termux:
pkg install python git
pip install pyrogram tgcrypto
git clone https://github.com/seu-usuario/message-forwarder
cd message-forwarder
python auto_forwarder.py
```

#### **5. 💻 VPS Gratuito - Fly.io**

- ✅ **Gratuito**: 3 VMs pequenas
- ✅ **Simples**: Deploy via Docker
- ⚠️ **Limitação**: 160 horas/mês

### **🎯 Recomendação:**

**Para uso 24/7 real:** Oracle Cloud Always Free  
**Para testes:** GitHub Codespaces  
**Para simplicidade:** Termux no celular

## 📈 **Próximos Passos**

Após configurar:

1. ✅ Execute o sistema
2. ✅ Aguarde uma mensagem do CornerProBot2
3. ✅ Verifique se apareceu automaticamente no grupo
4. ✅ Sistema funcionando - deixe rodando 24/7!

## 🎉 **Resultado**

Agora **toda mensagem** que o CornerProBot2 enviar para você será **automaticamente encaminhada** para o grupo configurado, **em tempo real**, **sem qualquer ação sua**!

---

🤖 **Message Forwarder** - Automação completa para Telegram em Python
