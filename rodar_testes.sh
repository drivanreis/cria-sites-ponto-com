# File: rodar_testes.sh
#!/bin/bash

clear

LOG_FILE="pytest_log_$(date +%Y%m%d_%H%M%S).txt" # Nome do arquivo de log com timestamp

echo "Executando testes e salvando log em: $LOG_FILE"
echo "----------------------------------------------" >> $LOG_FILE # Adiciona linha divisória ao log

# docker compose exec backend pytest > $LOG_FILE 2>&1
# docker compose exec backend pytest --cov=. tests/admin_users/ tests/users/ tests/test_auth.py tests/employees/ > $LOG_FILE 2>&1

# O comando para rodar o arquivo específico (descomente o que precisar)

# docker compose exec backend pytest tests/test_auth.py > $LOG_FILE 2>&1
docker compose exec backend pytest tests/users/test_users_crud.py > $LOG_FILE 2>&1
# docker compose exec backend pytest tests/users/test_users_permissions.py > $LOG_FILE 2>&1
# docker compose exec backend pytest tests/admin_users/test_admin_users_crud.py > $LOG_FILE 2>&1
# docker compose exec backend pytest tests/admin_users/test_admin_users_permissions.py > $LOG_FILE 2>&1
# docker compose exec backend pytest tests/employees/test_employees_crud.py > $LOG_FILE 2>&1
# docker compose exec backend pytest tests/employees/test_employees_permissions.py > $LOG_FILE 2>&1
echo "----------------------------------------------" >> $LOG_FILE
echo "Testes concluídos. Verifique o arquivo: $LOG_FILE"