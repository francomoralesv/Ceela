import React from 'react';
interface BadgeProps {
  text: string;
  type?: 'success' | 'danger' | 'warning' | 'info';
}

const Badge: React.FC<BadgeProps> = ({ text, type = 'info' }) => {
  return <span className={`badge bg-${type} p-2`}>{text}</span>;
};

export default Badge;
