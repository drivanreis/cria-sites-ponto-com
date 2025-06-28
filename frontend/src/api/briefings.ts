// frontend/src/api/briefings.ts

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

type BriefingContentValue = string | number | boolean | null | BriefingContentValue[] | { [key: string]: BriefingContentValue };

export interface Briefing {
  id: string;
  title: string;
  status: string;
  content?: Record<string, BriefingContentValue>;
  development_roteiro?: Record<string, BriefingContentValue>;
  creation_date?: string;
  update_date?: string;
  last_edited_by?: string;
}

export interface BriefingChatMessage {
  sender_type: string;
  message_content: string;
  timestamp: string;
}

export interface BriefingWithHistory extends Briefing {
  conversation_history: BriefingChatMessage[];
}

const getAuthHeaders = () => {
  const token = localStorage.getItem('accessToken');
  return {
    'ngrok-skip-browser-warning': 'true',
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
  };
};

// Criar novo briefing (POST /briefings/)
export const createBriefing = async (briefingData: Partial<Briefing>): Promise<Briefing> => {
  const response = await fetch(`${API_BASE_URL}/briefings/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(briefingData),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Erro ao criar briefing.');
  }

  return response.json();
};

// Listar todos os briefings do usuário (GET /briefings/)
export const getBriefings = async (): Promise<Briefing[]> => {
  const response = await fetch(`${API_BASE_URL}/briefings/`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Erro ao listar briefings.');
  }

  return response.json();
};

// Obter briefing com histórico (GET /briefings/{id})
export const getBriefingById = async (id: string): Promise<BriefingWithHistory> => {
  const response = await fetch(`${API_BASE_URL}/briefings/${id}`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Erro ao buscar briefing.');
  }

  return response.json();
};

// Atualizar briefing (PUT /briefings/{id})
export const updateBriefing = async (id: string, data: Partial<Briefing>): Promise<Briefing> => {
  const response = await fetch(`${API_BASE_URL}/briefings/${id}`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Erro ao atualizar briefing.');
  }

  return response.json();
};

// Deletar briefing (DELETE /briefings/{id})
export const deleteBriefing = async (id: string): Promise<{ message: string }> => {
  const response = await fetch(`${API_BASE_URL}/briefings/${id}`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Erro ao deletar briefing.');
  }

  return { message: `Briefing ${id} deletado com sucesso.` };
};

// Enviar mensagem para funcionário (POST /briefings/{id}/chat/{employee_name})
export const chatWithEmployee = async (
  briefingId: string,
  employeeName: string,
  message: string
): Promise<BriefingWithHistory> => {
  const response = await fetch(`${API_BASE_URL}/briefings/${briefingId}/chat/${employeeName}`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ user_message: message, employee_name: employeeName }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Erro ao enviar mensagem.');
  }

  return response.json();
};

// Compilar briefing (POST /briefings/{id}/compile)
export const compileBriefing = async (briefingId: string): Promise<Record<string, BriefingContentValue>> => {
  const response = await fetch(`${API_BASE_URL}/briefings/${briefingId}/compile`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Erro ao compilar briefing.');
  }

  return response.json();
};
