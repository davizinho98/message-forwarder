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

# Comando para executar o bot
CMD ["python", "auto_forwarder.py"]
