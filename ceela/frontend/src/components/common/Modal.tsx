import useIsClient from '@/utils/useIsClient';
import React, { useState, useEffect } from 'react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
  /** Título del modal */
  title?: string;
  /** Estilos personalizados para el contenedor del modal */
  modalStyle?: React.CSSProperties;
  /** Estilos personalizados para el overlay */
  overlayStyle?: React.CSSProperties;
}

const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  children,
  title,
  modalStyle,
  overlayStyle,
}) => {
  const isClient = useIsClient();
  const [windowWidth, setWindowWidth] = useState(isClient ? window.innerWidth : 0);

  useEffect(() => {
    if (!isClient) return;

    const handleResize = () => {
      setWindowWidth(window.innerWidth);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [isClient]);

  if (!isOpen) return null;

  // Estilos por defecto para el overlay (fondo semi-transparente)
  const defaultOverlayStyle: React.CSSProperties = {
    position: 'fixed',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1200,
    backdropFilter: 'blur(3px)',
    transition: 'all 0.3s ease-in-out',
  };

  // Estilos por defecto para el modal (con bordes redondeados)
  const defaultModalStyle: React.CSSProperties = {
    backgroundColor: '#fff',
    borderRadius: '12px',
    padding: '24px',
    position: 'relative',
    minWidth: '300px',
    maxWidth: '500px', // Reducido de 85% a un valor fijo más pequeño
    width: '100%',
    boxShadow: '0 10px 25px rgba(0,0,0,0.2)',
    transform: 'translateY(0)',
    transition: 'all 0.3s ease-in-out',
  };

  const responsiveModalStyle: React.CSSProperties = 
    isClient ? {
      ...(windowWidth < 1200 && {
      }),
      ...(windowWidth < 768 && {
        padding: '20px',
      }),
      ...(windowWidth < 480 && {
        margin: '10px',
        padding: '16px',
        borderRadius: '8px',
      })
    } : {};

  return (
    <div
      style={{ ...defaultOverlayStyle, ...overlayStyle }}
      onClick={onClose} // Cierra el modal al hacer clic en el overlay
    >
      <div
        style={{
          ...defaultModalStyle,
          ...responsiveModalStyle,
          ...modalStyle,
        }}
        onClick={(e) => e.stopPropagation()} // Evita cerrar el modal al hacer clic en su contenido
      >
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '16px',
            right: '16px',
            background: '#f0f0f0',
            border: 'none',
            cursor: 'pointer',
            fontSize: '18px',
            color: '#666',
            width: '32px',
            height: '32px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            borderRadius: '50%',
            transition: 'all 0.2s ease',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          }}
          aria-label="Cerrar modal"
        >
          ✕
        </button>
        {title && (
          <h4>{title}</h4>  
        )}
        {children}
      </div>
    </div>
  );
};

export default Modal;
