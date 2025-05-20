# File: backend/src/utils/datetime_utils.py
# Módulo de utilitários para manipulação de data e hora com fuso horário de Brasília.

from datetime import datetime
import pytz # Certifique-se de que 'pytz' está no requirements.txt

# Função para obter a hora atual em Brasília
def get_current_datetime_brasilia() -> datetime:
    """
    Retorna o horário atual no fuso horário de Brasília (América/Sao_Paulo),
    com informações de fuso horário anexadas.
    """
    timezone_brasilia = pytz.timezone("America/Sao_Paulo")
    # datetime.now(timezone_brasilia) já retorna um datetime 'aware'
    return datetime.now(timezone_brasilia)

# Função para converter string para datetime (se necessário)
def convert_string_to_datetime(user_datetime_str: str) -> datetime:
    """
    Converte uma string de data/hora nos formatos 'DD-MM-YYYY HH:MM[:SS]' para um objeto datetime.
    """
    try:
        # Tenta com segundos
        return datetime.strptime(user_datetime_str, "%d-%m-%Y %H:%M:%S")
    except ValueError:
        # Tenta sem segundos
        return datetime.strptime(user_datetime_str, "%d-%m-%Y %H:%M")