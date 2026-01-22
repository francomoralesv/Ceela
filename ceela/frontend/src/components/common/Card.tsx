import React from "react";

interface CardProps {
  children: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
  marginTop?: string;
}

const Card: React.FC<CardProps> = ({ children, className = "", style }) => {
  const cardStyle: React.CSSProperties = {
    border: 'none',
    overflow: 'hidden',
    boxShadow: '0 0 40px rgba(8, 21, 66, 0.05)',
    borderRadius: '12px !important',
    transition: 'all 0.3s ease',
    ...style,
  };
  return <div className="col-xxl-12 col-xl-12 box-col-12 order-xl-1 col-sm-12 col-md-12 pb-2 ">
    <div className={`card rounded-2 mb-2 ${className}`} style={cardStyle}>
      <div className={"card-body pb-0 pt-0 my-2 "}>
        {children}
      </div>
    </div>
  </div>

};

export default Card;
