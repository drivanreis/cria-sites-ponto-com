// src/components/common/Input.tsx
import React from 'react';
import '../../App.css'; // Usando o CSS global para estilos básicos

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  id: string; // O ID é importante para acessibilidade e associação com o label
}

const Input: React.FC<InputProps> = ({ label, id, ...props }) => {
  return (
    <div style={{ marginBottom: '10px' }}>
      {label && <label htmlFor={id} style={{ display: 'block', marginBottom: '5px' }}>{label}:</label>}
      <input
        id={id}
        className="input-field" // Adicione uma classe para estilização via CSS
        {...props}
        style={{ padding: '8px', border: '1px solid #ccc', borderRadius: '4px', width: '100%', boxSizing: 'border-box' }}
      />
    </div>
  );
};

export default Input;
