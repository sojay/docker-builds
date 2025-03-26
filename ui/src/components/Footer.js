// src/components/Footer.js
import React from 'react';

function Footer() {
  return (
    <footer className="footer">
      <div className="footer-content">
        <div className="footer-section">
          <h3>Prepare.sh Book Shop</h3>
          <p>Your premier destination for Classic literature and beyond.</p>
        </div>
        <div className="footer-section">
          <h3>Contact</h3>
          <p>Email: info@prepare.sh</p>
          <p>Phone: +1 123-456-7890</p>
        </div>
        <div className="footer-section">
          <h3>Hours</h3>
          <p>Monday - Friday: 9am - 8pm</p>
          <p>Saturday - Sunday: 10am - 6pm</p>
        </div>
      </div>
      <div className="footer-bottom">
        <p>&copy; {new Date().getFullYear()} Prepare.sh Book Shop. All rights reserved.</p>
      </div>
    </footer>
  );
}

export default Footer;