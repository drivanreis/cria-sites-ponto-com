// File: frontend/src/components/layout/HeaderAdmin.tsx

import React from 'react';
import { Link } from 'react-router-dom';
import { useAdminAuth } from '../../hooks/useAdminAuth';
import '../../App.css';

const HeaderAdmin: React.FC = () => {
  const { logout } = useAdminAuth();

  return (
    <header className="app-header admin">
      <div className="header-content">
        <Link to="/admin/dashboard" className="app-logo">Admin - Cria Sites</Link>
        <nav>
          <Link to="/admin/admin-users">Administradores</Link>
          <Link to="/admin/users">Usuários</Link>
          <Link to="/admin/employees">Funcionários</Link>
          <Link to="/admin/test-connections">Testar Conexões</Link>
          <button onClick={logout}>Sair</button>
        </nav>
      </div>
    </header>
  );
};

export default HeaderAdmin;
