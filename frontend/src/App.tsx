// src/App.tsx

import { Routes, Route } from 'react-router-dom';
// Importe seus componentes de página
import HomePage from './pages/common/HomePage.tsx';
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage.tsx'; // << NOVO
import DashboardPage from './pages/user/DashboardPage.tsx';
import ProfilePage from './pages/user/ProfilePage.tsx';
import BriefingsListPage from './pages/user/BriefingsListPage.tsx';
import BriefingDetailPage from './pages/user/BriefingDetailPage.tsx';
import AdminDashboardPage from './pages/admin/AdminDashboardPage.tsx';
import AdminUsersPage from './pages/admin/AdminUsersPage.tsx';
import AdminEmployeesPage from './pages/admin/AdminEmployeesPage.tsx';
import TestConnectionsPage from './pages/admin/TestConnectionsPage.tsx';
import AboutPage from './pages/common/AboutPage.tsx';

import Header from './components/layout/Header.tsx'; // << NOVO
import Footer from './components/layout/Footer.tsx'; // << NOVO

import { AuthProvider } from './contexts/AuthProvider.tsx';
import ProtectedRoute from './components/common/ProtectedRoute.tsx';

import './App.css'; // Certifique-se de que este CSS existe e contém os estilos básicos

function App() {
  return (
    <AuthProvider>
      <div className="App">
        <Header /> {/* Incluir o Header aqui */}

        <main className="app-content"> {/* Um elemento main para o conteúdo principal */}
          <Routes>
            {/* Rotas Públicas */}
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/cadastro" element={<RegisterPage />} /> {/* << ROTA PARA REGISTRO */}
            <Route path="/sobre" element={<AboutPage />} />

            {/* Rotas de Usuário Protegidas */}
            <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
            <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
            <Route path="/briefings" element={<ProtectedRoute><BriefingsListPage /></ProtectedRoute>} />
            <Route path="/briefings/:id" element={<ProtectedRoute><BriefingDetailPage /></ProtectedRoute>} />

            {/* Rotas de Administrador Protegidas (exige login e permissão de admin) */}
            <Route path="/admin/dashboard" element={<ProtectedRoute adminOnly><AdminDashboardPage /></ProtectedRoute>} />
            <Route path="/admin/users" element={<ProtectedRoute adminOnly><AdminUsersPage /></ProtectedRoute>} />
            <Route path="/admin/employees" element={<ProtectedRoute adminOnly><AdminEmployeesPage /></ProtectedRoute>} />
            <Route path="/admin/test-connections" element={<ProtectedRoute adminOnly><TestConnectionsPage /></ProtectedRoute>} />

            {/* Rota para 404 - Not Found */}
            <Route path="*" element={<div>404 - Página Não Encontrada</div>} />
          </Routes>
        </main>

        <Footer /> {/* Incluir o Footer aqui */}
      </div>
    </AuthProvider>
  );
}

export default App;