// src/components/common/Button.tsx
import React from 'react';
import '../../App.css'; // Usando o CSS global para estilos básicos

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'danger'; // Opcional: para diferentes estilos de botão
}

const Button: React.FC<ButtonProps> = ({ children, variant = 'primary', ...props }) => {
  const className = `button ${variant}`; // Adiciona classes CSS baseadas na variante
  return (
    <button className={className} {...props}>
      {children}
    </button>
  );
};

export default Button;

// No seu App.css, você precisaria adicionar estilos como:
/*
.button {
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.button.primary {
  background-color: #007bff;
  color: white;
}

.button.secondary {
  background-color: #6c757d;
  color: white;
}

.button.danger {
  background-color: #dc3545;
  color: white;
}

.button:hover {
  opacity: 0.9;
}
*/