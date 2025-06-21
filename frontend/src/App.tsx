import { useState, useEffect } from 'react';
import './App.css'; // Mantenha ou ajuste se tiver seu próprio CSS

function App() {
  const [backendMessage, setBackendMessage] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchBackendMessage = async () => {
      try {
        const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

        const response = await fetch(`${API_BASE_URL}/`); // Faz a requisição para a rota raiz do seu backend
        if (!response.ok) {
          throw new Error(`Erro HTTP: ${response.status} ${response.statusText}`);
        }
        const data = await response.json();
        setBackendMessage(data.message);
      } catch (err) {
        console.error("Erro ao buscar mensagem do backend:", err);
        if (err instanceof Error) {
          setError(`Falha ao conectar com o backend: ${err.message}. Verifique se o backend está rodando em ${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}`);
        } else {
          setError("Falha ao conectar com o backend: Erro desconhecido.");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchBackendMessage();
  }, []); // O array vazio garante que o useEffect rode apenas uma vez, no montagem do componente

  if (loading) {
    return <div className="App">Carregando mensagem do backend...</div>;
  }

  if (error) {
    return <div className="App" style={{ color: 'red' }}>Erro: {error}</div>;
  }

  return (
    <div className="App">
      <h1>Mensagem do seu Backend:</h1>
      <p>{backendMessage}</p>
      <p>Se você vê a mensagem acima, a integração frontend-backend está funcionando!</p>
      <p>Agora você pode começar a construir sua interface de usuário aqui.</p>
    </div>
  );
}

export default App;