// src/pages/admin/TestConnectionsPage.tsx
import React, { useState } from 'react';
import { testAllAiConnections } from '../../api/employees'; // Importa a função de teste
import '../../App.css'; // Usando o CSS global por enquanto

const TestConnectionsPage: React.FC = () => {
  const [testResult, setTestResult] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleTestConnections = async () => {
    setLoading(true);
    setError(null);
    setTestResult(null);
    try {
      const result = await testAllAiConnections();
      setTestResult(result);
    } catch (err: any) {
      setError(err.message || 'Erro ao executar o teste de conexões AI.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <h1>Testar Conexões de IA</h1>
      <p>Clique no botão abaixo para testar a conectividade com todas as APIs de Inteligência Artificial.</p>
      
      <button onClick={handleTestConnections} disabled={loading}>
        {loading ? 'Testando...' : 'Executar Teste de Conexões AI'}
      </button>

      {error && (
        <div style={{ color: 'red', marginTop: '20px' }}>
          <h3>Erro no Teste:</h3>
          <p>{error}</p>
        </div>
      )}

      {testResult && (
        <div style={{ marginTop: '20px', textAlign: 'left', maxWidth: '600px', margin: '20px auto', border: '1px solid #ccc', padding: '15px', backgroundColor: '#f9f9f9' }}>
          <h3>Resultado do Teste:</h3>
          <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
            {JSON.stringify(testResult, null, 2)}
          </pre>
        </div>
      )}

      <div style={{ marginTop: '20px' }}>
        <a href="/admin/dashboard">Voltar ao Painel Admin</a>
      </div>
    </div>
  );
};

export default TestConnectionsPage;