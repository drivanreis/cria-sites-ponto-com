import { useState, useEffect } from 'react';
import '../../App.css';

function App() {
  const [backendMessage, setBackendMessage] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL // Equivalente 'http://localhost:8000';

  useEffect(() => {
    const fetchBackendMessage = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/`, {
          // *** AQUI É ONDE ADICIONAMOS O CABEÇALHO ***
          headers: {
            'ngrok-skip-browser-warning': 'true', // Este cabeçalho diz ao ngrok para pular a página de aviso
            'Content-Type': 'application/json' // Geralmente é bom incluir para APIs JSON
          }
        });

        if (!response.ok) {
          throw new Error(`Erro HTTP: ${response.status} ${response.statusText}`);
        }
        const data = await response.json();
        setBackendMessage(data.message);
      } catch (err) {
        console.error("Erro ao buscar mensagem do backend:", err);
        if (err instanceof Error) {
          setError(`Falha ao conectar com o backend: ${err.message}. Verifique se o backend está rodando em API_BASE_URL: ${API_BASE_URL}`);
        } else {
          setError("Falha ao conectar com o backend: Erro desconhecido.");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchBackendMessage();
  }, [API_BASE_URL]);

  if (loading) {
    return <div className="App">Carregando mensagem do backend...</div>;
  }

  if (error) {
    return <div className="App" style={{ color: 'red' }}>Erro: {error}</div>;
  }

  return (
    <div className="App">
      <h1>Bem-vindo!</h1>
      <h2> ao Cria Sites Ponto Com!</h2>
      <p>Se você vê a mensagem abaixo, a integração frontend-backend está funcionando!</p>
      <p>{backendMessage}</p>
      <p>Pelo endereço: {API_BASE_URL}</p>
      <p>Agora você pode começar a construir sua interface de usuário aqui.</p>
    </div>
  );
}

export default App;