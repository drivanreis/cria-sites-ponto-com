// src/api/users.ts

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

// Interface para um usuário (completa, incluindo campos que podem vir da API)
export interface User {
  id: string; // Ou number, dependendo da sua API
  username: string;
  email: string;
  is_active: boolean;
  is_admin: boolean; // Supondo que a API retorne isso para diferenciar
  // Adicione outros campos conforme a estrutura do seu User e AdminUser na API
}

// Helper para lidar com a autenticação (token)
const getAuthHeaders = () => {
  const token = localStorage.getItem('accessToken');
  return {
    'ngrok-skip-browser-warning': 'true',
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` }), // Adiciona o token se existir
  };
};

// Funções para Usuários Comuns e Admin Users
// ------------------------------------------

// Obter todos os usuários (Admin)
export const getAllUsers = async (): Promise<User[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/users/`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Erro ao buscar usuários: ${response.status} ${response.statusText}`);
    }
    return response.json();
  } catch (error) {
    console.error("Erro em getAllUsers:", error);
    throw error;
  }
};

// Obter um usuário específico por ID (Admin)
export const getUserById = async (userId: string): Promise<User> => {
  try {
    const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Erro ao buscar usuário ${userId}: ${response.status} ${response.statusText}`);
    }
    return response.json();
  } catch (error) {
    console.error(`Erro em getUserById (${userId}):`, error);
    throw error;
  }
};

// Atualizar um usuário existente (Admin)
export const updateUser = async (userId: string, userData: Partial<User>): Promise<User> => {
  try {
    const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Erro ao atualizar usuário ${userId}: ${response.status} ${response.statusText}`);
    }
    return response.json();
  } catch (error) {
    console.error(`Erro em updateUser (${userId}):`, error);
    throw error;
  }
};

// Deletar um usuário existente (Admin)
export const deleteUser = async (userId: string): Promise<{ message: string }> => {
  try {
    const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Erro ao deletar usuário ${userId}: ${response.status} ${response.statusText}`);
    }
    // A API pode retornar um corpo vazio ou uma mensagem, ajuste conforme necessário
    return { message: `Usuário ${userId} deletado com sucesso.` };
  } catch (error) {
    console.error(`Erro em deleteUser (${userId}):`, error);
    throw error;
  }
};

// Criar um novo Admin User (somente para Admins)
export const createAdminUser = async (userData: Omit<User, 'id' | 'is_active' | 'is_admin'>): Promise<User> => {
  try {
    const response = await fetch(`${API_BASE_URL}/admin_users/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Erro ao criar admin user: ${response.status} ${response.statusText}`);
    }
    return response.json();
  } catch (error) {
    console.error("Erro em createAdminUser:", error);
    throw error;
  }
};

// Obter todos os usuários admin (Admin)
export const getAllAdminUsers = async (): Promise<User[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/admin_users/`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Erro ao buscar admin users: ${response.status} ${response.statusText}`);
    }
    return response.json();
  } catch (error) {
    console.error("Erro em getAllAdminUsers:", error);
    throw error;
  }
};

// Obter o perfil do admin logado (Admin)
export const getOwnAdminProfile = async (): Promise<User> => {
  try {
    const response = await fetch(`${API_BASE_URL}/admin_users/me`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Erro ao buscar perfil admin: ${response.status} ${response.statusText}`);
    }
    return response.json();
  } catch (error) {
    console.error("Erro em getOwnAdminProfile:", error);
    throw error;
  }
};

// Obter um admin user específico por ID (Admin)
export const getAdminUserById = async (adminUserId: string): Promise<User> => {
  try {
    const response = await fetch(`${API_BASE_URL}/admin_users/${adminUserId}`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Erro ao buscar admin user ${adminUserId}: ${response.status} ${response.statusText}`);
    }
    return response.json();
  } catch (error) {
    console.error(`Erro em getAdminUserById (${adminUserId}):`, error);
    throw error;
  }
};

// Atualizar um admin user existente (Admin)
export const updateAdminUser = async (adminUserId: string, userData: Partial<User>): Promise<User> => {
  try {
    const response = await fetch(`${API_BASE_URL}/admin_users/${adminUserId}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Erro ao atualizar admin user ${adminUserId}: ${response.status} ${response.statusText}`);
    }
    return response.json();
  } catch (error) {
    console.error(`Erro em updateAdminUser (${adminUserId}):`, error);
    throw error;
  }
};

// Deletar um admin user existente (Admin)
export const deleteAdminUser = async (adminUserId: string): Promise<{ message: string }> => {
  try {
    const response = await fetch(`${API_BASE_URL}/admin_users/${adminUserId}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Erro ao deletar admin user ${adminUserId}: ${response.status} ${response.statusText}`);
    }
    return { message: `Admin user ${adminUserId} deletado com sucesso.` };
  } catch (error) {
    console.error(`Erro em deleteAdminUser (${adminUserId}):`, error);
    throw error;
  }
};

// Obter o próprio perfil do usuário logado (GET /users/me)
export const getUserProfile = async (): Promise<User> => {
  const response = await fetch(`${API_BASE_URL}/users/me`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Erro ao buscar perfil');
  }

  return response.json();
};

// Atualizar o próprio perfil (PUT /users/me)
export const updateUserProfile = async (
  data: Partial<User>
): Promise<User> => {
  const response = await fetch(`${API_BASE_URL}/users/me`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Erro ao atualizar perfil');
  }

  return response.json();
};
