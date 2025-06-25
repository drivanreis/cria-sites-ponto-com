// src/api/employees.ts

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

// Interface para um funcionário (Employee)
export interface Employee {
  id: string; // Ou number, dependendo da sua API
  name: string;
  email: string;
  is_active: boolean;
  // Adicione outros campos conforme a estrutura do seu Employee na API
}

// Helper para obter os headers de autenticação
const getAuthHeaders = () => {
  const token = localStorage.getItem('accessToken');
  return {
    'ngrok-skip-browser-warning': 'true',
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` }),
  };
};

// Funções para gerenciamento de Employees
// ------------------------------------------

// Obter todos os funcionários
export const getAllEmployees = async (): Promise<Employee[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/employees/`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Erro ao buscar funcionários: ${response.status} ${response.statusText}`);
    }
    return response.json();
  } catch (error) {
    console.error("Erro em getAllEmployees:", error);
    throw error;
  }
};

// Obter um funcionário específico por ID
export const getEmployeeById = async (employeeId: string): Promise<Employee> => {
  try {
    const response = await fetch(`${API_BASE_URL}/employees/${employeeId}`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Erro ao buscar funcionário ${employeeId}: ${response.status} ${response.statusText}`);
    }
    return response.json();
  } catch (error) {
    console.error(`Erro em getEmployeeById (${employeeId}):`, error);
    throw error;
  }
};

// Atualizar um funcionário existente
export const updateEmployee = async (employeeId: string, employeeData: Partial<Employee>): Promise<Employee> => {
  try {
    const response = await fetch(`${API_BASE_URL}/employees/${employeeId}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(employeeData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Erro ao atualizar funcionário ${employeeId}: ${response.status} ${response.statusText}`);
    }
    return response.json();
  } catch (error) {
    console.error(`Erro em updateEmployee (${employeeId}):`, error);
    throw error;
  }
};

// Testar todas as conexões de IA (API: GET /employees/test_ai_connections)
export const testAllAiConnections = async (): Promise<unknown> => { // O tipo de retorno pode ser mais específico
  try {
    const response = await fetch(`${API_BASE_URL}/employees/test_ai_connections`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Erro ao testar conexões AI: ${response.status} ${response.statusText}`);
    }
    return response.json();
  } catch (error) {
    console.error("Erro em testAllAiConnections:", error);
    throw error;
  }
};

// Observação: As rotas para POST (criar) e DELETE (deletar) funcionários
// não foram explicitamente mostradas na sua Swagger UI para `Employees`.
// Se elas existirem, você adicionaria funções aqui:
/*
export const createEmployee = async (employeeData: Omit<Employee, 'id'>): Promise<Employee> => { ... };
export const deleteEmployee = async (employeeId: string): Promise<unknown> => { ... };
*/