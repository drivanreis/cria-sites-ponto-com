// File: frontend/src/pages/admin/AdminBriefingsPage.tsx

import React, { useState, useEffect, useCallback } from 'react';
import { getBriefings, getBriefingById, type Briefing, type BriefingWithHistory} from '../../api/briefings';
import { getAllUsers, type User } from '../../api/users';
import { useAdminAuth } from '../../hooks/useAdminAuth';
import '../../App.css';

const AdminBriefingsPage: React.FC = () => {
  const { userRole } = useAdminAuth(); // Apenas para exibição, se desejar

  const [briefings, setBriefings] = useState<Briefing[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedBriefing, setSelectedBriefing] = useState<BriefingWithHistory | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [selectedUserFilter, setSelectedUserFilter] = useState<string>(''); // Para filtrar por ID de usuário

  // Função para buscar todos os briefings
  const fetchBriefings = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getBriefings();
      // Se houver um filtro de usuário selecionado, aplique-o
      const filteredData = selectedUserFilter
        ? data.filter(briefing => briefing.last_edited_by === selectedUserFilter)
        : data;
      setBriefings(filteredData);
    } catch (err) {
      console.error("Erro ao buscar briefings:", err);
      setError("Erro ao carregar briefings. Tente novamente mais tarde.");
    } finally {
      setLoading(false);
    }
  }, [selectedUserFilter]);

  // Função para buscar um briefing específico com histórico
  const fetchBriefingHistory = useCallback(async (briefingId: string) => {
    setLoading(true); // Pode ser um estado de loading separado para o histórico
    setError(null);
    try {
      const data = await getBriefingById(briefingId);
      setSelectedBriefing(data);
    } catch (err) {
      console.error("Erro ao buscar histórico do briefing:", err);
      setError("Erro ao carregar histórico do briefing. Tente novamente mais tarde.");
    } finally {
      setLoading(false);
    }
  }, []);

  // Função para buscar a lista de usuários para o filtro
  const fetchUsers = useCallback(async () => {
    try {
      const data = await getAllUsers();
      setUsers(data);
    } catch (err) {
      console.error("Erro ao buscar usuários para o filtro:", err);
      // Não define erro na UI principal, pois é apenas um filtro opcional
    }
  }, []);

  // Efeito para carregar briefings e usuários ao montar o componente ou quando o filtro de usuário muda
  useEffect(() => {
    fetchBriefings();
    fetchUsers();
  }, [fetchBriefings, fetchUsers]);

  // Handler para selecionar um briefing da lista
  const handleSelectBriefing = (briefingId: string) => {
    setSelectedBriefing(null); // Limpa o briefing selecionado anterior
    fetchBriefingHistory(briefingId);
  };

  // Handler para mudar o filtro de usuário
  const handleUserFilterChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedUserFilter(event.target.value);
    setSelectedBriefing(null); // Limpa o briefing selecionado ao mudar o filtro
  };

  const getStatusClass = (status: string) => {
    switch (status) {
      case 'open': return 'status-open';
      case 'in_progress': return 'status-in-progress';
      case 'completed': return 'status-completed';
      case 'cancelled': return 'status-cancelled';
      default: return '';
    }
  };

  return (
    <div className="App">
      <h1>Gerenciar Briefings (Admin)</h1>
      <p>Você está logado como: {userRole}</p>

      {error && <p className="error-message">{error}</p>}

      <div style={{ marginBottom: '20px' }}>
        <label htmlFor="userFilter">Filtrar por Usuário: </label>
        <select
          id="userFilter"
          value={selectedUserFilter}
          onChange={handleUserFilterChange}
          style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
        >
          <option value="">Todos os Usuários</option>
          {users.map((user) => (
            <option key={user.id} value={user.id}>
              {user.nickname} ({user.email})
            </option>
          ))}
        </select>
      </div>

      <div style={{ display: 'flex', gap: '20px' }}>
        <div style={{ flex: 1, border: '1px solid #ddd', padding: '15px', borderRadius: '8px', backgroundColor: '#f9f9f9' }}>
          <h2>Lista de Briefings</h2>
          {loading && !selectedBriefing ? (
            <p>Carregando briefings...</p>
          ) : briefings.length === 0 ? (
            <p>Nenhum briefing encontrado.</p>
          ) : (
            <ul style={{ listStyleType: 'none', padding: 0 }}>
              {briefings.map((briefing) => (
                <li
                  key={briefing.id}
                  onClick={() => handleSelectBriefing(briefing.id)}
                  style={{
                    padding: '10px 15px',
                    margin: '5px 0',
                    border: `1px solid ${selectedBriefing?.id === briefing.id ? '#007bff' : '#eee'}`,
                    borderRadius: '5px',
                    cursor: 'pointer',
                    backgroundColor: selectedBriefing?.id === briefing.id ? '#e9f5ff' : '#fff',
                    boxShadow: selectedBriefing?.id === briefing.id ? '0 0 5px rgba(0,123,255,0.3)' : 'none',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}
                >
                  <div>
                    <strong>{briefing.title || `Briefing ${briefing.id.substring(0, 8)}...`}</strong>
                    <br />
                    <small>Criado em: {briefing.creation_date ? new Date(briefing.creation_date).toLocaleDateString() : 'N/A'}</small>
                  </div>
                  <span className={`briefing-status ${getStatusClass(briefing.status)}`}>
                    {briefing.status.replace(/_/g, ' ').toUpperCase()}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div style={{ flex: 1, border: '1px solid #ddd', padding: '15px', borderRadius: '8px', backgroundColor: '#f9f9f9' }}>
          <h2>Histórico do Briefing</h2>
          {loading && selectedBriefing ? (
            <p>Carregando histórico...</p>
          ) : selectedBriefing ? (
            <div>
              <h3>{selectedBriefing.title || `Briefing ${selectedBriefing.id.substring(0, 8)}...`}</h3>
              <p>ID: {selectedBriefing.id}</p>
              <p>Status: <span className={`briefing-status ${getStatusClass(selectedBriefing.status)}`}>{selectedBriefing.status.replace(/_/g, ' ').toUpperCase()}</span></p>
              <p>Última Edição por: {selectedBriefing.last_edited_by || 'N/A'}</p>
              <p>Conteúdo: {selectedBriefing.content ? JSON.stringify(selectedBriefing.content) : 'N/A'}</p>
              <p>Roteiro de Desenvolvimento: {selectedBriefing.development_roteiro ? JSON.stringify(selectedBriefing.development_roteiro) : 'N/A'}</p>

              <h4>Conversa:</h4>
              {selectedBriefing.conversation_history && selectedBriefing.conversation_history.length > 0 ? (
                <div style={{ maxHeight: '400px', overflowY: 'auto', border: '1px solid #eee', padding: '10px', borderRadius: '5px' }}>
                  {selectedBriefing.conversation_history.map((msg, index) => (
                    <div
                      key={index}
                      style={{
                        marginBottom: '10px',
                        padding: '8px',
                        borderRadius: '5px',
                        backgroundColor: msg.sender_type === 'user' ? '#d4edda' : '#f8d7da',
                        alignSelf: msg.sender_type === 'user' ? 'flex-end' : 'flex-start',
                        maxWidth: '80%',
                      }}
                    >
                      <strong>{msg.sender_type === 'user' ? 'Você' : 'Funcionário'}:</strong> {msg.message_content}
                      <br />
                      <small style={{ fontSize: '0.75em', color: '#666' }}>
                        {new Date(msg.timestamp).toLocaleString()}
                      </small>
                    </div>
                  ))}
                </div>
              ) : (
                <p>Nenhum histórico de conversa para este briefing.</p>
              )}
            </div>
          ) : (
            <p>Selecione um briefing da lista para ver o histórico de conversas.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminBriefingsPage;