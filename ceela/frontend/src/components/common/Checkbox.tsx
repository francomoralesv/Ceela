import React from 'react';
import { Tooltip } from 'react-tooltip';

interface CheckboxProps {
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  tooltip?: string;
}

const Checkbox: React.FC<CheckboxProps> = ({ label, checked, onChange, tooltip }) => {
  const tooltipId = `checkbox-tooltip-${label}`;

  return (
    <div className="form-check form-switch">
      <input
        type="checkbox"
        id={label}
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="form-check-input small-input"
        role="switch"
        data-tooltip-id={tooltipId}
        data-tooltip-content={tooltip}
      />
      <label 
        htmlFor={label} 
        className="form-check-label ms-2"
        data-tooltip-id={tooltipId}
        data-tooltip-content={tooltip}
      >
        {label}
      </label>
      {tooltip && (
        <Tooltip 
          id={tooltipId}
          place="top"
          className="custom-tooltip"
        />
      )}
      <style jsx>{`
        .form-check-input {
          width: 3em;
          height: 1.5em;
          cursor: pointer;
          transition: all 0.3s ease-in-out;
        }
        
        .form-check-input:checked {
          background-color: var(--primary-color);
          border-color: var(--primary-color);
        }

        .form-check-input:focus {
          border-color: var(--primary-color);
          box-shadow: 0 0 0 0.25rem rgba(var(--primary-color-rgb), 0.25);
        }

        .form-check-label {
          cursor: pointer;
          user-select: none;
        }

        .form-switch .form-check-input {
          background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='-4 -4 8 8'%3e%3ccircle r='3' fill='rgba%280, 0, 0, 0.25%29'/%3e%3c/svg%3e");
        }

        .form-switch .form-check-input:checked {
          background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='-4 -4 8 8'%3e%3ccircle r='3' fill='%23fff'/%3e%3c/svg%3e");
        }

        .form-check.form-switch {
          display: flex;
          align-items: center;
          justify-content: center;
        }

        :global(.custom-tooltip) {
          z-index: 9999;
          background-color: #333;
          color: white;
          padding: 5px 10px;
          border-radius: 4px;
          font-size: 14px;
        }
      `}</style>
    </div>
  );
};

export default Checkbox;