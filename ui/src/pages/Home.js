// src/pages/Home.js
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

function Home() {
  const [categories, setCategories] = useState([]);
  const [featuredBooks, setFeaturedBooks] = useState([]);
  
  useEffect(() => {
    // Fetch categories
    fetch('/api/categories')
      .then(res => res.json())
      .then(data => setCategories(data));
    
    // Fetch featured books
    fetch('/api/products/featured')
      .then(res => res.json())
      .then(data => setFeaturedBooks(data));
  }, []);

  return (
    <div className="home">
      <div className="hero">
        <div className="hero-content">
          <h1>Welcome to Prepare.sh Book Shop</h1>
          <p>Discover the world through Russian literature</p>
          <Link to="/category/classics" className="cta-button">Explore Classics</Link>
        </div>
      </div>
      
      <section className="categories-section">
        <h2>Browse Categories</h2>
        <div className="categories-grid">
          {categories.map(category => (
            <Link to={`/category/${category.id}`} key={category.id} className="category-card">
              <div className="category-content">
                <h3>{category.name}</h3>
                <p>Explore →</p>
              </div>
            </Link>
          ))}
        </div>
      </section>
      
      <section className="featured-section">
        <h2>Featured Books</h2>
        <div className="featured-books">
          {featuredBooks.map(book => (
            <Link to={`/product/${book.id}`} key={book.id} className="book-card">
              <div className="book-cover">
                <img src={book.imageUrl} alt={book.name} />
              </div>
              <div className="book-info">
                <h3>{book.name}</h3>
                <p className="author">{book.author}</p>
                <p className="price">${book.price.toFixed(2)}</p>
              </div>
            </Link>
          ))}
        </div>
      </section>
      
      <section className="quote-section">
        <blockquote>
          "The soul is healed by being with children."
          <cite>— Fyodor Dostoevsky</cite>
        </blockquote>
      </section>
    </div>
  );
}

export default Home;