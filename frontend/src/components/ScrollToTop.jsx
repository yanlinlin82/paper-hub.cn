import React, { useState, useEffect } from 'react';

function ScrollToTop() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setVisible(window.scrollY > 300);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  if (!visible) return null;

  return (
    <a
      href="#top"
      onClick={(e) => {
        e.preventDefault();
        scrollToTop();
      }}
      style={{
        position: 'fixed',
        bottom: '20px',
        right: '20px',
        zIndex: 999,
        width: '40px',
        height: '40px',
        borderRadius: '50%',
        backgroundColor: '#6c757d',
        color: 'white',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        textDecoration: 'none',
        opacity: 0.8,
      }}
    >
      ↑
    </a>
  );
}

export default ScrollToTop;
