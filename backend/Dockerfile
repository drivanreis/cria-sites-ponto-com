# File: backend/Dockerfile

FROM python:3.10-slim

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Instale curl e netcat para os healthchecks e outras utilidades
RUN apt-get update && apt-get install -y curl netcat-traditional && rm -rf /var/lib/apt/lists/*

# Copia APENAS o arquivo de requisitos para o diretório de trabalho
COPY requirements.txt .

# Instala as dependências Python.
# Usamos --no-cache-dir para evitar armazenar o cache do pip na imagem final, reduzindo o tamanho.
RUN pip install --no-cache-dir -r requirements.txt

# Não copiamos mais o código-fonte aqui, pois ele será mapeado via volume no docker-compose.yml
# CMD padrão para manter o contêiner rodando; o comando principal é definido no docker-compose.yml
CMD ["tail", "-f", "/dev/null"]