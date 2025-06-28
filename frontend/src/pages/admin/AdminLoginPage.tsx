// frontend/src/contexts/AuthContext.tsx

import React, { createContext, useContext, useEffect, useState } from 'react';
import { loginAdmin as apiLoginAdmin, loginUser as apiLoginUser, logoutUser } from '../api/auth';

interface AuthContextType {
  isAuthenticated: boolean;
  userRole: 'admin' | 'user' | null;
  loginUser: (email: string, password: string) => Promise<void>;
  loginAdmin: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userRole, setUserRole] = useState<'admin' | 'user' | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    const role = localStorage.getItem('userRole') as 'admin' | 'user' | null;
    if (token && role) {
      setIsAuthenticated(true);
      setUserRole(role);
    }
  }, []);

  const loginUser = async (email: string, password: string) => {
    const data = await apiLoginUser(email, password);
    localStorage.setItem('accessToken', data.access_token);
    localStorage.setItem('userRole', 'user');
    setIsAuthenticated(true);
    setUserRole('user');
  };

  const loginAdmin = async (username: string, password: string) => {
    const data = await apiLoginAdmin(username, password);
    localStorage.setItem('accessToken', data.access_token);
    localStorage.setItem('userRole', 'admin');
    setIsAuthenticated(true);
    setUserRole('admin');
  };

  const logout = () => {
    logoutUser();
    localStorage.removeItem('userRole');
    setIsAuthenticated(false);
    setUserRole(null);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, userRole, loginUser, loginAdmin, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider');
  }
  return context;
};
