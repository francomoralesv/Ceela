import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer 
      className="app-footer"
      style={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        backgroundColor: 'rgba(248, 249, 250, 0.7)',
        backdropFilter: 'blur(8px)',
        borderTop: '1px solid rgba(0, 0, 0, 0.08)',
        padding: '8px 16px',
        fontSize: '11px',
        color: '#6c757d',
        textAlign: 'center',
        zIndex: 999,
        fontFamily: 'system-ui, -apple-system, sans-serif',
        opacity: 0.8
      }}
    >
      <span>Desarrollado por Deuman® con colaboración de E3 Ingeniería</span>
    </footer>
  );
};

export default Footer;
