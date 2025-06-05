# File: backend/tests/services/test_compila_briefing_service.py

import pytest
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from unittest.mock import patch, MagicMock

from src.services.compila_briefing_service import compile_briefing_from_conversation
from src.cruds import briefing_cruds, conversation_history_cruds, employee_cruds
from src.schemas.briefing_schemas import BriefingCreate
from src.models.briefing_models import Briefing
from src.models.conversation_history_models import ConversationHistory
from src.models.employee_models import Employee
from tests.conftest import create_test_user, create_test_briefing, create_test_employee, create_test_conversation_history_entry

# Mock da função call_external_ai_api para evitar chamadas de rede reais
@pytest.fixture
def mock_call_external_ai_api():
    with patch('src.services.connect_ai_service.call_external_ai_api') as mock_func:
        yield mock_func

# Mock do character_service para isolar o teste do compila_briefing_service
@pytest.fixture
def mock_character_service():
    with patch('src.services.character_service.get_ai_response_for_character') as mock_func:
        yield mock_func

def test_compile_briefing_success_new_briefing(db_session_override: Session, mock_character_service):
    user = create_test_user(db_session_override, "Test User", "test_compile@example.com", "Password123!")
    employee_name = "Assistente de Palco"
    create_test_employee(db_session_override, sender_type=employee_name)

    # Simula um histórico de conversa que a IA usaria para compilar
    briefing_chat_title = f"Conversa com Entrevistador Pessoal (Usuário {user.id})"
    briefing_for_chat = create_test_briefing(db_session_override, user.id, briefing_chat_title)
    
    create_test_conversation_history_entry(db_session_override, briefing_for_chat.id, "user", "Olá, quero um site para vender bolos.")
    create_test_conversation_history_entry(db_session_override, briefing_for_chat.id, "Entrevistador Pessoal", "Ótimo! Qual o público-alvo?")
    create_test_conversation_history_entry(db_session_override, briefing_for_chat.id, "user", "Pessoas que gostam de doces, de 25 a 50 anos.")

    # A resposta simulada da IA já em formato JSON
    mock_character_service.return_value = """
    ```json
    {
        "titulo": "Site de Venda de Bolos",
        "objetivo": "Vender bolos online para clientes locais.",
        "publico_alvo": "Pessoas que gostam de doces, de 25 a 50 anos.",
        "funcionalidades": ["Catálogo de produtos", "Carrinho de compras", "Pagamento online"],
        "orcamento": "A ser definido"
    }
    ```
    """

    # Chama o serviço
    compiled_briefing = compile_briefing_from_conversation(db_session_override, user.id, employee_name)

    assert compiled_briefing is not None
    assert compiled_briefing.user_id == user.id
    assert compiled_briefing.title == f"Briefing Compilado por {employee_name} para Usuário {user.id}"
    assert compiled_briefing.status == "Pronto para Revisão"
    assert compiled_briefing.content == {
        "titulo": "Site de Venda de Bolos",
        "objetivo": "Vender bolos online para clientes locais.",
        "publico_alvo": "Pessoas que gostam de doces, de 25 a 50 anos.",
        "funcionalidades": ["Catálogo de produtos", "Carrinho de compras", "Pagamento online"],
        "orcamento": "A ser definido"
    }
    assert compiled_briefing.last_edited_by == "ai"
    assert compiled_briefing.update_date is not None

    # Verifica se um novo briefing foi criado no banco de dados
    briefing_in_db = db_session_override.query(Briefing).filter_by(id=compiled_briefing.id).first()
    assert briefing_in_db is not None
    assert briefing_in_db.content == compiled_briefing.content

def test_compile_briefing_success_existing_briefing(db_session_override: Session, mock_character_service):
    user = create_test_user(db_session_override, "Existing Briefing User", "exist.briefing@example.com", "Password123!")
    employee_name = "Assistente de Palco"
    create_test_employee(db_session_override, sender_type=employee_name)

    # Cria um briefing existente que será compilado
    existing_briefing_title = f"Briefing Compilado por {employee_name} para Usuário {user.id}"
    existing_briefing = create_test_briefing(db_session_override, user.id, existing_briefing_title, status="Em Construção", content=None)
    
    # Adiciona histórico de conversa para este briefing
    create_test_conversation_history_entry(db_session_override, existing_briefing.id, "user", "Qual o nome da empresa?")
    create_test_conversation_history_entry(db_session_override, existing_briefing.id, "Entrevistador Pessoal", "É 'Padaria do Zé'.")

    mock_character_service.return_value = """{"nome_empresa": "Padaria do Zé", "ramo": "Panificação"}"""

    compiled_briefing = compile_briefing_from_conversation(db_session_override, user.id, employee_name)

    assert compiled_briefing.id == existing_briefing.id
    assert compiled_briefing.status == "Pronto para Revisão"
    assert compiled_briefing.content == {"nome_empresa": "Padaria do Zé", "ramo": "Panificação"}
    assert compiled_briefing.last_edited_by == "ai"

    # Verifica se o briefing existente foi atualizado no banco de dados
    updated_briefing_in_db = db_session_override.query(Briefing).filter_by(id=existing_briefing.id).first()
    assert updated_briefing_in_db.content == compiled_briefing.content


def test_compile_briefing_no_conversation_history(db_session_override: Session, mock_character_service):
    user = create_test_user(db_session_override, "No History User", "no.history@example.com", "Password123!")
    employee_name = "Assistente de Palco"
    create_test_employee(db_session_override, sender_type=employee_name)

    # Não adiciona nenhum histórico de conversa para este briefing
    # A função irá tentar criar um briefing, mas não encontrará histórico associado.
    
    with pytest.raises(HTTPException) as exc_info:
        compile_briefing_from_conversation(db_session_override, user.id, employee_name)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Nenhum histórico de conversa encontrado" in exc_info.value.detail


def test_compile_briefing_employee_not_found(db_session_override: Session):
    user = create_test_user(db_session_override, "No Employee User", "no.employee@example.com", "Password123!")
    employee_name = "Personagem Inexistente"

    # Não cria o employee "Personagem Inexistente"

    # O character_service deve levantar uma HTTPException 404 se o employee não for encontrado.
    # No entanto, a lógica de `compile_briefing_from_conversation` primeiro tenta recuperar o briefing,
    # depois o histórico e SÓ ENTÃO chama o character_service.
    # Se não houver histórico, a exceção de histórico será levantada antes.
    # Para testar diretamente a falta do employee, precisaríamos de um histórico existente.
    # Para simplificar, vamos simular o cenário mais provável: o briefing é criado, mas a IA falha.

    briefing_chat_title = f"Conversa com Entrevistador Pessoal (Usuário {user.id})"
    briefing_for_chat = create_test_briefing(db_session_override, user.id, briefing_chat_title)
    create_test_conversation_history_entry(db_session_override, briefing_for_chat.id, "user", "Teste de mensagem.")
    
    # Mockando especificamente get_employee_by_name para simular a ausência do funcionário
    with patch('src.cruds.employee_cruds.get_employee_by_name', return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            compile_briefing_from_conversation(db_session_override, user.id, employee_name)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert f"Personagem '{employee_name}' não encontrado." in exc_info.value.detail


def test_compile_briefing_invalid_ai_response_json(db_session_override: Session, mock_character_service):
    user = create_test_user(db_session_override, "Invalid JSON User", "invalid.json@example.com", "Password123!")
    employee_name = "Assistente de Palco"
    create_test_employee(db_session_override, sender_type=employee_name)

    briefing_chat_title = f"Conversa com Entrevistador Pessoal (Usuário {user.id})"
    briefing_for_chat = create_test_briefing(db_session_override, user.id, briefing_chat_title)
    create_test_conversation_history_entry(db_session_override, briefing_for_chat.id, "user", "Qualquer coisa.")
    
    mock_character_service.return_value = "Isso não é JSON válido."

    with pytest.raises(HTTPException) as exc_info:
        compile_briefing_from_conversation(db_session_override, user.id, employee_name)

    assert exc_info.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "A IA retornou um formato de briefing inválido." in exc_info.value.detail


def test_compile_briefing_empty_ai_response(db_session_override: Session, mock_character_service):
    user = create_test_user(db_session_override, "Empty Response User", "empty.response@example.com", "Password123!")
    employee_name = "Assistente de Palco"
    create_test_employee(db_session_override, sender_type=employee_name)

    briefing_chat_title = f"Conversa com Entrevistador Pessoal (Usuário {user.id})"
    briefing_for_chat = create_test_briefing(db_session_override, user.id, briefing_chat_title)
    create_test_conversation_history_entry(db_session_override, briefing_for_chat.id, "user", "Mensagem.")
    
    mock_character_service.return_value = "" # Resposta vazia da IA

    with pytest.raises(HTTPException) as exc_info:
        compile_briefing_from_conversation(db_session_override, user.id, employee_name)

    assert exc_info.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "A IA retornou um formato de briefing inválido." in exc_info.value.detail # A falha na decodificação JSON será o erro primário aqui

def test_compile_briefing_internal_ai_error(db_session_override: Session, mock_character_service):
    user = create_test_user(db_session_override, "Internal AI Error User", "ai.error@example.com", "Password123!")
    employee_name = "Assistente de Palco"
    create_test_employee(db_session_override, sender_type=employee_name)

    briefing_chat_title = f"Conversa com Entrevistador Pessoal (Usuário {user.id})"
    briefing_for_chat = create_test_briefing(db_session_override, user.id, briefing_chat_title)
    create_test_conversation_history_entry(db_session_override, briefing_for_chat.id, "user", "Mensagem.")

    # Simula uma exceção interna no character_service (e, por extensão, na chamada à API externa)
    mock_character_service.side_effect = HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AI service is down")

    with pytest.raises(HTTPException) as exc_info:
        compile_briefing_from_conversation(db_session_override, user.id, employee_name)
    
    assert exc_info.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert "AI service is down" in exc_info.value.detail