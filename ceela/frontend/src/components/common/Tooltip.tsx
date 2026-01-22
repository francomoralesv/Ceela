import React from 'react';

interface TooltipProps {
  text: string;
  position?: 'top' | 'right' | 'bottom' | 'left';
  children: React.ReactNode;
}

const Tooltip: React.FC<TooltipProps> = ({ text, position = 'top', children }) => {
  return (
    <div className="d-inline-block position-relative">
      <span className={`tooltip bs-tooltip-${position}`} role="tooltip">
        {text}
      </span>
      {children}
    </div>
  );
};

export default Tooltip;
