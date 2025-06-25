# File: pega_app_code.sh

cd src

#!/bin/bash

# Nome do arquivo de saída
OUTPUT_FILE="todos_os_codigos_python_do_meu_projeto.txt"

# Limpa o arquivo de saída se ele já existir
> "$OUTPUT_FILE"

echo "Coletando arquivos Python e salvando em '$OUTPUT_FILE' (ignorando __init__.py)..."
echo "" >> "$OUTPUT_FILE"

# Encontra todos os arquivos .py a partir do diretório atual,
# mas exclui os arquivos __init__.py
find . -name "*.py" ! -name "__init__.py" | while read -r filepath; do
    echo "Processando: $filepath"
    
    # Adiciona um cabeçalho para indicar o nome do arquivo
    echo "--- INÍCIO DO ARQUIVO: $filepath ---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE" # Adiciona uma linha em branco para melhor legibilidade
    
    # Copia o conteúdo do arquivo para o arquivo de saída
    cat "$filepath" >> "$OUTPUT_FILE"
    
    echo "" >> "$OUTPUT_FILE" # Adiciona uma linha em branco após o conteúdo do arquivo
    echo "--- FIM DO ARQUIVO: $filepath ---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE" # Adiciona uma linha em branco para separar os arquivos
done

echo ""
echo "Concluído! Todos os códigos foram salvos em '$OUTPUT_FILE'."