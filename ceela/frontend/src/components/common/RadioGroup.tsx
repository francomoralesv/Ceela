import React from 'react';

interface RadioGroupProps {
  options: { label: string; value: string }[];
  name: string;
  selectedValue: string;
  onChange: (value: string) => void;
}

const RadioGroup: React.FC<RadioGroupProps> = ({ options, name, selectedValue, onChange }) => {
  return (
    <div className="mb-3">
      {options.map((option) => (
        <div key={option.value} className="form-check">
          <input
            type="radio"
            id={option.value}
            name={name}
            value={option.value}
            checked={selectedValue === option.value}
            onChange={(e) => onChange(e.target.value)}
            className="form-check-input"
          />
          <label htmlFor={option.value} className="form-check-label">
            {option.label}
          </label>
        </div>
      ))}
    </div>
  );
};

export default RadioGroup;
