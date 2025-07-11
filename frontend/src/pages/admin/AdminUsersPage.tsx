// File: frontend/src/pages/admin/AdminUsersPage.tsx

import React, { useEffect, useState } from 'react';
import {
  getAllUsers,
  updateUser,
  deleteUser,
} from '../../api/users';
import type { User } from '../../api/users';

import '../../App.css';

const AdminUsersPage: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<Partial<User>>({});
  const [editingUserId, setEditingUserId] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const fetchUsers = async () => {
    try {
      const usersData = await getAllUsers();
      setUsers(usersData);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Erro ao carregar usuários.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingUserId) {
        await updateUser(editingUserId, formData);
        setSuccessMessage('Usuário atualizado com sucesso!');
      }
      setFormData({});
      setEditingUserId(null);
      fetchUsers();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Erro ao salvar alterações.');
      }
    }
  };

  const handleEdit = (user: User) => {
    setEditingUserId(user.id);
    setFormData({
      nickname: user.nickname,
      email: user.email,
      phone_number: user.phone_number,
    });
    setSuccessMessage(null);
    setError(null);
  };

  const handleDelete = async (userId: string) => {
    const confirmDelete = confirm('Tem certeza que deseja excluir este usuário?');
    if (!confirmDelete) return;

    try {
      await deleteUser(userId);
      setSuccessMessage('Usuário excluído com sucesso.');
      fetchUsers();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Erro ao excluir usuário.');
      }
    }
  };

  if (loading) return <div className="App">Carregando usuários...</div>;
  if (error) return <div className="App" style={{ color: 'red' }}>{error}</div>;

  return (
    <div className="App">
      <h1>Gerenciar Usuários Comuns</h1>

      {successMessage && <p style={{ color: 'green' }}>{successMessage}</p>}

      <form onSubmit={handleSubmit} style={{ marginBottom: '2rem' }}>
        <h3>{editingUserId ? 'Editar Usuário' : 'Selecione um usuário para editar'}</h3>

        <input
          type="text"
          name="nickname"
          placeholder="Nickname"
          value={formData.nickname || ''}
          onChange={handleChange}
          required
        />
        <input
          type="email"
          name="email"
          placeholder="Email"
          value={formData.email || ''}
          onChange={handleChange}
        />
        <input
          type="text"
          name="phone_number"
          placeholder="Telefone"
          value={formData.phone_number || ''}
          onChange={handleChange}
        />

        <button type="submit">Salvar Alterações</button>
      </form>

      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th>ID</th>
            <th>Nickname</th>
            <th>Email</th>
            <th>Telefone</th>
            <th>Status</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user: User) => (
            <tr key={user.id}>
              <td>{user.id}</td>
              <td>{user.nickname}</td>
              <td>{user.email}</td>
              <td>{user.phone_number}</td>
              <td>{user.status}</td>
              <td>
                <button onClick={() => handleEdit(user)}>Editar</button>
                <button onClick={() => handleDelete(user.id)} style={{ color: 'red' }}>
                  Excluir
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default AdminUsersPage;
