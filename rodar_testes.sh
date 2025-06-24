# File: rodar_testes.sh
#!/bin/bash

clear

LOG_FILE="pytest_log_$(date +%Y%m%d_%H%M%S).txt" # Nome do arquivo de log com timestamp

echo "Executando testes e salvando log em: $LOG_FILE"
echo "----------------------------------------------" >> "$LOG_FILE" # Adiciona linha divisória ao log

# O comando para rodar os arquivos específicos (descomente o que precisar)

# Testes de autenticação
# docker compose exec backend pytest tests/integration/test_auth.py >> "$LOG_FILE" 2>&1

# Testes de integração de usuários (Pate 01)
# docker compose exec backend pytest tests/integration/users/test_users_integration_bl01.py >> "$LOG_FILE" 2>&1
# docker compose exec backend pytest tests/integration/users/test_users_integration_bl02.py >> "$LOG_FILE" 2>&1
# docker compose exec backend pytest tests/integration/users/test_users_integration_bl03.py >> "$LOG_FILE" 2>&1
# docker compose exec backend pytest tests/integration/users/test_users_integration_bl04.py >> "$LOG_FILE" 2>&1
# docker compose exec backend pytest tests/integration/users/test_users_integration_bl05.py >> "$LOG_FILE" 2>&1
# docker compose exec backend pytest tests/integration/users/test_users_integration_bl06.py >> "$LOG_FILE" 2>&1


# Testes de integração de administradores
docker compose exec backend pytest tests/integration/admin_users/test_admin_users_integration_01.py >> "$LOG_FILE" 2>&1
# docker compose exec backend pytest tests/integration/admin_users/test_admin_users_integration_02.py >> "$LOG_FILE" 2>&1

# Testes de integração de briefings
# docker compose exec backend pytest tests/integration/briefing/test_briefing_integration_01.py >> "$LOG_FILE" 2>&1
# docker compose exec backend pytest tests/integration/briefing/test_briefing_integration_02.py >> "$LOG_FILE" 2>&1

# Testes de integração de personagens
# docker compose exec backend pytest tests/integration/character/test_character_integration_01.py >> "$LOG_FILE" 2>&1
# docker compose exec backend pytest tests/integration/character/test_character_integration_02.py >> "$LOG_FILE" 2>&1

# Testes de integração de chat
# docker compose exec backend pytest tests/integration/chat/test_chat_integration_01.py >> "$LOG_FILE" 2>&1
# docker compose exec backend pytest tests/integration/chat/test_chat_integration_02.py >> "$LOG_FILE" 2>&1

# Testes de integração de funcionários (employees)
# docker compose exec backend pytest tests/integration/employees/test_employees_integration_01.py >> "$LOG_FILE" 2>&1
# docker compose exec backend pytest tests/integration/employees/test_employees_integration_02.py >> "$LOG_FILE" 2>&1

# Adicione aqui outros arquivos de teste unitários ou de integração conforme necessário
# Ex: Testes unitários (se quiser rodá-los com este script)
# docker compose exec backend pytest tests/unit/admin_users/_test_admin_users_crud.py >> "$LOG_FILE" 2>&1
# docker compose exec backend pytest tests/unit/admin_users/_test_admin_users_permissions.py >> "$LOG_FILE" 2>&1
# docker compose exec backend pytest tests/unit/employees/_test_employees_crud.py >> "$LOG_FILE" 2>&1
# docker compose exec backend pytest tests/unit/employees/_test_employees_permissions.py >> "$LOG_FILE" 2>&1
# docker compose exec backend pytest tests/unit/users/_test_futuros.py >> "$LOG_FILE" 2>&1
# docker compose exec backend pytest tests/unit/users/_test_users_crud.py >> "$LOG_FILE" 2>&1


echo "----------------------------------------------" >> "$LOG_FILE"
echo "Testes concluídos. Verifique o arquivo: $LOG_FILE"