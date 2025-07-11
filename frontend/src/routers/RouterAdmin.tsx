// File: frontend/src/routers/RouterAdmin.tsx

import { Routes, Route, Navigate } from 'react-router-dom';

import AdminDashboardPage from '../pages/admin/AdminDashboardPage';
import AdminEmployeesPage from '../pages/admin/AdminEmployeesPage';
import AdminAdminsPage from '../pages/admin/AdminAdminsPage';
import AdminUsersPage from '../pages/admin/AdminUsersPage';
import TestConnectionsPage from '../pages/admin/TestConnectionsPage';
// ✅ IMPORTAR A PÁGINA DE BRIEFINGS DO ADMIN
import AdminBriefingsPage from '../pages/admin/AdminBriefingsPage'; // Supondo este nome

import AdminLoginPage from '../pages/auth/AdminLoginPage';

import HeaderAdmin from '../components/layout/HeaderAdmin';
import NavbarAdmin from '../components/layout/NavbarAdmin';
import ProtectedAdminRoute from '../components/common/ProtectedAdminRoute';

const RouterAdmin = () => {
  return (
    <>
      <HeaderAdmin />
      <NavbarAdmin />
      <Routes>
        {/* Login do administrador (sem proteção) */}
        <Route path="/admin/login" element={<AdminLoginPage />} />

        {/* Redirecionamento para rota semântica do dashboard */}
        <Route path="/admin" element={<Navigate to="/admin/dashboard" replace />} />

        {/* Dashboard principal */}
        <Route
          path="/admin/dashboard"
          element={
            <ProtectedAdminRoute>
              <AdminDashboardPage />
            </ProtectedAdminRoute>
          }
        />

        {/* CRUD de usuários comuns */}
        <Route
          path="/admin/users"
          element={
            <ProtectedAdminRoute>
              <AdminUsersPage />
            </ProtectedAdminRoute>
          }
        />

        {/* CRUD de administradores */}
        <Route
          path="/admin/admins"
          element={
            <ProtectedAdminRoute>
              <AdminAdminsPage />
            </ProtectedAdminRoute>
          }
        />

        {/* Gerenciamento de funcionários */}
        <Route
          path="/admin/employees"
          element={
            <ProtectedAdminRoute>
              <AdminEmployeesPage />
            </ProtectedAdminRoute>
          }
        />

        {/* ✅ NOVA ROTA: Gerenciamento de Briefings */}
        <Route
          path="/admin/briefings"
          element={
            <ProtectedAdminRoute>
              <AdminBriefingsPage /> {/* Use o componente da página de briefings do admin aqui */}
            </ProtectedAdminRoute>
          }
        />

        {/* Teste de conexões AI */}
        <Route
          path="/admin/test-connections" // ✅ Corrigi para corresponder ao link no dashboard
          element={
            <ProtectedAdminRoute>
              <TestConnectionsPage />
            </ProtectedAdminRoute>
          }
        />

        {/* Fallback para qualquer rota inválida em /admin */}
        <Route path="/admin/*" element={<Navigate to="/admin/dashboard" replace />} />
      </Routes>
    </>
  );
};

export default RouterAdmin;