# backend/src/models/__init__.py

# Importe todos os seus modelos aqui para garantir que eles sejam registrados com Base.metadata
from .user_models import User
from .admin_user_models import AdminUser
from .employee_models import Employee
from .briefing_models import Briefing
from .conversation_history_models import ConversationHistory
# Adicione aqui quaisquer outros modelos que você possa ter (ex: other_model.py)
# from .other_model import OtherModel