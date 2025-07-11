#!/bin/bash

clear
echo "Iniciando"
cd backend
cd src
rm todos_os_codigos_py_do_meu_projeto.txt
cd ..
./pega_app_code.sh
cd ..
cd frontend
cd src
rm todos_os_codigos_ts_e_tsx_do_meu_projeto.txt
cd ..
./pega_app_code.sh
clear
cd src
clear
tree -I node*
cd ..
