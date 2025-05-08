import openai
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

# Configurar a chave da OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def chatbot_inicio(request: Request):
    return templates.TemplateResponse("chatbot_inicio.html", {"request": request})

@app.get("/chatbot-pessoa", response_class=HTMLResponse)
async def chatbot_pessoa(request: Request):
    return templates.TemplateResponse("chatbot_pessoa.html", {"request": request})

@app.post("/chatbot-pessoa", response_class=HTMLResponse)
async def responder_chatbot_pessoa(request: Request, mensagem: str = Form(...)):
    try:
        # Fazendo a chamada para o modelo GPT-3/4 da OpenAI
        response = openai.Completion.create(
            model="text-davinci-003",  # ou outro modelo, como "gpt-4"
            prompt=(
                f"Cliente: {mensagem}\nIA: O que você gostaria de divulgar sobre você? "
                "Conte-nos mais sobre sua carreira, seus hobbies ou algo que te represente. "
                "Se você puder ser específico, isso ajudará a construir o seu site."
            ),
            max_tokens=150,
            temperature=0.7
        )
        resposta_ia = response.choices[0].text.strip()
        return HTMLResponse(content=f"<strong>IA:</strong> {resposta_ia}")
    
    except Exception as e:
        return HTMLResponse(content=f"<strong>Erro ao consultar a IA:</strong> {str(e)}")
