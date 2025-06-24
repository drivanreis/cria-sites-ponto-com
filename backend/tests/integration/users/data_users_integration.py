# File: backend/tests/integration/users/data_users_integration.py

# Helpers para gerar dados de teste

import random

def get_valid_manual_user_data(suffix: str = "") -> dict:
    # Gera um phone_number numérico com 12 a 14 dígitos
    phone_length = random.randint(12, 14)
    phone_number = ''.join([str(random.randint(0, 9)) for _ in range(phone_length)])

    return {
        "nickname": f"Manual User {suffix}",
        "email": f"manual{suffix}@example.com",
        "phone_number": phone_number,
        "password": "SecurePassword123!"
    }

def get_valid_social_user_data(suffix: str = "") -> dict:
    return {
        "nickname": f"Social User {suffix}",
        "google_id": f"google-oauth-{suffix}",
        "github_id": f"github-oauth-{suffix}"
    }
