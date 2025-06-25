// src/pages/user/BriefingsListPage.tsx

import React, { useEffect, useState } from 'react';
import { getBriefings, createBriefing, deleteBriefing } from '../../api/briefings';
import type { Briefing } from '../../api/briefings';

import { useNavigate } from 'react-router-dom';
import '../../App.css';

const BriefingsListPage: React.FC = () => {
  const [briefings, setBriefings] = useState<Briefing[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newBriefingTitle, setNewBriefingTitle] = useState('');
  const [newBriefingDescription, setNewBriefingDescription] = useState('');
  const navigate = useNavigate();

  const fetchBriefings = async () => {
    try {
      setLoading(true);
      const data = await getBriefings();
      setBriefings(data);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Erro ao carregar briefings');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBriefings();
  }, []);

  const handleCreateBriefing = async () => {
    if (!newBriefingTitle.trim()) {
      alert('Título é obrigatório');
      return;
    }
try {
  const newBriefing = await createBriefing({
    title: newBriefingTitle,
    description: newBriefingDescription,
  });
  setBriefings((prev) => [...prev, newBriefing]);
  setNewBriefingTitle('');
  setNewBriefingDescription('');
} catch (err: unknown) {
  if (err instanceof Error) {
    alert(err.message);
  } else {
    alert('Erro ao criar briefing');
  }
}
  };

const handleDeleteBriefing = async (id: string) => {
  if (!window.confirm(`Tem certeza que deseja excluir o briefing ${id}?`)) return;
  try {
    await deleteBriefing(id);
    setBriefings((prev) => prev.filter((b) => b.id !== id));
  } catch (err: unknown) {
    if (err instanceof Error) {
      alert(err.message);
    } else {
      alert('Erro ao excluir briefing');
    }
  }
};

  return (
    <div className="App">
      <h1>Meus Briefings</h1>

      <div style={{ marginBottom: '20px' }}>
        <h2>Novo Briefing</h2>
        <input
          type="text"
          placeholder="Título"
          value={newBriefingTitle}
          onChange={(e) => setNewBriefingTitle(e.target.value)}
          style={{ marginRight: '10px', padding: '5px' }}
        />
        <input
          type="text"
          placeholder="Descrição"
          value={newBriefingDescription}
          onChange={(e) => setNewBriefingDescription(e.target.value)}
          style={{ marginRight: '10px', padding: '5px' }}
        />
        <button onClick={handleCreateBriefing}>Criar</button>
      </div>

      {loading ? (
        <p>Carregando briefings...</p>
      ) : error ? (
        <p style={{ color: 'red' }}>{error}</p>
      ) : briefings.length === 0 ? (
        <p>Nenhum briefing encontrado.</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={{ borderBottom: '1px solid #ccc' }}>ID</th>
              <th style={{ borderBottom: '1px solid #ccc' }}>Título</th>
              <th style={{ borderBottom: '1px solid #ccc' }}>Descrição</th>
              <th style={{ borderBottom: '1px solid #ccc' }}>Ações</th>
            </tr>
          </thead>
          <tbody>
            {briefings.map((briefing) => (
              <tr key={briefing.id}>
                <td>{briefing.id}</td>
                <td>{briefing.title}</td>
                <td>{briefing.description}</td>
                <td>
                  <button onClick={() => navigate(`/briefings/${briefing.id}`)}>Ver</button>
                  <button
                    onClick={() => handleDeleteBriefing(briefing.id)}
                    style={{ marginLeft: '10px', backgroundColor: 'red', color: 'white' }}
                  >
                    Excluir
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default BriefingsListPage;
