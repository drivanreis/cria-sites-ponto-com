// src/api/auth.ts

// Usamos import.meta.env.VITE_API_BASE_URL para acessar a variável de ambiente definida no .env
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

interface LoginResponse {
  access_token: string;
  token_type: string;
  // Adicione outros campos da resposta de login se houver, ex: user_id, user_role
}

interface LoginError {
  detail: string;
}

export const loginUser = async (username: string, password: string): Promise<LoginResponse> => {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);

  try {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'ngrok-skip-browser-warning': 'true', // Mantém o cabeçalho para ngrok
        'Content-Type': 'application/x-www-form-urlencoded', // A API de login espera este content-type para form-data
      },
      body: formData.toString(), // Envia os dados do formulário como string
    });

    if (!response.ok) {
      const errorData: LoginError = await response.json();
      throw new Error(errorData.detail || `Erro HTTP: ${response.status} ${response.statusText}`);
    }

    const data: LoginResponse = await response.json();
    return data;
  } catch (error) {
    console.error("Erro ao fazer login:", error);
    throw error;
  }
};

// Futuramente, você pode adicionar uma função para logout se sua API tiver uma rota de logout,
// ou simplesmente para limpar o token do frontend.
export const logoutUser = () => {
  localStorage.removeItem('accessToken'); // Remove o token do armazenamento local
  // Poderia também invalidar o token no backend se houver uma rota para isso
};