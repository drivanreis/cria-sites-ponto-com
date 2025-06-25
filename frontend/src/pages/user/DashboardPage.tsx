// src/pages/user/DashboardPage.tsx
import React from 'react';
import { useAuth } from '../../hooks/useAuth';
import { Link } from 'react-router-dom';
import '../../App.css';

const DashboardPage: React.FC = () => {
  const { userRole, logout } = useAuth();
  return (
    <div className="App">
      <h1>Dashboard do Usuário</h1>
      <p>Bem-vindo ao seu painel de controle!</p>
      <p>Seu papel: {userRole}</p>
      
      <nav>
        <ul>
          <li><Link to="/briefings">Meus Briefings</Link></li>
          <li><Link to="/profile">Meu Perfil</Link></li>
        </ul>
      </nav>
      <button onClick={logout}>Sair</button>
    </div>
  );
};

export default DashboardPage;