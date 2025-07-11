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
