FROM python:3.11-slim

WORKDIR /app

# Instalar dependências
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY backend/app/ /app/
COPY frontend/ /app/frontend/

# Porta (Railway usa $PORT)
EXPOSE 8000

# Comando direto (sem cd)
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
