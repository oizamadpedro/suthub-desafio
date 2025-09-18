# Usa a imagem oficial do Python 3.8
FROM python:3.8-slim

# Define diretório de trabalho dentro do container
WORKDIR /app

# Instala dependências básicas do sistema (útil para pacotes que precisam compilar coisas)
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos de requirements primeiro (para melhor uso de cache)
COPY requirements-dev.txt .

# Instala dependências do projeto
RUN pip install --upgrade pip setuptools wheel \
    && pip install -r requirements-dev.txt

# Copia o restante do código para dentro do container
COPY . .

# Expõe a porta padrão do FastAPI/Uvicorn
EXPOSE 8000

# Comando default (pode ser sobrescrito no docker-compose)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
