# File: faz_tudo.sh
#!/bin/bash

clear
echo "Iniciando o processo de limpeza e inicialização do ambiente Docker..."
sudo ./cls_file.sh
sleep 1
./limpeza_docker.sh
sleep 5
# Redundancia:
echo "Remoção forçada de contêineres..."
docker system prune -a -f --volumes
sleep 1
docker compose up -d --build
sleep 20
./init_alembic.sh
sleep 5
docker compose exec backend python3 src/startup.py