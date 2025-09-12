# Dockerfile para hospedagem em Railway, Fly.io, etc.

FROM python:3.10-slim

# Configurar diretório de trabalho
WORKDIR /app

# Copiar requirements primeiro (para cache do Docker)
COPY requirements.txt .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretório para sessões
RUN mkdir -p /app/sessions

# Definir variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Expor porta (se necessário para healthcheck)
EXPOSE 8000

# Variáveis de ambiente necessárias (definir na plataforma de deploy):
# API_ID - ID da aplicação Telegram
# API_HASH - Hash da aplicação Telegram  
# PHONE_NUMBER - Número de telefone no formato internacional
# SOURCE_USER_ID - ID do CornerProBot2 (779230055)
# TARGET_CHAT_ID - ID do grupo de destino
# DEBUG - true/false para logs detalhados
# STRATEGY_FILTERS_ENABLED - true/false para habilitar filtros
# STRATEGY_FILTERS_MODE - whitelist/blacklist 
# STRATEGY_FILTERS_STRATEGIES - estratégias separadas por vírgula

# Comando para executar o bot
CMD ["python", "auto_forwarder.py"]
