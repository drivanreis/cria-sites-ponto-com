// src/components/layout/Footer.tsx
import React from 'react';
import '../../App.css'; // Usando o CSS global por enquanto

const Footer: React.FC = () => {
  return (
    <footer className="app-footer">
      <p>&copy; {new Date().getFullYear()} Cria Sites .com. Todos os direitos reservados.</p>
    </footer>
  );
};

export default Footer;
