// frontend/src/components/common/ProtectedRoute.tsx
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { useAdminAuth } from '../../hooks/useAdminAuth';

interface ProtectedRouteProps {
  children: React.ReactNode;
  adminOnly?: boolean;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, adminOnly = false }) => {
  const location = useLocation();
  const isAdminRoute = location.pathname.startsWith('/admin');

  // Hooks devem sempre ser chamados, sem condicional
  const userAuth = useAuth();
  const adminAuth = useAdminAuth();

  // Decide qual contexto usar com base na rota
  const context = isAdminRoute ? adminAuth : userAuth;
  const { isAuthenticated, userRole } = context;

  if (!isAuthenticated) {
    return <Navigate to={isAdminRoute ? '/admin/login' : '/login'} replace />;
  }

  if (adminOnly && userRole !== 'admin') {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;