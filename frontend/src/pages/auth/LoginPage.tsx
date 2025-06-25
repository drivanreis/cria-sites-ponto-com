
// src/pages/auth/LoginPage.tsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthProvider.tsx';
import '../../App.css'; // Usando o CSS global por enquanto

const LoginPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const { login, isAuthenticated, userRole } = useAuth();
  const navigate = useNavigate();

  // Redireciona se já estiver logado
  if (isAuthenticated) {
    if (userRole === 'admin') {
      navigate('/admin/dashboard', { replace: true });
    } else {
      navigate('/dashboard', { replace: true });
    }
  }

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null); // Limpa erros anteriores
    try {
      await login(username, password);
      // O redirecionamento acontece automaticamente pelo `if (isAuthenticated)` acima,
      // pois o estado de autenticação será atualizado pelo AuthContext.
    } catch (err: any) {
      setError(err.message || "Erro desconhecido ao tentar fazer login.");
    }
  };

  return (
    <div className="App"> {/* Usando a classe App para centralizar */}
      <h1>Login</h1>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxWidth: '300px', margin: '20px auto' }}>
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
      <p>
        Não tem uma conta? <a href="/cadastro">Cadastre-se aqui</a>
      </p>
      <p>
        Para testar como Admin: use qualquer usuário/senha que inclua "admin" no nome de usuário (ex: admin@example.com / password).
      </p>
    </div>
  );
};

export default LoginPage;