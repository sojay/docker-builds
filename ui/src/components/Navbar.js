// src/components/Navbar.js
import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);
  
  return (
    <nav className="navbar">
      <div className="logo">
        <Link to="/">
          <span className="logo-text">Prepare.sh Book Shop</span>
        </Link>
      </div>
      
      <div className="mobile-menu-button" onClick={() => setMenuOpen(!menuOpen)}>
        <span>☰</span>
      </div>
      
      <div className={`nav-links ${menuOpen ? 'open' : ''}`}>
        <Link to="/category/classics" onClick={() => setMenuOpen(false)}>Classics</Link>
        <Link to="/category/modern" onClick={() => setMenuOpen(false)}>Modern</Link>
        <Link to="/category/poetry" onClick={() => setMenuOpen(false)}>Poetry</Link>
        <Link to="/category/fiction" onClick={() => setMenuOpen(false)}>Fiction</Link>
      </div>
      
      <div className="cart-icon">
        <Link to="/cart">
          <span className="material-icons">shopping_cart</span>
        </Link>
      </div>
    </nav>
  );
}

export default Navbar;