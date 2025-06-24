# File: backend/src/utils/datetime_utils.py

from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+

def get_current_datetime_str() -> str:
    """
    Retorna a data e hora atuais de Fortaleza-CE formatadas como 'DD/MM/YYYY HH:MM:SS'.
    """
    fortaleza_tz = ZoneInfo("America/Fortaleza")
    now = datetime.now(fortaleza_tz)
    return now.strftime("%d/%m/%Y %H:%M:%S")
