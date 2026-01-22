import React from 'react';

interface StatsCardProps {
  title: string;
  value: string | number;
  icon?: string;
  color?: string;
}

const StatsCard: React.FC<StatsCardProps> = ({ title, value, icon, color = 'primary' }) => {
  return (
    <div className={`card text-white bg-${color} mb-3`} style={{ maxWidth: '18rem' }}>
      <div className="card-header">
        {icon && <i className={`bi ${icon} me-2`}></i>}
        {title}
      </div>
      <div className="card-body">
        <h5 className="card-title">{value}</h5>
      </div>
    </div>
  );
};

export default StatsCard;
