// src/components/common/ProtectedRoute.tsx
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth'; // Supondo que você tenha um AuthContext

interface ProtectedRouteProps {
  children: React.ReactNode;
  adminOnly?: boolean;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, adminOnly }) => {
  const { isAuthenticated, userRole, loadingAuth } = useAuth(); // Assume que useAuth fornece isAuthenticated e userRole

  if (loadingAuth) {
    return <div>Carregando autenticação...</div>; // Ou um spinner/loader
  }

  if (!isAuthenticated) {
    // Redireciona para a página de login se não estiver autenticado
    return <Navigate to="/login" replace />;
  }

  if (adminOnly && userRole !== 'admin') {
    // Redireciona para algum lugar se não for admin mas a rota exige
    return <Navigate to="/dashboard" replace />; // Ou uma página de "Acesso Negado"
  }

  return <>{children}</>;
};

export default ProtectedRoute;