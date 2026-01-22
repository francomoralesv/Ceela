import React from 'react';

interface ButtonProps {
  text: string;
  onClick: () => void;
  type?: 'button' | 'submit' | 'reset';
  className?: string;
  disabled?: boolean;
  icon?: string;  
}

const Button: React.FC<ButtonProps> = ({ text, onClick, type = 'button', className = '', disabled = false, icon }) => {
  return (
    <button 
      type={type} 
      className={`btn ${className} ${disabled ? 'disabled' : ''}`} 
      onClick={onClick} 
      disabled={disabled}
    >
      {icon && <i className={`bi ${icon} me-2`}></i>}
      {text}
    </button>
  );
};

export default Button;
