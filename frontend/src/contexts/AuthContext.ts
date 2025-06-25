// frontend/src/contexts/AuthContext.ts

import { createContext } from 'react';

export interface AuthUser {
  id: string;
  username: string;
  email: string;
  is_admin: boolean;
}

export interface AuthContextType {
  user: AuthUser | null;
  accessToken: string | null;
  login: (token: string) => void;
  logout: () => void;
}

// 👇 Agora sim estamos exportando tudo corretamente
export const AuthContext = createContext<AuthContextType | undefined>(undefined);
