// File: frontend/src/components/layout/HeaderPublic.tsx

import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import '../../App.css';

const HeaderPublic: React.FC = () => {
  const { isAuthenticated, logout, userRole } = useAuth();

  return (
    <header className="app-header">
      <div className="header-content">
        <Link to="/" className="app-logo">Cria Sites .com</Link>
        <nav>
          {isAuthenticated ? (
            <>
              {userRole === 'admin' && <Link to="/admin/dashboard">Admin</Link>}
              {userRole === 'user' && <Link to="/dashboard">Dashboard</Link>}
              <button onClick={logout}>Sair</button>
            </>
          ) : (
            <>
              <Link to="/login">Entrar</Link>
              <Link to="/cadastro">Cadastrar</Link>
            </>
          )}
          <Link to="/sobre">Sobre</Link>
        </nav>
      </div>
    </header>
  );
};

export default HeaderPublic;
