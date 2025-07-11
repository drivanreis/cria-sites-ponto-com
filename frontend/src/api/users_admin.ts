// File: frontend/src/api/users_admin.ts

/**
 * Módulo exclusivo para Admin Users.
 * Mantém tipagens e funções REST alinhadas ao backend (/admin_users/*).
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

import { getAuthHeaders } from '../utils/getAuthHeaders';

// ---------- Tipagens ----------
export type AdminUser = {
  id: string;
  username: string;
  creation_date: string;
  last_login?: string;
};

export type CreateAdminUser = {
  username: string;
  password: string;
};

// ---------- Funções REST ----------

// GET /admin_users/
export const getAllAdminUsers = async (): Promise<AdminUser[]> => {
  const response = await fetch(`${API_BASE_URL}/admin_users/`, {
    method: 'GET',
    headers: getAuthHeaders('admin'),
  });
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `Erro HTTP: ${response.status} ${response.statusText}`);
  }
  return response.json();
};

// GET /admin_users/me
export const getOwnAdminProfile = async (): Promise<AdminUser> => {
  const response = await fetch(`${API_BASE_URL}/admin_users/me`, {
    method: 'GET',
    headers: getAuthHeaders('admin'),
  });
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `Erro HTTP: ${response.status} ${response.statusText}`);
  }
  return response.json();
};

// GET /admin_users/{id}
export const getAdminUserById = async (adminUserId: string): Promise<AdminUser> => {
  const response = await fetch(`${API_BASE_URL}/admin_users/${adminUserId}`, {
    method: 'GET',
    headers: getAuthHeaders('admin'),
  });
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `Erro HTTP: ${response.status} ${response.statusText}`);
  }
  return response.json();
};

// POST /admin_users/
export const createAdminUser = async (
  data: CreateAdminUser
): Promise<AdminUser> => {
  const response = await fetch(`${API_BASE_URL}/admin_users/`, {
    method: 'POST',
    headers: getAuthHeaders('admin'),
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `Erro HTTP: ${response.status} ${response.statusText}`);
  }
  return response.json();
};

// PUT /admin_users/{id}
export const updateAdminUser = async (
  adminUserId: string,
  data: Partial<CreateAdminUser>
): Promise<AdminUser> => {
  const response = await fetch(`${API_BASE_URL}/admin_users/${adminUserId}`, {
    method: 'PUT',
    headers: getAuthHeaders('admin'),
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `Erro HTTP: ${response.status} ${response.statusText}`);
  }
  return response.json();
};

// DELETE /admin_users/{id}
export const deleteAdminUser = async (
  adminUserId: string
): Promise<{ message: string }> => {
  const response = await fetch(`${API_BASE_URL}/admin_users/${adminUserId}`, {
    method: 'DELETE',
    headers: getAuthHeaders('admin'),
  });
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `Erro HTTP: ${response.status} ${response.statusText}`);
  }
  return { message: `Admin user ${adminUserId} deletado com sucesso.` };
};
