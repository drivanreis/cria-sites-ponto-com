# File: faz_tudo.sh
#!/bin/bash

clear
sudo rm -f backend/alembic/versions/*.py
sudo find . -type d -name "__pycache__" -exec rm -rf {} +
./limpeza_docker.sh
sleep 10
docker compose up -d --build
sleep 15
./init_alembic.sh