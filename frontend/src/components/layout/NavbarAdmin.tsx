// File: frontend/src/components/layout/NavbarAdmin.tsx

import React from 'react';
import { Link } from 'react-router-dom';
import '../../App.css';

const NavbarAdmin: React.FC = () => {
  return (
    <nav style={{ padding: '10px', background: '#222', color: '#fff' }}>
      <ul style={{ listStyle: 'none', display: 'flex', gap: '20px', margin: 0 }}>
        <li>
          <Link to="/admin/dashboard" style={{ color: '#fff', textDecoration: 'none' }}>
            Dashboard
          </Link>
        </li>
        <li>
          <Link to="/admin/admin-users" style={{ color: '#fff', textDecoration: 'none' }}>
            Gerenciar Administradores
          </Link>
        </li>
        <li>
          <Link to="/admin/users" style={{ color: '#fff', textDecoration: 'none' }}>
            Gerenciar Usuários
          </Link>
        </li>
        <li>
          <Link to="/admin/employees" style={{ color: '#fff', textDecoration: 'none' }}>
            Gerenciar Funcionários
          </Link>
        </li>
        <li>
          <Link to="/admin/test-ai" style={{ color: '#fff', textDecoration: 'none' }}>
            Testar Conexões AI
          </Link>
        </li>
      </ul>
    </nav>
  );
};

export default NavbarAdmin;
