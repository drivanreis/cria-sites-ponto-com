// frontend/src/pages/user/ProfilePage.tsx

import React, { useEffect, useState } from 'react';
import {
  getUserProfile,
  updateUserProfile,
} from '../../api/users';
import type { User } from '../../api/users';

import '../../App.css';

const ProfilePage: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [formData, setFormData] = useState<Partial<User>>({});
  const [loading, setLoading] = useState(true);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchProfile = async () => {
    try {
      const profile = await getUserProfile();
      setUser(profile);
      setFormData({
        nickname: profile.nickname,
        email: profile.email,
        phone_number: profile.phone_number,
      });
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message || 'Erro ao carregar perfil');
      } else {
        setError('Erro ao carregar perfil');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const updated = await updateUserProfile(formData);
      setUser(updated);
      setSuccessMessage('Perfil atualizado com sucesso!');
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message || 'Erro ao atualizar perfil');
      } else {
        setError('Erro ao atualizar perfil');
      }
    }
  };

  if (loading) return <div className="App">Carregando perfil...</div>;
  if (error) return <div className="App" style={{ color: 'red' }}>{error}</div>;
  if (!user) return <div className="App">Perfil não encontrado.</div>;

  return (
    <div className="App">
      <h1>Meu Perfil</h1>

      <form onSubmit={handleSubmit} style={{ maxWidth: '400px', margin: 'auto' }}>
        <div>
          <label>Apelido (nickname):</label>
          <input
            type="text"
            name="nickname"
            value={formData.nickname || ''}
            onChange={handleChange}
            required
          />
        </div>

        <div>
          <label>Email:</label>
          <input
            type="email"
            name="email"
            value={formData.email || ''}
            onChange={handleChange}
          />
        </div>

        <div>
          <label>Telefone:</label>
          <input
            type="text"
            name="phone_number"
            value={formData.phone_number || ''}
            onChange={handleChange}
          />
        </div>

        <button type="submit" style={{ marginTop: '10px' }}>
          Salvar Alterações
        </button>
      </form>

      {successMessage && <p style={{ color: 'green' }}>{successMessage}</p>}

      <hr />

      <h3>Informações do Sistema</h3>
      <p><strong>Status:</strong> {user.status}</p>
      <p><strong>Email Verificado:</strong> {user.email_verified ? 'Sim' : 'Não'}</p>
      <p><strong>2FA Ativado:</strong> {user.is_two_factor_enabled ? 'Sim' : 'Não'}</p>
      <p><strong>Criado em:</strong> {user.creation_date}</p>
      {user.last_login && <p><strong>Último Login:</strong> {user.last_login}</p>}
    </div>
  );
};

export default ProfilePage;
