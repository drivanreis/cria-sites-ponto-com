// src/pages/common/HomePage.tsx
import React, { useState, useEffect } from 'react';
import '../../App.css'; // Mantenha ou ajuste se tiver seu próprio CSS
import { useAuth } from '../../hooks/useAuth'; // Importa useAuth para mostrar o status

const HomePage: React.FC = () => {
  const [backendMessage, setBackendMessage] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
  const { isAuthenticated, userRole, logout } = useAuth(); // Obtém o status de autenticação

  useEffect(() => {
    const fetchBackendMessage = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/`, {
          headers: {
            'ngrok-skip-browser-warning': 'true',
            'Content-Type': 'application/json'
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
      <h1>Bem-vindo ao Cria Sites Ponto Com!</h1>
      <p>Se você vê a mensagem abaixo, a integração frontend-backend está funcionando!</p>
      <p>{backendMessage}</p>
      <p>Pelo endereço: {API_BASE_URL}</p>
      <p>Agora você pode começar a construir sua interface de usuário aqui.</p>

      {isAuthenticated ? (
        <div>
          <p>Você está logado como: {userRole}</p>
          <button onClick={logout}>Sair</button>
          {userRole === 'admin' ? (
              <p><a href="/admin/dashboard">Ir para o Painel Admin</a></p>
          ) : (
              <p><a href="/dashboard">Ir para o Dashboard</a></p>
          )}
        </div>
      ) : (
        <p><a href="/login">Faça Login</a> ou <a href="/cadastro">Cadastre-se</a> para continuar.</p>
      )}
    </div>
  );
};

export default HomePage;