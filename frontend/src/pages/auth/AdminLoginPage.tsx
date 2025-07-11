// File: frontend/src/pages/auth/AdminLoginPage.tsx

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAdminAuth } from '../../hooks/useAdminAuth';
import { loginAdmin } from '../../api/auth';
import '../../App.css';

const AdminLoginPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const { login, isAuthenticated, userRole } = useAdminAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated && userRole === 'admin') {
      navigate('/admin/dashboard', { replace: true });
    }
  }, [isAuthenticated, userRole, navigate]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);

    try {
      const response = await loginAdmin(username, password);
      login(response.access_token);
      navigate('/admin/dashboard'); // ✅ redireciona para a rota semântica correta
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message || 'Erro desconhecido ao tentar fazer login.');
      } else {
        setError('Erro desconhecido.');
      }
    }
  };

  return (
    <div className="App">
      <h1>Login Administrativo</h1>

      <form
        onSubmit={handleSubmit}
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '10px',
          maxWidth: '300px',
          margin: '20px auto',
        }}
      >
        <div>
          <label htmlFor="username">Usuário:</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>

        <div>
          <label htmlFor="password">Senha:</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        {error && <p style={{ color: 'red' }}>{error}</p>}

        <button type="submit">Entrar</button>
      </form>

      <p style={{ textAlign: 'center', marginTop: '20px' }}>
        <a href="/">Voltar para o site público</a>
      </p>
    </div>
  );
};

export default AdminLoginPage;
