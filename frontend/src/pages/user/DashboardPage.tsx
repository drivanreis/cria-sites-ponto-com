// frontend/src/pages/user/DashboardPage.tsx

import React, { useEffect, useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { Link } from 'react-router-dom';
import { getUserProfile } from '../../api/users';
import type { User } from '../../api/users';

import '../../App.css';

const DashboardPage: React.FC = () => {
  const { userRole, logout } = useAuth();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const profile = await getUserProfile();
        setUser(profile);
      } catch (err: unknown) {
        if (err instanceof Error) {
          setError(err.message);
        } else {
          setError('Erro ao carregar informações do usuário.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, []);

  if (loading) return <div className="App">Carregando...</div>;
  if (error) return <div className="App" style={{ color: 'red' }}>{error}</div>;
  if (!user) return <div className="App">Usuário não encontrado.</div>;

  return (
    <div className="App">
      <h1>Dashboard do Usuário</h1>
      <p>Bem-vindo, <strong>{user.nickname}</strong>!</p>
      <p>Seu papel: {userRole}</p>
      <p>Status: {user.status}</p>
      <p>Email verificado: {user.email_verified ? 'Sim' : 'Não'}</p>
      <p>2FA ativo: {user.is_two_factor_enabled ? 'Sim' : 'Não'}</p>

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
