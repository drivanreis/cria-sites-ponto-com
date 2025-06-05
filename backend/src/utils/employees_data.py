# File: backend/src/utils/employees_data.py

from typing import List, Dict, Any

# Dados para inicialização dos Employees (personagens) no banco de dados.
# Estes dados são usados para criar registros mínimos quando a aplicação inicia,
# caso eles ainda não existam.
# As chaves de API (`endpoint_key`) devem ser substituídas pelas suas chaves reais
# ou gerenciadas via variáveis de ambiente em um ambiente de produção.
REQUIRED_EMPLOYEES_DATA: List[Dict[str, Any]] = [
    {
        "sender_type": "Entrevistador Pessoal",
        "employee_script": {
            "intro": "Olá, sou seu entrevistador pessoal. Estou aqui para entender suas necessidades para um projeto de desenvolvimento de site. Por favor, me diga o que você tem em mente.",
            "context": "Você é um entrevistador de clientes para projetos de desenvolvimento de sites, focado em entender as necessidades de pessoas físicas. Faça perguntas abertas e guiadas para coletar o máximo de informações sobre o projeto, o público-alvo, funcionalidades desejadas e orçamento. Sempre tente fazer a próxima pergunta para extrair mais detalhes."
        },
        "ia_name": "Gemini",
        "endpoint_url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent", # Exemplo de URL para Gemini
        "endpoint_key": "SUA_CHAVE_GEMINI_ENTREVISTADOR_PESSOAL_AQUI", # SUBSTITUA PELA SUA CHAVE REAL!
        "headers_template": {"Content-Type": "application/json"},
        # Este body_template é um exemplo para APIs que usam o formato de 'messages' ou 'contents'
        "body_template": {
            "contents": [
                {"role": "user", "parts": [{"text": "{user_input}"}]}
            ],
            "generationConfig": {
                "temperature": 0.9, # Temperatura mais alta para respostas mais criativas/conversacionais
                "topK": 1,
                "topP": 1,
                "maxOutputTokens": 2048,
                "stopSequences": []
            },
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ],
        },
    },
    {
        "sender_type": "Assistente de Palco",
        "employee_script": {
            "intro": "Olá, sou o Assistente de Palco. Por favor, forneça as informações da conversa para que eu possa compilar o briefing.",
            "prompt_for_compilation": "Com base no histórico de conversa a seguir, compile um briefing detalhado no formato JSON. O JSON deve conter as seguintes chaves: 'titulo_do_projeto', 'publico_alvo', 'objetivos', 'funcionalidades_principais', 'requisitos_tecnicos', 'prazo_desejado', 'orcamento_estimado', 'observacoes_adicionais'. Se alguma informação não for explicitamente mencionada, use 'Não especificado' ou deixe a chave vazia se o campo for naturalmente um array vazio ou objeto vazio. Não inclua qualquer texto além do JSON. Confirme se necessário. Sua resposta deve ser APENAS o JSON.",
            "context": "Você é um analista de dados, sintetizador de informações e compilador de briefings."
        },
        "ia_name": "Gemini", # O Assistente de Palco também usa uma IA, pode ser Gemini ou outra
        "endpoint_url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent", # Exemplo de URL para Gemini
        "endpoint_key": "SUA_CHAVE_GEMINI_ASSISTENTE_AQUI", # SUBSTITUA PELA SUA CHAVE REAL!
        "headers_template": {"Content-Type": "application/json"},
        # Mesmo body_template do Gemini, mas o prompt será a instrução + histórico
        "body_template": {
            "contents": [
                {"role": "user", "parts": [{"text": "{user_input}"}]}
            ],
            "generationConfig": {
                "temperature": 0.5, # Temperatura mais baixa para respostas mais diretas/fatuais (JSON)
                "topK": 1,
                "topP": 1,
                "maxOutputTokens": 2048,
                "stopSequences": []
            },
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ],
        },
    },
]