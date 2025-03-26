// src/pages/ProductList.js
import React, { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';

function ProductList() {
  const { categoryId } = useParams();
  const [books, setBooks] = useState([]);
  const [category, setCategory] = useState({});
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    setLoading(true);
    
    // Fetch category info
    fetch(`/api/categories/${categoryId}`)
      .then(res => res.json())
      .then(data => setCategory(data));
    
    // Fetch books for this category
    fetch(`/api/categories/${categoryId}/products`)
      .then(res => res.json())
      .then(data => {
        setBooks(data);
        setLoading(false);
      });
  }, [categoryId]);

  if (loading) {
    return <div className="loading">Loading books...</div>;
  }

  return (
    <div className="product-list">
      <div className="category-header">
        <h1>{category.name}</h1>
        <p>{category.description}</p>
      </div>
      
      {books.length === 0 ? (
        <p className="no-books">No books found in this category.</p>
      ) : (
        <div className="books-grid">
          {books.map(book => (
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
      )}
    </div>
  );
}

export default ProductList;