// src/routers/RouterAdmin.tsx
import { Routes, Route, Navigate } from 'react-router-dom';
import HeaderAdmin from '../components/layout/HeaderAdmin';
import AdminLoginPage from '../pages/auth/AdminLoginPage';
import AdminDashboardPage from '../pages/admin/AdminDashboardPage';
import AdminUsersPage from '../pages/admin/AdminUsersPage';
import AdminEmployeesPage from '../pages/admin/AdminEmployeesPage';
import TestConnectionsPage from '../pages/admin/TestConnectionsPage';
import ProtectedRoute from '../components/common/ProtectedRoute';

const RouterAdmin = () => {
  return (
    <>
      <HeaderAdmin />

      <main className="app-content">
        <Routes>
          <Route path="/admin/login" element={<AdminLoginPage />} />
          <Route path="/admin" element={<Navigate to="/admin/dashboard" replace />} />
          <Route
            path="/admin/dashboard"
            element={<ProtectedRoute adminOnly><AdminDashboardPage /></ProtectedRoute>}
          />
          <Route
            path="/admin/admin-users"
            element={<ProtectedRoute adminOnly><AdminUsersPage /></ProtectedRoute>}
          />
          <Route
            path="/admin/users"
            element={<ProtectedRoute adminOnly><AdminUsersPage /></ProtectedRoute>}
          />
          <Route
            path="/admin/employees"
            element={<ProtectedRoute adminOnly><AdminEmployeesPage /></ProtectedRoute>}
          />
          <Route
            path="/admin/test-connections"
            element={<ProtectedRoute adminOnly><TestConnectionsPage /></ProtectedRoute>}
          />
        </Routes>
      </main>
    </>
  );
};

export default RouterAdmin;
