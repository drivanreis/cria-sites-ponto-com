# File: frontend/pega_app_code.sh

#!/bin/bash

cd src

# Nome do arquivo de saída
OUTPUT_FILE="todos_os_codigos_ts_e_tsx_do_meu_projeto.txt"

# Limpa o arquivo de saída se ele já existir
> "$OUTPUT_FILE"

echo "Coletando arquivos TypeScript (.ts e .tsx) e salvando em '$OUTPUT_FILE'..."
echo "" >> "$OUTPUT_FILE"

# Encontra todos os arquivos .ts e .tsx a partir do diretório atual (que é 'src')
find . -name "*.tsx" -o -name "*.ts" | while read -r filepath; do
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
echo "Concluído! Todos os códigos .ts e .tsx foram salvos em '$OUTPUT_FILE'."