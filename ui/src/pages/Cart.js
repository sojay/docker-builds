// src/pages/Cart.js
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

function Cart() {
  const [cartItems, setCartItems] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    setLoading(true);
    fetch('/api/cart')
      .then(res => res.json())
      .then(data => {
        setCartItems(data);
        setLoading(false);
      });
  }, []);

  const updateQuantity = (itemId, newQuantity) => {
    if (newQuantity < 1) return;
    
    fetch('/api/cart/update', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        itemId,
        quantity: newQuantity
      }),
    }).then(() => {
      setCartItems(cartItems.map(item => 
        item.id === itemId ? {...item, quantity: newQuantity} : item
      ));
    });
  };

  const removeItem = (itemId) => {
    fetch(`/api/cart/remove/${itemId}`, { method: 'DELETE' })
      .then(() => {
        setCartItems(cartItems.filter(item => item.id !== itemId));
      });
  };

  const checkout = () => {
    fetch('/api/cart/checkout', { method: 'POST' })
      .then(() => {
        setCartItems([]);
        alert('Thank you for your purchase!');
      });
  };

  const total = cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);

  if (loading) {
    return <div className="loading">Loading cart...</div>;
  }

  return (
    <div className="cart">
      <h1>Your Shopping Cart</h1>
      
      {cartItems.length === 0 ? (
        <div className="empty-cart">
          <p>Your cart is empty</p>
          <Link to="/" className="continue-shopping">Continue Shopping</Link>
        </div>
      ) : (
        <>
          <div className="cart-items">
            {cartItems.map(item => (
              <div key={item.id} className="cart-item">
                <div className="item-image">
                  <img src={item.imageUrl} alt={item.name} />
                </div>
                <div className="item-details">
                  <h3>{item.name}</h3>
                  <p className="author">{item.author}</p>
                  <p className="price">${item.price.toFixed(2)}</p>
                </div>
                <div className="item-quantity">
                  <button onClick={() => updateQuantity(item.id, item.quantity - 1)}>−</button>
                  <span>{item.quantity}</span>
                  <button onClick={() => updateQuantity(item.id, item.quantity + 1)}>+</button>
                </div>
                <div className="item-total">
                  ${(item.price * item.quantity).toFixed(2)}
                </div>
                <button className="remove-item" onClick={() => removeItem(item.id)}>
                  <span className="material-icons">delete</span>
                </button>
              </div>
            ))}
          </div>
          
          <div className="cart-summary">
            <div className="summary-row">
              <span>Subtotal:</span>
              <span>${total.toFixed(2)}</span>
            </div>
            <div className="summary-row">
              <span>Shipping:</span>
              <span>Free</span>
            </div>
            <div className="summary-row total">
              <span>Total:</span>
              <span>${total.toFixed(2)}</span>
            </div>
            <button onClick={checkout} className="checkout-button">Proceed to Checkout</button>
            <Link to="/" className="continue-shopping">Continue Shopping</Link>
          </div>
        </>
      )}
    </div>
  );
}

export default Cart;