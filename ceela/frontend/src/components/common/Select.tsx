import React from 'react';

interface SelectProps {
  label: string;
  options: { value: string; label: string }[];
  value: string;
  onChange: (e: React.ChangeEvent<HTMLSelectElement>) => void;
  className?: string;
}

const Select: React.FC<SelectProps> = ({ label, options, value, onChange, className }) => {
  return (
    <div className="mb-3">
      <label className="form-label">{label}</label>
      <select value={value} onChange={onChange} className={`form-select ${className}`}>
        <option value="">Seleccione una opción</option>
        {options.map((opt, index) => (
          <option key={index} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
};

export default Select;
