# File: pega_all_code.sh

#!/bin/bash

# entro no diretório do backend
cd backend
# entro no diretório src
cd src
# excluir o arquivo "todos_os_codigos_python_do_meu_projeto.txt" se ele já existir
rm -f todos_os_codigos_python_do_meu_projeto.txt

# saio do diretório src
cd ..
# entro no diretório tests
cd tests
# excluir o arquivo "todos_os_codigos_Testes_do_meu_projeto.txt" se ele já existir
rm -f todos_os_codigos_Testes_do_meu_projeto.txt
# saio do diretório tests
cd ..
# saio do diretório backend
cd ..
# Estou no diretório raiz do projeto

# Executar pega_app_code.sh
./pega_app_code.sh
# Executar pega_testes_code.sh
./pega_testes_code.sh

# copiar os arquivos de saida para cá/aqui
cp backend/src/todos_os_codigos_python_do_meu_projeto.txt .
cp backend/tests/todos_os_codigos_Testes_do_meu_projeto.txt .
# Exibir mensagem de conclusão
echo "Tudo foi copiado para o diretório atual."