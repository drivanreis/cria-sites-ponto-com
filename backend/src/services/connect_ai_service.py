# File: backend/src/services/connect_ai_service.py

import httpx
import json
import logging
from typing import Dict, Any
from fastapi import HTTPException, status

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def call_external_ai_api(
    endpoint_url: str,
    endpoint_key: str,
    headers_template: Dict[str, Any],
    body_template: Dict[str, Any],
    system_prompt: str,
    user_prompt: str,
    ia_name: str
) -> str:
    """
    Chamada HTTP para API de IA externa.
    Injeta system_prompt e user_prompt no body_template conforme padrão da IA.
    Retorna a resposta em texto.
    """
    logger.info(f"Chamando API externa de IA ({ia_name}) em: {endpoint_url}")
    logger.debug(f"system_prompt (100): {system_prompt[:100]}...")
    logger.debug(f"user_prompt (100): {user_prompt[:100]}...")

    final_body = body_template.copy()

    # --- INJEÇÃO POR TIPO DE IA ---

    if 'messages' in final_body and isinstance(final_body['messages'], list):
        # OpenAI / DeepSeek / Azure ChatGPT
        final_body['messages'].append({"role": "system", "content": system_prompt})
        final_body['messages'].append({"role": "user", "content": user_prompt})

    elif 'contents' in final_body and isinstance(final_body['contents'], list):
        # Gemini (Google)
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        final_body['contents'].append({"parts": [{"text": full_prompt}]})

    elif 'prompt' in final_body and isinstance(final_body['prompt'], str):
        # Modelos simples baseados em prompt
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        final_body['prompt'] = full_prompt

    else:
        logger.warning(f"Formato de body_template não reconhecido para IA {ia_name}. Tentando fallback.")
        if not final_body:
            final_body = {"prompt": f"{system_prompt}\n\n{user_prompt}"}

    headers = {**headers_template}
    if endpoint_key:
        if "Authorization" not in headers:
            headers["Authorization"] = f"Bearer {endpoint_key}"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(endpoint_url, headers=headers, json=final_body)
            response.raise_for_status()
            response_data = response.json()

            # --- EXTRAÇÃO DA RESPOSTA POR TIPO DE IA ---
            if ia_name in ["OpenAI", "ChatGPT", "DeepSeek"]:
                return response_data.get('choices', [{}])[0].get('message', {}).get('content', '')

            elif ia_name == "Gemini":
                candidates = response_data.get('candidates', [])
                if candidates:
                    parts = candidates[0].get('content', {}).get('parts', [])
                    if parts:
                        return parts[0].get('text', '')
                return ""

            elif ia_name == "Copilot":
                return response_data.get('choices', [{}])[0].get('message', {}).get('content', '')

            else:
                logger.warning(f"IA '{ia_name}' não reconhecida. Tentando extração genérica.")
                return response_data.get('text', response_data.get('response', {}).get('text', str(response_data)))

    except httpx.HTTPStatusError as e:
        logger.error(f"Erro HTTP da IA ({ia_name}): {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"Erro da IA ({ia_name}): {e.response.text}")

    except httpx.RequestError as e:
        logger.error(f"Erro de rede na IA ({ia_name}): {e}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Falha ao conectar com IA ({ia_name}).")

    except json.JSONDecodeError:
        logger.error(f"Resposta inválida da IA ({ia_name}) — não é JSON.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Resposta inválida da IA ({ia_name}).")

    except Exception as e:
        logger.error(f"Erro inesperado na IA ({ia_name}): {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro inesperado na IA ({ia_name}).")
