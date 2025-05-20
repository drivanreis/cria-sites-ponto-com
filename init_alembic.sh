# File: init_alembic.sh
#!/bin/bash

echo "Iniciando a sequência de inicialização do Alembic para criar tabelas..."

# Verifica se os contêineres estão rodando
echo "Verificando se os contêineres 'backend' e 'db' estão rodando..."
docker compose ps | grep 'backend' | grep 'Up' > /dev/null
if [ $? -ne 0 ]; then
    echo "Serviço 'backend' não está rodando. Por favor, inicie-o com 'docker compose up -d backend --build'."
    exit 1
fi

docker compose ps | grep 'db' | grep 'Up' > /dev/null
if [ $? -ne 0 ]; then
    echo "Serviço 'db' não está rodando. Por favor, inicie-o com 'docker compose up -d db'."
    exit 1
fi

echo "Contêineres 'backend' e 'db' estão rodando. Prosseguindo..."

# 1. Gerar a primeira migração (vazia)
echo "Passo 1/4: Gerando a primeira migração vazia ('initial_schema_creation')..."
docker compose exec backend alembic revision -m "initial_schema_creation"
if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao gerar a primeira migração. Verifique os logs."
    exit 1
fi
echo "Primeira migração gerada com sucesso."

# 2. Carimbar o banco de dados com a versão HEAD (esta migração)
echo "Passo 2/4: Carimbando o banco de dados com a versão 'head' (initial_schema_creation)..."
docker compose exec backend alembic stamp head
if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao carimbar o banco de dados. Verifique os logs."
    exit 1
fi
echo "Banco de dados carimbado com sucesso."

# 3. Gerar a migração auto-gerada com base nos modelos
echo "Passo 3/4: Gerando a migração auto-gerada ('create_tables')..."
docker compose exec backend alembic revision --autogenerate -m "create_tables"
if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao gerar a migração auto-gerada. Verifique os logs."
    exit 1
fi
echo "Migração 'create_tables' gerada com sucesso. Verifique o arquivo em backend/alembic/versions/."

# 4. Aplicar a migração auto-gerada
echo "Passo 4/4: Aplicando a migração 'create_tables' ao banco de dados..."
docker compose exec backend alembic upgrade head
if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao aplicar a migração. Verifique os logs."
    exit 1
fi
echo "Migração aplicada com sucesso! Suas tabelas devem estar criadas no banco de dados."

echo "Processo de inicialização do Alembic concluído."
echo "Parabéns, Chef! As tabelas estão no lugar!"