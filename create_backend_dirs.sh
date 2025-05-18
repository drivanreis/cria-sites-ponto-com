# File: ./create_backend_dirs.sh
#!/bin/bash

# Navega para o diretório raiz do projeto (onde o repositório foi clonado)
# Assumindo que você está na raiz do projeto ao executar este script.
# Se não estiver, ajuste o caminho conforme necessário.

echo "Criando estrutura de diretórios para Backend e Database..."

mkdir -p backend/src/{db,models,cruds,schemas,routers,services,utils,middlewares}
mkdir -p database

echo "Estrutura de diretórios criada."