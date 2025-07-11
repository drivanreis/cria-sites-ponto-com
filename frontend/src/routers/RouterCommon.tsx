// File: frontend/src/routers/RouterCommon.tsx

import { Routes, Route } from 'react-router-dom';
import HeaderPublic from '../components/layout/HeaderPublic';
import Footer from '../components/layout/Footer';
import HomePage from '../pages/common/HomePage';
import AboutPage from '../pages/common/AboutPage';
import UserLoginPage from '../pages/auth/UserLoginPage';
import DashboardPage from '../pages/user/DashboardPage';
import ProfilePage from '../pages/user/ProfilePage';
import BriefingsListPage from '../pages/user/BriefingsListPage';
import BriefingDetailPage from '../pages/user/BriefingDetailPage';
import ProtectedRoute from '../components/common/ProtectedRoute';

const RouterCommon = () => {
  return (
    <>
      <HeaderPublic />

      <main className="app-content">
        <Routes>
          {/* Rotas públicas */}
          <Route path="/" element={<HomePage />} />
          <Route path="/sobre" element={<AboutPage />} />
          <Route path="/login" element={<UserLoginPage />} />

          {/* Rotas protegidas (usuário comum) */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/briefings"
            element={
              <ProtectedRoute>
                <BriefingsListPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/briefings/:id"
            element={
              <ProtectedRoute>
                <BriefingDetailPage />
              </ProtectedRoute>
            }
          />

          {/* 404 (limitada ao domínio público) */}
          <Route path="*" element={<div>404 - Página Não Encontrada</div>} />
        </Routes>
      </main>

      <Footer />
    </>
  );
};

export default RouterCommon;
