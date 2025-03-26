// src/components/Hero.js
import React from 'react';
import { Link } from 'react-router-dom';

function Hero() {
  const heroStyle = {
    backgroundImage: `linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), url(${process.env.PUBLIC_URL}/images/books/hero-bg.jpg)`,
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    height: '500px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    textAlign: 'center',
    color: 'white',
    marginBottom: '50px'
  };

  return (
    <div className="hero" style={heroStyle}>
      <div className="hero-content">
        <h1>Welcome to Prepare.sh Book Shop</h1>
        <p>Discover the world through Russian literature</p>
        <Link to="/category/classics" className="cta-button">Explore Classics</Link>
      </div>
    </div>
  );
}

export default Hero;