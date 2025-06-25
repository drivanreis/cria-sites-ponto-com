// src/pages/admin/AdminUsersPage.tsx
import React, { useEffect, useState } from 'react';
import { getAllUsers, User, deleteUser } from '../../api/users'; // Importa funções da API de usuários
import '../../App.css'; // Usando o CSS global por enquanto

const AdminUsersPage: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const fetchedUsers = await getAllUsers();
      setUsers(fetchedUsers);
    } catch (err: any) {
      setError(err.message || 'Erro ao carregar usuários.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUser = async (userId: string) => {
    if (window.confirm(`Tem certeza que deseja deletar o usuário com ID ${userId}?`)) {
      try {
        await deleteUser(userId);
        alert(`Usuário ${userId} deletado com sucesso!`);
        fetchUsers(); // Recarrega a lista de usuários após a exclusão
      } catch (err: any) {
        setError(err.message || `Erro ao deletar usuário ${userId}.`);
      }
    }
  };

  if (loading) {
    return <div className="App">Carregando usuários...</div>;
  }

  if (error) {
    return <div className="App" style={{ color: 'red' }}>Erro: {error}</div>;
  }

  return (
    <div className="App">
      <h1>Gerenciamento de Usuários</h1>
      <p>Aqui você pode visualizar e gerenciar todos os usuários do sistema.</p>
      
      {users.length === 0 ? (
        <p>Nenhum usuário encontrado.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Username</th>
              <th>Email</th>
              <th>Ativo</th>
              <th>Admin</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id}>
                <td>{user.id}</td>
                <td>{user.username}</td>
                <td>{user.email}</td>
                <td>{user.is_active ? 'Sim' : 'Não'}</td>
                <td>{user.is_admin ? 'Sim' : 'Não'}</td>
                <td>
                  <button onClick={() => alert(`Funcionalidade de editar para o usuário ${user.id} (ainda não implementado)`)}>Editar</button>
                  <button onClick={() => handleDeleteUser(user.id)} style={{ marginLeft: '5px', backgroundColor: 'red', color: 'white' }}>Deletar</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      <div style={{ marginTop: '20px' }}>
        <button onClick={fetchUsers}>Atualizar Lista</button>
        <a href="/admin/dashboard" style={{ marginLeft: '10px' }}>Voltar ao Painel Admin</a>
      </div>
    </div>
  );
};

export default AdminUsersPage;