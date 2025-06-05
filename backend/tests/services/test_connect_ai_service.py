import pytest
import httpx
import json
from fastapi import HTTPException, status
from src.services.connect_ai_service import call_external_ai_api

# --- Testes para a função call_external_ai_api ---

# Teste 1: Verificação da injeção do prompt_content para OpenAI-like (messages)
@pytest.mark.asyncio
async def test_call_external_ai_api_openai_body_injection(mocker):
    endpoint_url = "http://openai.api/v1/chat/completions"
    endpoint_key = "test_openai_key"
    headers_template = {"Authorization": f"Bearer {endpoint_key}"}
    body_template = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "PLACEHOLDER_PROMPT"}]
    }
    prompt_content = "Olá, como você está?"
    ia_name = "OpenAI"

    mock_response_json = {"choices": [{"message": {"content": "Estou bem, obrigado!"}}]}
    # Mockando a resposta HTTPX para um sucesso
    mocker.patch('httpx.AsyncClient.post', return_value=httpx.Response(
        status_code=200,
        json=mock_response_json
    ))

    response = await call_external_ai_api(
        endpoint_url, endpoint_key, headers_template, body_template, prompt_content, ia_name
    )

    assert response == "Estou bem, obrigado!"
    # Verificar se o post foi chamado com o corpo correto
    httpx.AsyncClient.post.assert_called_once()
    called_args, called_kwargs = httpx.AsyncClient.post.call_args
    assert called_kwargs['json']['messages'][0]['content'] == prompt_content
    assert called_kwargs['headers']['Authorization'] == f"Bearer {endpoint_key}"

# Teste 2: Verificação da injeção do prompt_content para Gemini-like (contents)
@pytest.mark.asyncio
async def test_call_external_ai_api_gemini_body_injection(mocker):
    endpoint_url = "http://gemini.api/v1beta/models/gemini-pro:generateContent"
    endpoint_key = "test_gemini_key"
    headers_template = {"x-goog-api-key": endpoint_key}
    body_template = {
        "contents": [{"role": "user", "parts": [{"text": "PLACEHOLDER_PROMPT"}]}]
    }
    prompt_content = "Qual é a capital do Brasil?"
    ia_name = "Gemini"

    mock_response_json = {"candidates": [{"content": {"parts": [{"text": "Brasília"}]}}]}
    mocker.patch('httpx.AsyncClient.post', return_value=httpx.Response(
        status_code=200,
        json=mock_response_json
    ))

    response = await call_external_ai_api(
        endpoint_url, endpoint_key, headers_template, body_template, prompt_content, ia_name
    )

    assert response == "Brasília"
    httpx.AsyncClient.post.assert_called_once()
    called_args, called_kwargs = httpx.AsyncClient.post.call_args
    assert called_kwargs['json']['contents'][0]['parts'][0]['text'] == prompt_content
    assert called_kwargs['headers']['x-goog-api-key'] == endpoint_key

# Teste 3: Chamada bem-sucedida com resposta genérica (sem estrutura específica de 'messages' ou 'contents')
@pytest.mark.asyncio
async def test_call_external_ai_api_generic_success(mocker):
    endpoint_url = "http://generic.api/generate"
    endpoint_key = "test_generic_key"
    headers_template = {"Custom-Header": "value"}
    body_template = {"input_text": "PROMPT"}
    prompt_content = "Me conte uma piada."
    ia_name = "GenericAI"

    mock_response_json = {"response": "Por que o tomate não é um bom detetive? Porque ele sempre Ketch-up!"}
    mocker.patch('httpx.AsyncClient.post', return_value=httpx.Response(
        status_code=200,
        json=mock_response_json
    ))

    response = await call_external_ai_api(
        endpoint_url, endpoint_key, headers_template, body_template, prompt_content, ia_name
    )

    assert response == "Por que o tomate não é um bom detetive? Porque ele sempre Ketch-up!"
    httpx.AsyncClient.post.assert_called_once()
    called_args, called_kwargs = httpx.AsyncClient.post.call_args
    assert called_kwargs['json']['input_text'] == prompt_content # Verifica se o prompt foi injetado na key 'input_text'
    assert called_kwargs['headers']['Custom-Header'] == "value"

# Teste 4: Tratamento de erro HTTP 400 (Bad Request)
@pytest.mark.asyncio
async def test_call_external_ai_api_http_400_error(mocker):
    endpoint_url = "http://error.api/bad_request"
    endpoint_key = "test_key"
    headers_template = {}
    body_template = {"prompt": "test"}
    prompt_content = "bad request"
    ia_name = "TestAI"

    mocker.patch('httpx.AsyncClient.post', return_value=httpx.Response(
        status_code=400,
        text="Invalid input data"
    ))

    with pytest.raises(HTTPException) as exc_info:
        await call_external_ai_api(
            endpoint_url, endpoint_key, headers_template, body_template, prompt_content, ia_name
        )
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid input data" in exc_info.value.detail

# Teste 5: Tratamento de erro HTTP 500 (Internal Server Error)
@pytest.mark.asyncio
async def test_call_external_ai_api_http_500_error(mocker):
    endpoint_url = "http://error.api/internal_error"
    endpoint_key = "test_key"
    headers_template = {}
    body_template = {"prompt": "test"}
    prompt_content = "server error"
    ia_name = "TestAI"

    mocker.patch('httpx.AsyncClient.post', return_value=httpx.Response(
        status_code=500,
        text="Internal server error at AI"
    ))

    with pytest.raises(HTTPException) as exc_info:
        await call_external_ai_api(
            endpoint_url, endpoint_key, headers_template, body_template, prompt_content, ia_name
        )
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Internal server error at AI" in exc_info.value.detail

# Teste 6: Tratamento de erro de rede (httpx.RequestError)
@pytest.mark.asyncio
async def test_call_external_ai_api_network_error(mocker):
    endpoint_url = "http://unreachable.api/test"
    endpoint_key = "test_key"
    headers_template = {}
    body_template = {"prompt": "test"}
    prompt_content = "network error"
    ia_name = "TestAI"

    mocker.patch('httpx.AsyncClient.post', side_effect=httpx.RequestError("Could not connect"))

    with pytest.raises(HTTPException) as exc_info:
        await call_external_ai_api(
            endpoint_url, endpoint_key, headers_template, body_template, prompt_content, ia_name
        )
    assert exc_info.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert "Não foi possível conectar com a API de IA" in exc_info.value.detail

# Teste 7: Tratamento de resposta JSON inválida
@pytest.mark.asyncio
async def test_call_external_ai_api_invalid_json_response(mocker):
    endpoint_url = "http://invalid.api/json"
    endpoint_key = "test_key"
    headers_template = {}
    body_template = {"prompt": "test"}
    prompt_content = "invalid json"
    ia_name = "TestAI"

    mocker.patch('httpx.AsyncClient.post', return_value=httpx.Response(
        status_code=200,
        text="This is not a JSON response"
    ))

    with pytest.raises(HTTPException) as exc_info:
        await call_external_ai_api(
            endpoint_url, endpoint_key, headers_template, body_template, prompt_content, ia_name
        )
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Resposta inválida da API de IA (TestAI). Não é um JSON." in exc_info.value.detail

# Teste 8: Resposta de IA com estrutura 'text'
@pytest.mark.asyncio
async def test_call_external_ai_api_response_with_text_key(mocker):
    endpoint_url = "http://another.ai/api"
    endpoint_key = "test_key"
    headers_template = {}
    body_template = {"query": "test"}
    prompt_content = "text response"
    ia_name = "AnotherAI"

    mock_response_json = {"text": "This is a simple text response."}
    mocker.patch('httpx.AsyncClient.post', return_value=httpx.Response(
        status_code=200,
        json=mock_response_json
    ))

    response = await call_external_ai_api(
        endpoint_url, endpoint_key, headers_template, body_template, prompt_content, ia_name
    )
    assert response == "This is a simple text response."

# Teste 9: Resposta de IA com estrutura aninhada 'response' -> 'text'
@pytest.mark.asyncio
async def test_call_external_ai_api_nested_response_text(mocker):
    endpoint_url = "http://nested.ai/api"
    endpoint_key = "test_key"
    headers_template = {}
    body_template = {"data": "test"}
    prompt_content = "nested text response"
    ia_name = "NestedAI"

    mock_response_json = {"data": {"response": {"text": "This is a nested text response."}}}
    mocker.patch('httpx.AsyncClient.post', return_value=httpx.Response(
        status_code=200,
        json=mock_response_json
    ))

    response = await call_external_ai_api(
        endpoint_url, endpoint_key, headers_template, body_template, prompt_content, ia_name
    )
    assert response == "This is a nested text response."

# Teste 10: Retorno de string se o JSON não tiver uma estrutura de resposta conhecida
@pytest.mark.asyncio
async def test_call_external_ai_api_unrecognized_structure(mocker):
    endpoint_url = "http://unknown.ai/api"
    endpoint_key = "test_key"
    headers_template = {}
    body_template = {"q": "test"}
    prompt_content = "unrecognized structure"
    ia_name = "UnknownAI"

    mock_response_json = {"some_other_key": "some_value", "data_field": "final_data"}
    mocker.patch('httpx.AsyncClient.post', return_value=httpx.Response(
        status_code=200,
        json=mock_response_json
    ))

    response = await call_external_ai_api(
        endpoint_url, endpoint_key, headers_template, body_template, prompt_content, ia_name
    )
    # Deve retornar a representação em string do JSON completo, pois não encontrou 'text' ou 'response'
    assert response == str(mock_response_json)

# Teste 11: Prompt content vazio (não deve causar erro)
@pytest.mark.asyncio
async def test_call_external_ai_api_empty_prompt_content(mocker):
    endpoint_url = "http://openai.api/v1/chat/completions"
    endpoint_key = "test_openai_key"
    headers_template = {"Authorization": f"Bearer {endpoint_key}"}
    body_template = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "PLACEHOLDER_PROMPT"}]
    }
    prompt_content = ""
    ia_name = "OpenAI"

    mock_response_json = {"choices": [{"message": {"content": "Ok."}}]}
    mocker.patch('httpx.AsyncClient.post', return_value=httpx.Response(
        status_code=200,
        json=mock_response_json
    ))

    response = await call_external_ai_api(
        endpoint_url, endpoint_key, headers_template, body_template, prompt_content, ia_name
    )

    assert response == "Ok."
    httpx.AsyncClient.post.assert_called_once()
    called_args, called_kwargs = httpx.AsyncClient.post.call_args
    assert called_kwargs['json']['messages'][0]['content'] == prompt_content