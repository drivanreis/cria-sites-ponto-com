// src/components/layout/Navbar.tsx
import React from 'react';
import '../../App.css'; // Usando o CSS global por enquanto

const Navbar: React.FC = () => {
  // Esta Navbar pode ser usada para navegação específica de uma seção,
  // ou se você quiser uma barra de navegação principal separada do Header.
  // Por enquanto, o Header já contém os links principais.
  return (
    <nav className="app-navbar">
      {/* Exemplo: links específicos de uma sub-seção */}
      {/* <Link to="/produtos" className="nav-link">Produtos</Link>
      <Link to="/servicos" className="nav-link">Serviços</Link> */}
      <p>Navegação secundária (se necessário)</p>
    </nav>
  );
};

export default Navbar;
