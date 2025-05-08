#!/bin/bash
cd ..
cd ..
echo "Criando ambiente virtual em .venv..."
python3 -m venv .venv

echo "Ativando ambiente virtual..."
source .venv/bin/activate

echo "Instalando dependências..."
pip install -r requirements.txt

echo "Ambiente configurado com sucesso!"
