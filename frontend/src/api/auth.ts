// File: frontend/src/api/auth.ts

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

interface LoginResponse {
  access_token: string;
  token_type: string;
}

interface LoginError {
  detail: string;
}

// Login do ADMIN
export const loginAdmin = async (username: string, password: string): Promise<LoginResponse> => {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);

  const response = await fetch(`${API_BASE_URL}/auth/login/admin`, {
    method: 'POST',
    headers: {
      'ngrok-skip-browser-warning': 'true',
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData.toString(),
  });

  if (!response.ok) {
    const errorData: LoginError = await response.json();
    throw new Error(errorData.detail || `Erro HTTP: ${response.status} ${response.statusText}`);
  }

  const data: LoginResponse = await response.json();
  // ✅ CORREÇÃO APLICADA AQUI: Chave alterada para 'adminAccessToken'
  sessionStorage.setItem('adminAccessToken', data.access_token);
  return data;
};

// Login do USUÁRIO comum (email ou telefone)
export const loginUser = async (email: string, password: string): Promise<LoginResponse> => {
  const formData = new URLSearchParams();
  formData.append('email', email);
  formData.append('password', password);

  try {
    const response = await fetch(`${API_BASE_URL}/auth/login/user`, {
      method: 'POST',
      headers: {
        'ngrok-skip-browser-warning': 'true',
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData.toString(),
    });

    if (!response.ok) {
      const errorData: LoginError = await response.json();
      throw new Error(errorData.detail || `Erro HTTP: ${response.status} ${response.statusText}`);
    }

    const data: LoginResponse = await response.json();
    // ✅ Este está correto para o usuário comum e corresponde ao AuthProvider
    localStorage.setItem('accessToken', data.access_token); 
    return data;
  } catch (error) {
    console.error("Erro ao fazer login USER:", error);
    throw error;
  }
};

export const logoutUser = () => {
  localStorage.removeItem('accessToken');
  // Se você tiver informações de usuário armazenadas, remova-as também
  localStorage.removeItem('user'); 
};