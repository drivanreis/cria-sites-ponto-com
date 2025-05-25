# File: backend/src/utils/datetime_utils.py

from datetime import datetime

def get_current_datetime_str() -> str:
    """
    Retorna a data e hora atuais formatadas como 'DD/MM/YYYY HH:MM:SS'.
    """
    now = datetime.now()
    return now.strftime("%d/%m/%Y %H:%M:%S")

# Você pode adicionar outras funções de manipulação de data/hora aqui no futuro, se precisar.