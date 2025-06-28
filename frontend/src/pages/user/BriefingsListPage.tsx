// frontend/src/pages/user/BriefingsListPage.tsx

import React, { useEffect, useState } from 'react';
import {
  getBriefings,
  createBriefing,
  deleteBriefing,
} from '../../api/briefings';
import type { Briefing } from '../../api/briefings';

import { useNavigate } from 'react-router-dom';
import '../../App.css';

const BriefingsListPage: React.FC = () => {
  const [briefings, setBriefings] = useState<Briefing[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newBriefingTitle, setNewBriefingTitle] = useState('');
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
        setError('Erro ao carregar briefings.');
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
      });
      setBriefings((prev) => [...prev, newBriefing]);
      setNewBriefingTitle('');
    } catch (err: unknown) {
      if (err instanceof Error) {
        alert(err.message);
      } else {
        alert('Erro ao criar briefing.');
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
        alert('Erro ao excluir briefing.');
      }
    }
  };

  const handleViewBriefing = (id: string) => {
    navigate(`/briefings/${id}`);
  };

  return (
    <div className="App">
      <h1>Meus Briefings</h1>

      <div style={{ marginBottom: '20px' }}>
        <h2>Criar Novo Briefing</h2>
        <input
          type="text"
          placeholder="Título do Briefing"
          value={newBriefingTitle}
          onChange={(e) => setNewBriefingTitle(e.target.value)}
          style={{ marginRight: '10px', padding: '5px' }}
        />
        <button onClick={handleCreateBriefing}>Criar</button>
      </div>

      {loading ? (
        <p>Carregando briefings...</p>
      ) : error ? (
        <p style={{ color: 'red' }}>{error}</p>
      ) : briefings.length === 0 ? (
        <p>Nenhum briefing criado ainda.</p>
      ) : (
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {briefings.map((briefing) => (
            <li key={briefing.id} style={{ marginBottom: '15px' }}>
              <strong>{briefing.title}</strong> — <em>{briefing.status}</em>
              <br />
              <button
                style={{ marginRight: '10px' }}
                onClick={() => handleViewBriefing(briefing.id)}
              >
                Ver Detalhes
              </button>
              <button onClick={() => handleDeleteBriefing(briefing.id)}>
                Excluir
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default BriefingsListPage;
