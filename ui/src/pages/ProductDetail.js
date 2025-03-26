// src/pages/ProductDetail.js
import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';

function ProductDetail() {
  const { productId } = useParams();
  const [book, setBook] = useState(null);
  const [loading, setLoading] = useState(true);
  const [quantity, setQuantity] = useState(1);
  
  useEffect(() => {
    setLoading(true);
    fetch(`/api/products/${productId}`)
      .then(res => res.json())
      .then(data => {
        setBook(data);
        setLoading(false);
      });
  }, [productId]);

  const addToCart = () => {
    // Send raw JSON data without the Content-Type header
    const jsonData = JSON.stringify({
      productId: productId,
      quantity: quantity
    });

    // Create a standard XMLHttpRequest to avoid automatic Content-Type setting
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/api/cart/add', true);
    
    // No Content-Type header is set here
    
    xhr.onload = function() {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const response = JSON.parse(xhr.responseText);
          if (response.success) {
            alert(`${book.name} added to cart!`);
          } else {
            alert('Error adding to cart: ' + (response.error || 'Unknown error'));
          }
        } catch (e) {
          alert('Error processing response');
          console.error('Error parsing response:', e);
        }
      } else {
        alert(`Error: ${xhr.status} - ${xhr.statusText}`);
      }
    };
    
    xhr.onerror = function() {
      alert('Network error occurred');
    };
    
    // Send the JSON data as a string
    xhr.send(jsonData);
  };

  if (loading) {
    return <div className="loading">Loading book details...</div>;
  }

  if (!book) {
    return <div className="not-found">Book not found</div>;
  }

  return (
    <div className="product-detail">
      <div className="book-image">
        <img src={book.imageUrl} alt={book.name} />
      </div>
      <div className="book-details">
        <h1>{book.name}</h1>
        <h2>by {book.author}</h2>
        <p className="price">${book.price.toFixed(2)}</p>
        
        <div className="book-description">
          <h3>Description</h3>
          <p>{book.description}</p>
        </div>
        
        <div className="book-meta">
          <div className="meta-item">
            <span>Category:</span> 
            <Link to={`/category/${book.categoryId}`}>{book.category}</Link>
          </div>
          <div className="meta-item">
            <span>Pages:</span> {book.pages}
          </div>
          <div className="meta-item">
            <span>Published:</span> {book.published}
          </div>
        </div>
        
        <div className="purchase-options">
          <div className="quantity-selector">
            <button 
              onClick={() => setQuantity(Math.max(1, quantity - 1))}
              disabled={quantity <= 1}
            >−</button>
            <span>{quantity}</span>
            <button onClick={() => setQuantity(quantity + 1)}>+</button>
          </div>
          <button onClick={addToCart} className="add-to-cart">Add to Cart</button>
        </div>
      </div>
    </div>
  );
}

export default ProductDetail;