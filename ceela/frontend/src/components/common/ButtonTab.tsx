import React from 'react';

interface ButtonTabProps {
    label: string;
    active: boolean;
    onClick: () => void;
    primaryColor?: string;
    className?: string;
}

const ButtonTab: React.FC<ButtonTabProps> = ({
    label,
    active,
    onClick,
    primaryColor = '#007bff',
    className = '',
}) => {
    return (
        <button
            className={`w-100 py-3 px-2 ${className}`}
            style={{
            backgroundColor: "#fff",
            color: active ? primaryColor : "var(--secondary-color)",
            border: active ? `1px solid ${primaryColor}` : "1px solid transparent",
            borderBottom: active ? `2px solid ${primaryColor}` : "none",
            borderRadius: "8px",
            transition: "all 0.3s ease",
            boxShadow: active ? `0 1px 2px rgba(0,0,0,0.05)` : "none"
            }}
            onClick={onClick}
        >
            {label}
        </button>
    );
};

export default ButtonTab;