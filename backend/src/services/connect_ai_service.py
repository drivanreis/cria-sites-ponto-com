# File: backend/src/services/connect_ai_service.py

import httpx
import json
import logging
from typing import Dict, Any
from fastapi import HTTPException, status # Para levantar exceções HTTP específicas

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def call_external_ai_api(
    endpoint_url: str,
    endpoint_key: str,
    headers_template: Dict[str, Any],
    body_template: Dict[str, Any],
    prompt_content: str,
    ia_name: str # Para logging e potenciais adaptações futuras
) -> str:
    """
    Função de baixo nível para fazer a chamada HTTP para a API de IA externa.
    Retorna a string de resposta de texto da IA.
    Levanta HTTPException em caso de falha de conexão ou resposta inválida.
    """
    logger.info(f"Chamando API externa de IA ({ia_name}) em: {endpoint_url}")
    logger.debug(f"Prompt Content (primeiros 100 chars): {prompt_content[:100]}...")

    # A lógica de como o prompt_content é inserido no body_template
    # depende da API de IA (Gemini, OpenAI, etc.).
    final_body = body_template.copy()
    
    # Lógica flexível para injetar o prompt:
    # Esta parte precisa ser adaptada ao formato exato esperado pela sua IA!
    # O exemplo abaixo cobre os formatos comuns para OpenAI-like (messages) e Gemini (contents).
    if 'messages' in final_body and isinstance(final_body['messages'], list):
        # Para modelos baseados em 'messages' (OpenAI, por exemplo)
        final_body['messages'].append({"role": "user", "content": prompt_content})
    elif 'contents' in final_body and isinstance(final_body['contents'], list):
        # Para modelos baseados em 'contents' (Gemini, por exemplo)
        final_body['contents'].append({"parts": [{"text": prompt_content}]})
    elif 'prompt' in final_body and isinstance(final_body['prompt'], str):
        # Para modelos mais simples que usam uma chave 'prompt'
        final_body['prompt'] = final_body['prompt'].format(user_input=prompt_content)
    else:
        # Fallback: Se não encontrou um formato conhecido, tentamos enviar o prompt diretamente
        # Isso é mais arriscado e pode falhar dependendo da IA.
        logger.warning(f"Formato de body_template não reconhecido para IA {ia_name}. Tentando enviar prompt diretamente.")
        # Se o body_template estiver vazio, pode-se tentar `{"prompt": prompt_content}` ou `{"text": prompt_content}`
        # Para este caso genérico de teste, é melhor que o `body_template` no DB já esteja pré-formatado
        # com os placeholders ou estrutura base esperada.
        # Vamos assumir que um dos formatos acima será utilizado.
        # Se você tiver um caso de uso onde o `body_template` é sempre `{}` e o `prompt_content`
        # precisa ser o valor de uma chave específica, você precisaria adicionar essa lógica aqui.
        # Exemplo: `final_body = {"text": prompt_content}` se o template estiver vazio.
        
        # Para o propósito deste teste de conectividade, assumiremos que o `body_template`
        # no banco de dados já reflete a estrutura esperada pela IA.
        # Se for um template vazio, e a IA espera, por exemplo, JSON de um único campo "prompt",
        # então o `body_template` no DB deveria ser `{"prompt": "{user_input}"}` e o `prompt_content`
        # seria substituído pelo `{user_input}`.

        # Como fallback para a simulação, se nada for encontrado, tentamos injetar no primeiro lugar razoável
        # ou apenas passar o prompt_content.
        if not final_body: # Se o body_template estiver vazio
             final_body = {"prompt": prompt_content} # Tentativa genérica
        else: # Se o body_template tem chaves mas nenhuma delas correspondeu
             # Pode ser necessário iterar e substituir um placeholder, e.g., "{INPUT_TEXT}"
             pass # A complexidade real de `body_template` é configurada no DB

    headers = {**headers_template}
    # Adicionar a chave de API ao Authorization header ou como um parâmetro de query,
    # dependendo de como a API de IA espera. Assumimos Authorization Bearer aqui.
    if endpoint_key:
        headers["Authorization"] = f"Bearer {endpoint_key}"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client: # Aumentar timeout para APIs de IA
            response = await client.post(endpoint_url, headers=headers, json=final_body)
            response.raise_for_status() # Levanta HTTPStatusError para respostas 4xx/5xx
            response_data = response.json()
            
            # --- Lógica para extrair a resposta de texto da IA ---
            # Esta parte é altamente dependente da estrutura da resposta da IA.
            # Exemplos comuns:
            if ia_name == "OpenAI" or ia_name == "ChatGPT":
                return response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
            elif ia_name == "Gemini":
                # Pode ser 'candidates' ou 'response', e a estrutura pode variar (text, parts, etc.)
                candidates = response_data.get('candidates', [])
                if candidates:
                    parts = candidates[0].get('content', {}).get('parts', [])
                    if parts:
                        return parts[0].get('text', '')
                return "" # Retorna vazio se não encontrar
            elif ia_name == "DeepSeek": # Exemplo para DeepSeek, que pode ter estrutura similar a OpenAI
                return response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
            # Adicione mais 'elif' para outros provedores de IA que você planeja usar.
            
            # Fallback genérico se o ia_name não for reconhecido ou a estrutura for inesperada
            logger.warning(f"Formato de resposta da IA '{ia_name}' não reconhecido. Tentando extração genérica.")
            # Uma tentativa de extração genérica de um campo 'text' ou 'response'.
            return response_data.get('text', response_data.get('response', {}).get('text', str(response_data)))

    except httpx.HTTPStatusError as e:
        logger.error(f"Erro HTTP da API de IA ({ia_name}): {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"Erro da API de IA ({ia_name}): {e.response.text}")
    except httpx.RequestError as e:
        logger.error(f"Erro de rede ao chamar API de IA ({ia_name}): {e}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Não foi possível conectar com a API de IA ({ia_name}). Verifique a URL e a conexão.")
    except json.JSONDecodeError:
        logger.error(f"Resposta da API de IA ({ia_name}) não é um JSON válido: {response.text if 'response' in locals() else 'Nenhuma resposta'}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Resposta inválida da API de IA ({ia_name}). Não é um JSON.")
    except Exception as e:
        logger.error(f"Erro inesperado ao chamar API de IA ({ia_name}): {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno ao processar resposta da IA ({ia_name}).")