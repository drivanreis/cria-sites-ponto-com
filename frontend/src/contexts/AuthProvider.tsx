// frontend/src/contexts/AuthProvider.tsx

import React, { useEffect, useState } from 'react';
import { AuthContext } from './AuthContext';
import type { AuthContextType, AuthUser } from './AuthContext';
import type { ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

export const AuthProvider: React.FC<Props> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    const userData = localStorage.getItem('user');
    if (token && userData) {
      setAccessToken(token);
      setUser(JSON.parse(userData));
    }
  }, []);

  const login = (token: string) => {
    try {
      const payload = JSON.parse(atob(token.split('.')[1])); // Decodifica o JWT
      const newUser: AuthUser = {
        id: payload.sub,
        username: payload.username,
        email: payload.email,
        is_admin: payload.is_admin,
      };
      setAccessToken(token);
      setUser(newUser);
      localStorage.setItem('accessToken', token);
      localStorage.setItem('user', JSON.stringify(newUser));
    } catch (err) {
      console.error('Erro ao decodificar o token JWT:', err);
    }
  };

  const logout = () => {
    setAccessToken(null);
    setUser(null);
    localStorage.removeItem('accessToken');
    localStorage.removeItem('user');
  };

  const value: AuthContextType = {
    user,
    accessToken,
    login,
    logout,
    isAuthenticated: !!user,
    userRole: user?.is_admin ? 'admin' : 'user',
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
