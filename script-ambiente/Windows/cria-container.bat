@echo off
echo "Construindo a imagem Docker..."
docker build -t cria-sites-ponto-com .
echo "Iniciando os containers com Docker Compose..."
docker compose up -d
echo "Processo concluído!"
pause