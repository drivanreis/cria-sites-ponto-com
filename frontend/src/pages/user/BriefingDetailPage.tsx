// src/pages/user/BriefingDetailPage.tsx
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  getBriefingById,
  chatWithEmployee,
  compileBriefing,
} from '../../api/briefings';
import type { BriefingWithHistory } from '../../api/briefings';

import '../../App.css';

const BriefingDetailPage: React.FC = () => {
  const { id } = useParams();
  const [briefing, setBriefing] = useState<BriefingWithHistory | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [chatMessage, setChatMessage] = useState('');
  const [employeeName, setEmployeeName] = useState('');

useEffect(() => {
  const fetchBriefing = async () => {
    try {
      if (!id) throw new Error('ID do briefing não fornecido.');
      const data = await getBriefingById(id);
      setBriefing(data);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Erro ao carregar briefing.');
      }
    } finally {
      setLoading(false);
    }
  };

  fetchBriefing();
}, [id]);

  const handleChat = async () => {
    if (!id || !employeeName || !chatMessage.trim()) return;

try {
  const updatedBriefing = await chatWithEmployee(id, employeeName, chatMessage);
  setBriefing(updatedBriefing);
  setChatMessage('');
} catch (err: unknown) {
  if (err instanceof Error) {
    alert(err.message);
  } else {
    alert('Erro ao enviar mensagem.');
  }
}

  };

  const handleCompile = async () => {
    if (!id) return;
try {
  const result = await compileBriefing(id);
  alert('Briefing compilado com sucesso!\nResultado:\n' + JSON.stringify(result, null, 2));
} catch (err: unknown) {
  if (err instanceof Error) {
    alert(err.message);
  } else {
    alert('Erro ao compilar briefing.');
  }
}

  };

  if (loading) return <div className="App">Carregando briefing...</div>;
  if (error) return <div className="App" style={{ color: 'red' }}>{error}</div>;
  if (!briefing) return <div className="App">Briefing não encontrado.</div>;

  return (
    <div className="App">
      <h1>Detalhes do Briefing</h1>
      <p><strong>ID:</strong> {briefing.id}</p>
      <p><strong>Título:</strong> {briefing.title}</p>
      <p><strong>Descrição:</strong> {briefing.description}</p>

      <hr />

      <h2>Histórico de Conversas</h2>
      {briefing.history && briefing.history.length > 0 ? (
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {briefing.history.map((msg, index) => (
            <li key={index} style={{ marginBottom: '10px' }}>
              <strong>{msg.sender}</strong> ({msg.timestamp}): {msg.message}
            </li>
          ))}
        </ul>
      ) : (
        <p>Nenhuma conversa ainda.</p>
      )}

      <hr />

      <h2>Enviar Mensagem para Funcionário</h2>
      <input
        type="text"
        placeholder="Nome do funcionário (ex: GPT4, Claude...)"
        value={employeeName}
        onChange={(e) => setEmployeeName(e.target.value)}
        style={{ marginBottom: '10px', padding: '5px', width: '100%' }}
      />
      <textarea
        placeholder="Sua mensagem"
        value={chatMessage}
        onChange={(e) => setChatMessage(e.target.value)}
        style={{ padding: '5px', width: '100%', height: '100px' }}
      />
      <br />
      <button onClick={handleChat} style={{ marginTop: '10px' }}>Enviar Mensagem</button>

      <hr />

      <h2>Compilar Briefing</h2>
      <button onClick={handleCompile}>Compilar</button>
    </div>
  );
};

export default BriefingDetailPage;
