#!/bin/bash

clear
echo "Iniciando o processo de limpeza e inicialização do ambiente Docker..."

# --- INÍCIO DA CHAMADA DA LÓGICA TÚNEL NGROK/LOCALHOST ---
# IMPORTANTE: Usar 'source' para que as variáveis exportadas por start_ngrok_tunnels.sh
# fiquem disponíveis neste shell.
source ./start_ngrok_tunnels.sh
# As variáveis $CREATE_NGROK_TUNNEL_FLAG, $NGROK_SCRIPT_STATUS,
# $FRONTEND_NGROK_URL, etc., agora estão disponíveis aqui.
# --- FIM DA CHAMADA DA LÓGICA TÚNEL NGROK/LOCALHOST ---


# --- RESTANTE DO SEU SCRIPT ORIGINAL ---
sudo ./cls_file.sh
sleep 1
./limpeza_docker.sh
sleep 5
# Redundancia:
echo "Remoção forçada de contêineres..."
docker system prune -a -f --volumes
sleep 1

# O docker compose up usará as variáveis de ambiente que foram EXPORTADAS pelo script sourciado
docker compose up -d --build
sleep 20
./init_alembic.sh
sleep 5
docker compose exec backend python3 src/startup.py

echo ""
echo "---------------------------------------------------"
echo "PROCESSO FAZ_TUDO CONCLUÍDO!"
# A mensagem final agora reflete o status real baseado nas variáveis exportadas
if [ "$CREATE_NGROK_TUNNEL_FLAG" = "S" ] && [ "$NGROK_SCRIPT_STATUS" -eq 0 ]; then
    echo "Acesse seu frontend (acesso público) em: $FRONTEND_NGROK_URL"
else
    echo "Acesse seu frontend (acesso local) em: http://localhost:3000"
fi
echo ""
echo "Para parar tudo, execute 'docker compose down' no diretório do seu projeto."
# Se o túnel ngrok foi criado e não falhou, lembre de matar o processo ngrok manualmente se não for encerrado pelo `docker compose down`.
if [ "$CREATE_NGROK_TUNNEL_FLAG" = "S" ] && [ "$NGROK_SCRIPT_STATUS" -eq 0 ]; then
    echo "Lembre-se de fechar a nova janela de terminal do NGROK para encerrar o túnel."
fi
echo "---------------------------------------------------"