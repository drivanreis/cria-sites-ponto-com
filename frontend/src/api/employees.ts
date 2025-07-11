// frontend/src/api/employees.ts

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

// Interface para um funcionário (Employee)
export interface Employee {
  id: string; // Ou number, dependendo da sua API
  name: string;
  email: string;
  is_active: boolean;
  // Adicione outros campos conforme a estrutura do seu Employee na API
}

// ✅ IMPORTE A FUNÇÃO getAuthHeaders DO MÓDULO DE UTILITÁRIOS:
import { getAuthHeaders } from '../utils/getAuthHeaders';

// Funções para gerenciamento de Employees
// ------------------------------------------

// Obter todos os funcionários
export const getAllEmployees = async (): Promise<Employee[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/employees/`, {
      method: 'GET',
      // ✅ CORREÇÃO AQUI: Use o getAuthHeaders global com o papel 'admin'
      headers: getAuthHeaders('admin'),
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
      // ✅ CORREÇÃO AQUI: Use o getAuthHeaders global com o papel 'admin'
      headers: getAuthHeaders('admin'),
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
      // ✅ CORREÇÃO AQUI: Use o getAuthHeaders global com o papel 'admin'
      headers: getAuthHeaders('admin'),
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
      // ✅ CORREÇÃO AQUI: Use o getAuthHeaders global com o papel 'admin'
      headers: getAuthHeaders('admin'),
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
// não existem!
// A aplicação não funciona com mais ou menos funcionários,
// apenas com os que já estão cadastrados no banco de dados.
// Portanto, não implementamos essas funções.