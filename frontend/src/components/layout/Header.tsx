// src/components/layout/Header.tsx
import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth'; // Para mostrar status de login
import '../../App.css'; // Usando o CSS global por enquanto

const Header: React.FC = () => {
  const { isAuthenticated, logout, userRole } = useAuth();

  return (
    <header className="app-header">
      <div className="header-content">
        <Link to="/" className="app-logo">Cria Sites .com</Link>
        <nav>
          {isAuthenticated ? (
            <>
              {userRole === 'admin' && <Link to="/admin/dashboard" className="nav-link">Admin</Link>}
              {userRole === 'user' && <Link to="/dashboard" className="nav-link">Dashboard</Link>}
              <button onClick={logout} className="nav-button">Sair</button>
            </>
          ) : (
            <>
              <Link to="/login" className="nav-link">Entrar</Link>
              <Link to="/cadastro" className="nav-link">Cadastrar</Link>
            </>
          )}
          <Link to="/sobre" className="nav-link">Sobre</Link>
        </nav>
      </div>
    </header>
  );
};

export default Header;
