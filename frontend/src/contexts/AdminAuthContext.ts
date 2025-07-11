// File: frontend/src/contexts/AdminAuthContext.ts

import { createContext } from 'react';

export interface AdminAuthContextType {
  isAuthenticated: boolean;
  isLoading: boolean; // ✅ Agora incluso no tipo
  userRole: 'admin' | null;
  login: (token: string) => void;
  logout: () => void;
}

// Utiliza sessionStorage em vez de localStorage para login temporário
export const AdminAuthContext = createContext<AdminAuthContextType | undefined>(undefined);
