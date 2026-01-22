import React from 'react';

interface DividerProps {
    className?: string;
}

const VerticalDivider: React.FC<DividerProps> = ({ className = '' }) => {
    return (
            <div className="d-none d-md-block" style={{
              width: '1px',
              backgroundColor: '#E5E7EB',
              marginLeft: '-1px',
              marginRight: '-1px'
            }}></div>
    );
};

export default VerticalDivider;