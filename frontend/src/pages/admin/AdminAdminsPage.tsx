// File: frontend/src/pages/admin/AdminAdminsPage.tsx


import React, { useEffect, useState } from 'react';
import {
  getAllAdminUsers,
  createAdminUser,
  updateAdminUser,
  deleteAdminUser,
} from '../../api/users_admin';
import type { AdminUser, CreateAdminUser } from '../../api/users_admin';
import '../../App.css';

const AdminAdminsPage: React.FC = () => {
  const [adminUsers, setAdminUsers] = useState<AdminUser[]>([]);
  const [formData, setFormData] = useState<CreateAdminUser>({
    username: '',
    password: '',
  });
  const [editingId, setEditingId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // ----------- CRUD handlers -----------
  const fetchAdmins = async () => {
    setLoading(true);
    setError(null);
    try {
      const admins = await getAllAdminUsers();
      setAdminUsers(admins);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAdmins();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.username || !formData.password) {
      setError('Usuário e senha são obrigatórios.');
      return;
    }
    try {
      setLoading(true);
      setError(null);
      setSuccess(null);

      if (editingId) {
        await updateAdminUser(editingId, formData);
        setSuccess('Administrador atualizado com sucesso.');
      } else {
        await createAdminUser(formData);
        setSuccess('Administrador criado com sucesso.');
      }

      setFormData({ username: '', password: '' });
      setEditingId(null);
      fetchAdmins();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (admin: AdminUser) => {
    setFormData({ username: admin.username, password: '' });
    setEditingId(admin.id);
    setError(null);
    setSuccess(null);
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setFormData({ username: '', password: '' });
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Tem certeza que deseja excluir este administrador?')) return;
    try {
      setLoading(true);
      await deleteAdminUser(id);
      setSuccess('Administrador excluído com sucesso.');
      fetchAdmins();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  // ----------- Render -----------
  return (
    <div className="App">
      <h1>Gerenciar Administradores</h1>

      {error && <p style={{ color: 'red' }}>{error}</p>}
      {success && <p style={{ color: 'green' }}>{success}</p>}

      <form onSubmit={handleSubmit} style={{ marginBottom: '2rem', maxWidth: 400 }}>
        <div>
          <label>Usuário (username):</label>
          <input
            type="text"
            name="username"
            value={formData.username}
            onChange={handleChange}
            required
          />
        </div>
        <div>
          <label>Senha:</label>
          <input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            required
          />
        </div>
        <button type="submit" disabled={loading} style={{ marginTop: '10px' }}>
          {editingId ? 'Atualizar' : 'Criar'}
        </button>
        {editingId && (
          <button
            type="button"
            onClick={handleCancelEdit}
            style={{ marginLeft: '10px' }}
          >
            Cancelar Edição
          </button>
        )}
      </form>

      <h2>Lista de Administradores</h2>
      {loading ? (
        <p>Carregando...</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th>ID</th>
              <th>Usuário</th>
              <th>Data Criação</th>
              <th>Último Login</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {adminUsers.length ? (
              adminUsers.map((admin) => (
                <tr key={admin.id}>
                  <td>{admin.id}</td>
                  <td>{admin.username}</td>
                  <td>{admin.creation_date}</td>
                  <td>{admin.last_login || 'N/A'}</td>
                  <td>
                    <button onClick={() => handleEdit(admin)}>Editar</button>
                    <button
                      onClick={() => handleDelete(admin.id)}
                      style={{ marginLeft: '10px' }}
                    >
                      Excluir
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={5}>Nenhum administrador encontrado.</td>
              </tr>
            )}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default AdminAdminsPage;
