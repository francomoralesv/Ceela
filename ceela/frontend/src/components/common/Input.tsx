import React from 'react';

interface InputProps {
  label: string;
  type?: 'text' | 'email' | 'password' | 'number';
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
  className?: string;
}

const Input: React.FC<InputProps> = ({ label, type = 'text', value, onChange, placeholder, className }) => {
  return (
    <div className="mb-3">
      <label className="form-label">{label}</label>
      <input 
        type={type} 
        value={value} 
        onChange={onChange} 
        placeholder={placeholder}
        className={`form-control ${className}`} 
      />
    </div>
  );
};

export default Input;
