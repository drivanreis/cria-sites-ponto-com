# File: backend/src/utils/validate_password.py

import re

def validate_password_complexity(value: str) -> str:
    """
    Valida a complexidade de uma senha.
    Requisitos:
    - Pelo menos 6 caracteres (mínimo, considere usar 8 ou mais para maior segurança)
    - Pelo menos um número
    - Pelo menos uma letra maiúscula
    - Pelo menos uma letra minúscula
    - Pelo menos um caractere especial (!@#$%^&*(),.?":{}|<>)
    """
    # if len(password) < 6:
    #     raise ValueError('A senha deve ter pelo menos 6 caracteres.')
    # if not any(char.isdigit() for char in password):
    #     raise ValueError('A senha deve conter pelo menos um número.')
    # if not any(char.isupper() for char in password):
    #     raise ValueError('A senha deve conter pelo menos uma letra maiúscula.')
    # if not any(char.islower() for char in password):
    #     raise ValueError('A senha deve conter pelo menos uma letra minúscula.')
    # # Regex para caracteres especiais.
    # # Adicione ou remova caracteres conforme suas regras de segurança.
    # # Ex: r"[!@#$%^&*(),.?\":{}|<>]"
    # # Este regex cobre a maioria dos caracteres especiais comuns.
    # if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
    #     raise ValueError('A senha deve conter pelo menos um caractere especial.')
    # return password
    if len(value) < 6:
        raise ValueError('A senha deve ter pelo menos 6 caracteres.')
    if not re.search(r"[A-Z]", value):
        raise ValueError('A senha deve conter pelo menos uma letra maiúscula.')
    if not re.search(r"[a-z]", value):
        raise ValueError('A senha deve conter pelo menos uma letra minúscula.')
    if not re.search(r"[0-9]", value):
        raise ValueError('A senha deve conter pelo menos um dígito.')
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
        raise ValueError('A senha deve conter pelo menos um caractere especial.')
    return value