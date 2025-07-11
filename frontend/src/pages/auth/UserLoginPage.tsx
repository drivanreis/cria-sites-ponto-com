// File: frontend/src/pages/auth/UserLoginPage.tsx

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { loginUser } from '../../api/auth';
import '../../App.css';

const UserLoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const { login, isAuthenticated, userRole } = useAuth();
  const navigate = useNavigate();

  if (isAuthenticated) {
    if (userRole === 'admin') {
      navigate('/admin/dashboard', { replace: true });
    } else {
      navigate('/dashboard', { replace: true });
    }
  }

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);

    try {
      const response = await loginUser(email, password);
      login(response.access_token);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message || "Erro desconhecido ao tentar fazer login.");
      } else {
        setError("Erro desconhecido.");
      }
    }
  };

  const handleSocialLogin = (provider: 'google' | 'github') => {
    window.location.href = `${import.meta.env.VITE_API_BASE_URL}/auth/${provider}`;
  };

  return (
    <div className="App">
      <h1>Login do Usuário</h1>

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
          <label htmlFor="email">Email:</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            placeholder="seu@email.com"
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

      <div style={{ textAlign: 'center' }}>
        <p>Ou entre com:</p>
        <button onClick={() => handleSocialLogin('google')} style={{ marginRight: '10px' }}>
          Google
        </button>
        <button onClick={() => handleSocialLogin('github')}>GitHub</button>
      </div>

      <p style={{ textAlign: 'center', marginTop: '20px' }}>
        Não tem uma conta? <a href="/cadastro">Cadastre-se aqui</a>
      </p>
    </div>
  );
};

export default UserLoginPage;
