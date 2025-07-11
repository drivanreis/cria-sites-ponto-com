// File: frontend/src/contexts/AdminAuthProvider.tsx

import React, {
  useState,
  useCallback,
  useMemo,
  useEffect,
} from 'react';
import type { ReactNode } from 'react';
import { AdminAuthContext } from './AdminAuthContext';

interface AdminAuthProviderProps {
  children: ReactNode;
}

export const AdminAuthProvider: React.FC<AdminAuthProviderProps> = ({ children }) => {
  const [adminAccessToken, setAdminAccessToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = sessionStorage.getItem('adminAccessToken');
    if (token) {
      setAdminAccessToken(token);
    }
    setIsLoading(false);
  }, []);

  const isAuthenticated = useMemo(() => !!adminAccessToken, [adminAccessToken]);

  const userRole = useMemo<'admin' | null>(
    () => (adminAccessToken ? 'admin' : null),
    [adminAccessToken]
  );

  const login = useCallback((token: string) => {
    sessionStorage.setItem('adminAccessToken', token);
    setAdminAccessToken(token);
  }, []);

  const logout = useCallback(() => {
    sessionStorage.removeItem('adminAccessToken');
    setAdminAccessToken(null);
  }, []);

  const value = useMemo(
    () => ({
      isAuthenticated,
      isLoading,
      userRole,
      login,
      logout,
    }),
    [isAuthenticated, isLoading, userRole, login, logout]
  );

  return (
    <AdminAuthContext.Provider value={value}>
      {children}
    </AdminAuthContext.Provider>
  );
};
