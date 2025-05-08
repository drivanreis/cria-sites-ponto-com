#!/bin/bash
echo "Verificando se o ambiente virtual está ativo..."
if [ ! -z "$VIRTUAL_ENV" ]; then
    echo "Ambiente virtual detectado em $VIRTUAL_ENV."
    echo "Desativando ambiente virtual..."
    deactivate
else
    echo "Ambiente virtual não está ativo."
fi

echo "Navegando para a raiz do projeto..."
cd ../../
echo "Diretório atual: $(pwd)"

echo "Destruindo ambiente virtual..."
rm -rf .venv
if [ $? -ne 0 ]; then
    echo "Erro ao tentar deletar o ambiente virtual."
    exit 1
fi

echo "Ambiente virtual removido com sucesso!"
