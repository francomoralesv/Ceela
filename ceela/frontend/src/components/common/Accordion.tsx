import React, { useState } from 'react';

interface AccordionProps {
  title: string;
  children: React.ReactNode;
}

const Accordion: React.FC<AccordionProps> = ({ title, children }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="accordion-item mb-3">
      <div
        className="accordion-header p-3 bg-primary text-white"
        style={{ cursor: 'pointer' }}
        onClick={() => setIsOpen(!isOpen)}
      >
        {title}
        <i className={`bi ${isOpen ? 'bi-chevron-up' : 'bi-chevron-down'} float-end`}></i>
      </div>
      {isOpen && <div className="accordion-body p-3 border">{children}</div>}
    </div>
  );
};

export default Accordion;
