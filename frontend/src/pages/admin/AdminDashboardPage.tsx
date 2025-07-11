// File: frontend/src/pages/admin/AdminDashboardPage.tsx
import React from 'react';
import { useAdminAuth } from '../../hooks/useAdminAuth'; // Alterado para useAdminAuth
import { Link } from 'react-router-dom';
import '../../App.css'; // Usando o CSS global por enquanto

const AdminDashboardPage: React.FC = () => {
  const { userRole, logout } = useAdminAuth(); // Alterado para useAdminAuth para obter o userRole para exibição

  return (
    <div className="App">
      <h1>Painel Administrativo</h1>
      <p>Bem-vindo, Administrador! Você está logado como: {userRole}</p>
      
      <nav>
        <h2>Gerenciamento</h2>
        <ul>
          <li><Link to="/admin/admins">Gerenciar Administradores</Link></li>
          <li><Link to="/admin/users">Gerenciar Usuários</Link></li>
          <li><Link to="/admin/employees">Gerenciar Funcionários</Link></li>
          <li><Link to="/admin/briefings">Gerenciar Briefings</Link></li>
          <li><Link to="/admin/test-connections">Testar Conexões AI</Link></li>
          {/* Adicione mais links conforme necessário */}
        </ul>
      </nav>

      <div style={{ marginTop: '20px' }}>
        <Link to="/dashboard" style={{ marginRight: '10px' }}>Ir para Dashboard do Usuário</Link>
        <button onClick={logout}>Sair</button>
      </div>
    </div>
  );
};

export default AdminDashboardPage;