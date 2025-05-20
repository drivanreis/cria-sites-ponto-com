# File: limpeza_docker.sh
#!/bin/bash

echo "Iniciando a limpeza completa do Docker..."

# 1. Parar e remover todos os contêineres em execução
echo "Parando e removendo todos os contêineres em execução..."
docker ps -aq | xargs -r docker stop
docker ps -aq | xargs -r docker rm -f
echo "Contêineres removidos."

# 2. Remover todas as imagens Docker (apenas as que não estão sendo usadas por contêineres rodando)
# A flag -a inclui imagens não usadas
echo "Removendo todas as imagens Docker não usadas..."
docker rmi $(docker images -aq) 2>/dev/null
echo "Imagens removidas ou não encontradas para remoção."

# 3. Remover todos os volumes não utilizados (CUIDADO: isso remove dados de DB!)
echo "Removendo todos os volumes não usados (CUIDADO: dados de DB em volumes anônimos serão perdidos)..."
docker volume prune -f
echo "Volumes removidos."

# 4. Remover todas as redes não utilizadas
echo "Removendo todas as redes não usadas..."
docker network prune -f
echo "Redes removidas."

# 5. Limpeza geral do sistema Docker (libera espaço de cache, etc.)
echo "Executando limpeza geral do sistema Docker..."
docker system prune -a -f --volumes
echo "Limpeza geral do Docker concluída."

echo "Limpeza completa do Docker finalizada!"
echo "Agora você pode recriar seus serviços com 'docker compose up -d --build'"