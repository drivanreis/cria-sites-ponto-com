#!/bin/bash

# Este script decide se inicia os túneis ngrok ou usa localhost,
# e exporta as URLs como variáveis de ambiente para o shell chamador.
# IMPORTANTE: Ele DEVE ser 'sourced' (executado com 'source ./start_ngrok_tunnels.sh')
# pelo script principal (faz_tudo.sh) para que as variáveis exportadas fiquem disponíveis.

# Variáveis globais para o status da operação do ngrok
# Estas serão exportadas e usadas pelo faz_tudo.sh
export CREATE_NGROK_TUNNEL_FLAG="N" # 'S' se tentou criar túnel
export NGROK_SCRIPT_STATUS=0        # 0 para sucesso, 1 para falha do ngrok


echo -n "Criar túnel ngrok para acesso externo? (S/N): "
read -r response

if [[ "$response" =~ ^[Ss]$ ]]; then
    CREATE_NGROK_TUNNEL_FLAG="S" # Define a flag para indicar que tentamos criar o túnel

    echo "Iniciando túneis ngrok para frontend (porta 3000) e backend (porta 8000) em uma NOVA JANELA DE TERMINAL..."

    # Parar ngrok existente para garantir que uma nova sessão seja iniciada
    killall ngrok > /dev/null 2>&1
    sleep 1

    # Define um arquivo de log específico para o ngrok usar.
    NGROK_LOG_FILE="ngrok_session_$(date +%s).log"
    echo "Log do ngrok será salvo em: $NGROK_LOG_FILE"

    # Iniciar o ngrok em uma nova janela de terminal para Ubuntu (gnome-terminal)
    # IMPORTANTE: A nova janela deve permanecer aberta!
    gnome-terminal --title="NGROK TUNNELS - DO NOT CLOSE" -- bash -c "ngrok start --all --log $NGROK_LOG_FILE; exec bash" &

    # Dê um tempo generoso para o ngrok iniciar e escrever as URLs no arquivo de log.
    sleep 15 # Aumentado para dar tempo suficiente.

    # --- Depuração: Exibir o conteúdo do arquivo de log do ngrok ---
    echo "--- Conteúdo do arquivo de log do ngrok ($NGROK_LOG_FILE) ---"
    cat "$NGROK_LOG_FILE"
    echo "--- Fim do conteúdo do arquivo de log do ngrok ---"

    # Extrair as URLs do log do ngrok.
    FRONTEND_NGROK_URL=$(grep 'url=' "$NGROK_LOG_FILE" | grep 'localhost:3000' | head -1 | awk -F'url=' '{print $2}' | cut -d' ' -f1 | tr -d '\r')
    if [ -z "$FRONTEND_NGROK_URL" ]; then
        FRONTEND_NGROK_URL=$(grep 'public_url=' "$NGROK_LOG_FILE" | grep 'localhost:3000' | head -1 | awk -F'public_url=' '{print $2}' | cut -d' ' -f1 | tr -d '\r')
    fi
    if [ -z "$FRONTEND_NGROK_URL" ]; then
        FRONTEND_NGROK_URL=$(grep 'Forwarding' "$NGROK_LOG_FILE" | grep 'localhost:3000' | head -1 | awk '{print $NF}' | tr -d '\r')
    fi

    BACKEND_NGROK_URL=$(grep 'url=' "$NGROK_LOG_FILE" | grep 'localhost:8000' | head -1 | awk -F'url=' '{print $2}' | cut -d' ' -f1 | tr -d '\r')
    if [ -z "$BACKEND_NGROK_URL" ]; then
        BACKEND_NGROK_URL=$(grep 'public_url=' "$NGROK_LOG_FILE" | grep 'localhost:8000' | head -1 | awk -F'public_url=' '{print $2}' | cut -d' ' -f1 | tr -d '\r')
    fi
    if [ -z "$BACKEND_NGROK_URL" ]; then
        BACKEND_NGROK_URL=$(grep 'Forwarding' "$NGROK_LOG_FILE" | grep 'localhost:8000' | head -1 | awk '{print $NF}' | tr -d '\r')
    fi
    
    FRONTEND_NGROK_HOST=$(echo "$FRONTEND_NGROK_URL" | sed 's/https:\/\///' | tr -d '\r')


    # Verifica se as URLs foram capturadas com sucesso. Se não, define status de falha.
    if [ -z "$FRONTEND_NGROK_URL" ] || [ -z "$BACKEND_NGROK_URL" ]; then
        echo "ERRO: Não foi possível obter as URLs do ngrok. Verifique o arquivo $NGROK_LOG_FILE e a janela do ngrok."
        echo "Definindo variáveis de ambiente para 'localhost' como fallback, pois o ngrok falhou."
        export BACKEND_NGROK_URL="http://localhost:8000"
        export FRONTEND_NGROK_HOST="localhost"
        export FRONTEND_NGROK_URL="http://localhost:3000"
        NGROK_SCRIPT_STATUS=1 # Define o status como falha
    else
        echo "---------------------------------------------------"
        echo "TÚNEIS NGROK ATIVOS (na nova janela de terminal):"
        echo "Frontend URL (acesso público): $FRONTEND_NGROK_URL"
        echo "Backend URL (para o Frontend): $BACKEND_NGROK_URL"
        echo "---------------------------------------------------"
        NGROK_SCRIPT_STATUS=0 # Define o status como sucesso
    fi
else
    echo "Não criando túnel ngrok. Usando URLs 'localhost' para desenvolvimento local."
    # Define as variáveis de ambiente para localhost
    export BACKEND_NGROK_URL="http://localhost:8000"
    export FRONTEND_NGROK_HOST="localhost" # Para vite.config.ts
    export FRONTEND_NGROK_URL="http://localhost:3000" # Para CORS no backend
    NGROK_SCRIPT_STATUS=0 # Considera sucesso para o caso de não querer ngrok
fi

# Exporta as variáveis para que fiquem disponíveis no shell que chamou este script.
# (Já estão exportadas acima, mas para clareza)
export BACKEND_NGROK_URL
export FRONTEND_NGROK_HOST
export FRONTEND_NGROK_URL
export CREATE_NGROK_TUNNEL_FLAG
export NGROK_SCRIPT_STATUS

# Note: Não há 'return' no final, pois o script principal o sourcéia e não precisa de um status de retorno direto aqui.