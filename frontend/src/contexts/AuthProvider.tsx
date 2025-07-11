// File: frontend/src/contexts/AuthProvider.tsx

import React, { useEffect, useState, useCallback, useMemo } from 'react'; // Adicionado useCallback e useMemo
import { AuthContext } from './AuthContext';
import type { AuthContextType, AuthUser } from './AuthContext';
import type { ReactNode } from 'react';
import { useNavigate } from 'react-router-dom'; // ✅ necessário para redirecionar

interface Props {
  children: ReactNode;
}

export const AuthProvider: React.FC<Props> = ({ children }) => {
  // Inicialização lazy do estado para ler do localStorage apenas uma vez na montagem
  const [user, setUser] = useState<AuthUser | null>(() => {
    try {
      const userData = localStorage.getItem('user');
      return userData ? JSON.parse(userData) : null;
    } catch (e) {
      console.error("Erro ao carregar usuário do localStorage na inicialização:", e);
      return null;
    }
  });
  const [accessToken, setAccessToken] = useState<string | null>(() => localStorage.getItem('accessToken'));
  const navigate = useNavigate(); // ✅ hook de navegação

  useEffect(() => {
    // A lógica de useEffect para carregar o token e usuário do localStorage é mantida
    // mas a inicialização do useState acima já lida com a carga inicial.
    // Este useEffect pode ser útil para revalidação ou outros efeitos secundários.
    const token = localStorage.getItem('accessToken');
    const userData = localStorage.getItem('user');
    if (token && userData) {
      // Verifica se os dados já foram carregados pelo useState inicial ou se precisam ser atualizados
      if (!accessToken || !user || accessToken !== token || JSON.stringify(user) !== userData) {
        setAccessToken(token);
        setUser(JSON.parse(userData));
      }
    }
  }, [accessToken, user]); // Dependências adicionadas para evitar loop se o estado for redefinido aqui

  // Memoiza a função login com useCallback
  const login = useCallback((token: string) => {
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
      // Opcional: Limpar token e usuário se houver erro de decodificação
      setAccessToken(null);
      setUser(null);
      localStorage.removeItem('accessToken');
      localStorage.removeItem('user');
    }
  }, []); // login não tem dependências externas que mudam, então array vazio

  // Memoiza a função logout com useCallback
  const logout = useCallback(() => {
    setAccessToken(null);
    setUser(null);
    localStorage.removeItem('accessToken');
    localStorage.removeItem('user');
    navigate('/login'); // ✅ redireciona após logout
  }, [navigate]); // navigate é uma dependência que precisa ser listada para useCallback

  // Memoiza os valores derivados isAuthenticated e userRole com useMemo
  const isAuthenticated = useMemo(() => !!user && !!accessToken, [user, accessToken]);
  const userRole = useMemo(() => user?.is_admin ? 'admin' : 'user', [user]);

  // Memoiza o objeto 'value' inteiro com useMemo
  const value: AuthContextType = useMemo(() => ({
    user,
    accessToken,
    login,
    logout,
    isAuthenticated,
    userRole,
  }), [user, accessToken, login, logout, isAuthenticated, userRole]); // Todas as dependências devem ser listadas aqui

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};