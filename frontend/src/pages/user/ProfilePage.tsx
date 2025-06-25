// src/pages/user/ProfilePage.tsx
import React, { useEffect, useState } from 'react';
import { getUserProfile, updateUserProfile } from '../../api/users';
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
        username: profile.username,
        email: profile.email,
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
          <label>Usuário:</label>
          <input
            type="text"
            name="username"
            value={formData.username || ''}
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
            required
          />
        </div>

        <button type="submit" style={{ marginTop: '10px' }}>
          Salvar Alterações
        </button>
      </form>

      {successMessage && <p style={{ color: 'green' }}>{successMessage}</p>}
    </div>
  );
};

export default ProfilePage;
