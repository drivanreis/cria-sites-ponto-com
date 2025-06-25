
// src/pages/auth/RegisterPage.tsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { loginUser as apiLoginUser } from '../../api/auth'; // Reuso do loginUser para exemplo pós-registro
// IMPORTANTE: Sua API Swagger mostra uma rota POST /users/ para criar NOVO USUÁRIO.
// Você precisará de uma função correspondente em src/api/users.ts para `createUser`.
import '../../App.css';

const RegisterPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleRegister = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    setSuccessMessage(null);

    if (password !== confirmPassword) {
      setError("As senhas não coincidem.");
      return;
    }

    // AQUI VOCÊ CHAMARIA A FUNÇÃO DA API PARA CRIAR O USUÁRIO
    // Exemplo HIPOTÉTICO, você precisaria implementar `createUser` em `src/api/users.ts`
    /*
    import { createUser } from '../../api/users';
    try {
      await createUser({ username, email, password });
      setSuccessMessage('Cadastro realizado com sucesso! Redirecionando para o login...');
      setTimeout(() => navigate('/login'), 2000);
    } catch (err: any) {
      setError(err.message || "Erro ao tentar registrar.");
    }
    */
    
    // POR ENQUANTO, como não temos o `createUser` aqui, vamos simular:
    console.log("Tentando registrar:", { username, email, password });
    setSuccessMessage('Cadastro simulado com sucesso! Redirecionando para o login...');
    setTimeout(() => navigate('/login'), 2000);
  };

  return (
    <div className="App">
      <h1>Cadastre-se</h1>
      <form onSubmit={handleRegister} style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxWidth: '300px', margin: '20px auto' }}>
        <div>
          <label htmlFor="regUsername">Usuário:</label>
          <input
            type="text"
            id="regUsername"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div>
          <label htmlFor="regEmail">Email:</label>
          <input
            type="email"
            id="regEmail"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div>
          <label htmlFor="regPassword">Senha:</label>
          <input
            type="password"
            id="regPassword"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <div>
          <label htmlFor="confirmPassword">Confirmar Senha:</label>
          <input
            type="password"
            id="confirmPassword"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />
        </div>
        {error && <p style={{ color: 'red' }}>{error}</p>}
        {successMessage && <p style={{ color: 'green' }}>{successMessage}</p>}
        <button type="submit">Cadastrar</button>
      </form>
      <p>
        Já tem uma conta? <a href="/login">Faça Login aqui</a>
      </p>
    </div>
  );
};

export default RegisterPage;