// frontend/src/contexts/AdminAuthContext.ts
import { createContext } from 'react';

interface AdminAuthContextType {
  isAuthenticated: boolean;
  userRole: 'admin' | null;
  login: (token: string) => void;
  logout: () => void;
}

export const AdminAuthContext = createContext<AdminAuthContextType | undefined>(undefined);
