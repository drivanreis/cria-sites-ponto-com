// frontend/src/contexts/AdminAuthProvider.tsx
import React, { useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import { AdminAuthContext } from './AdminAuthContext';

interface AdminAuthProviderProps {
  children: ReactNode;
}

export const AdminAuthProvider: React.FC<AdminAuthProviderProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userRole, setUserRole] = useState<'admin' | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('admin_token');
    if (token) {
      setIsAuthenticated(true);
      setUserRole('admin');
    }
  }, []);

  const login = (token: string) => {
    localStorage.setItem('admin_token', token);
    setIsAuthenticated(true);
    setUserRole('admin');
  };

  const logout = () => {
    localStorage.removeItem('admin_token');
    setIsAuthenticated(false);
    setUserRole(null);
  };

  return (
    <AdminAuthContext.Provider value={{ isAuthenticated, userRole, login, logout }}>
      {children}
    </AdminAuthContext.Provider>
  );
};
