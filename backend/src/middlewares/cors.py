# File: backend/src/middlewares/cors.py

from fastapi.middleware.cors import CORSMiddleware
import os

# Lista de origens permitidas para requisições CORS
# Em desenvolvimento, você pode usar "*" para permitir todas as origens,
# mas em produção, especifique as origens exatas do seu frontend.
# Exemplo: ["http://localhost:3000", "https://seufrotend.com"]
ALLOWED_ORIGINS = [
    "http://localhost:3000", # Exemplo para React dev server
    os.environ.get('FRONTEND_NGROK_URL_FOR_CORS'),
]

# Configurações do Middleware CORS
# Para serem usadas na aplicação FastAPI
CORS_MIDDLEWARE_SETTINGS = {
    "allow_origins": ALLOWED_ORIGINS,
    "allow_credentials": True, # Permitir cookies, cabeçalhos de autorização, etc.
    "allow_methods": ["*"],    # Permitir todos os métodos (GET, POST, PUT, DELETE, OPTIONS, etc.)
    "allow_headers": ["*"],    # Permitir todos os cabeçalhos
}