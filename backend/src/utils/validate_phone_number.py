# File: backend/src/utils/validate_phone_number.py

import re
from typing import Optional

def validate_phone_number_format(value: Optional[str]) -> Optional[str]:
    """
    Valida o formato de um número de telefone brasileiro com regras mais estritas.
    Requisitos:
    - Obrigatório '+' no início.
    - Obrigatório DDI (2 ou 3 dígitos).
    - Obrigatório DDD (2 dígitos).
    - Obrigatório Número com 8 ou 9 dígitos no final.

    Exemplos válidos: '+5511987654321', '+12345987654321' (se DDI de 3 dígitos permitido)
    Exemplos inválidos: '5511987654321', '987654321', '+5511987654' (muito curto)
    """
    if value is None:
        return value

    # Regex ajustado para as novas regras:
    # ^\+              -> Obrigatório '+' no início
    # (\d{2,3})        -> DDI obrigatório (2 ou 3 dígitos, capturado)
    # (\d{2})          -> DDD obrigatório (2 dígitos, capturado)
    # (\d{8,9})$       -> Número obrigatório (8 ou 9 dígitos no final, capturado)
    # Vou simplificar o regex (Tudo é numero)
    # phone_regex = r"^\+(\d{2,3})(\d{2})(\d{8,9})$"
    phone_regex = r"\d{12,14}"
    
    if not re.fullmatch(phone_regex, value):
        # raise ValueError("Formato de telefone inválido. Use o formato: +DDI DDD NNNNNNNN ou +DDI DDD NNNNNNNNN. Ex: +5511987654321. Deve começar com '+', seguido por DDI (2 ou 3 dígitos), DDD (2 dígitos) e número (8 ou 9 dígitos).")
        raise ValueError("Formato de telefone inválido. Use de 12 a 14 dígitos, apenas números. Ex: 11987654321 ou 5511987654321.")
    
    return value