import React from 'react';

interface ProgressBarProps {
    label: string;
    value: number;
    max: number;
    variant?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({ label, value, max, variant = "primary" }) => {
    const percentage = max > 0 ? Math.round((value / max) * 100) : 0;

    return (
        <div className="mb-2">
            <div className="d-flex justify-content-between align-items-center mb-1">
                <small>{label}</small>
                <small>{value}/{max} ({percentage}%)</small>
            </div>
            <div className="progress" style={{ height: "10px" }}>
                <div
                    className={`progress-bar bg-${variant}`}
                    role="progressbar"
                    style={{ width: `${percentage}%` }}
                    aria-valuenow={value}
                    aria-valuemin={0}
                    aria-valuemax={max}
                ></div>
            </div>
        </div>
    );
};
