# File: backend/Dockerfile

# Use uma imagem base com Python compatível com a versão do seu ambiente virtual
FROM python:3.10-slim

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia o arquivo de requisitos para o diretório de trabalho
COPY requirements.txt .

# Instala as dependências Python.
# Usamos --no-cache-dir para evitar armazenar o cache do pip na imagem final, reduzindo o tamanho.
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto do código fonte do backend e o arquivo .env
# O .env é copiado para desenvolvimento; em produção, variáveis de ambiente seguras são preferidas.
COPY ./src /app/src

# Copia o .env para a raiz do WORKDIR /app
COPY .env /app/

# Copia a pasta alembic/ e o arquivo alembic.ini para dentro do contêiner
COPY ./alembic /app/alembic
COPY alembic.ini /app/

# Comando padrão para manter o contêiner rodando em desenvolvimento,
# permitindo que você execute comandos dentro dele via docker compose exec.
# O comando real para iniciar a aplicação FastAPI pode ser definido no docker-compose.yml.
CMD ["tail", "-f", "/dev/null"]