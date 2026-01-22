import React from 'react';

interface CancelButtonProps {
  onClick: () => void;
  title?: string;
}

const CancelButton: React.FC<CancelButtonProps> = ({
  onClick,
  title = 'Cancel'
}) => {
  return (
    <>
      <button
        onClick={onClick}
        title={title}
        aria-label={title}
        className="btn btn-sm btn-danger mt-2 m-2 btn-small"
      >
        {/* <X size={16} /> */}Cancelar
      </button>
      <style jsx>{`
        .btn {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s ease-in-out;
          background-color: #dc3545 !important; /* Red background */
          border: none;
          font-size: 14px;
          border-radius: 8px;
          padding: 10px 16px;
          cursor: pointer;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          font-weight: 500;
          letter-spacing: 0.3px;
          min-width: max-content;
          white-space: normal;
          line-height: 1.5;
          height: auto;
          color: white;
        }

        .btn-borderless {
          background-color: transparent !important;
          padding: 8px;
          color: var(--btn-save-bg);
          box-shadow: none;
        }

        .btn-borderless:hover {
          background-color: rgba(0, 0, 0, 0.04) !important;
          color: var(--btn-save-hover-bg);
        }

        .btn-small {
          font-size: 13px;
          padding: 8px 12px;
        }

        .btn-large {
          padding: 12px 24px;
          font-size: 16px;
        }

        .btn:hover {
          background-color: #c82333 !important; /* Darker red on hover */
          transform: translateY(-1px);
          box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        }

        .btn:active {
          transform: translateY(1px);
          box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        }

        .btn-icon-content {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          transition: transform 0.2s ease;
          color: var(--primary-color);
        }

        .loading {
          animation: spin 1s linear infinite;
          display: inline-block;
          margin-right: 8px;
        }

        @keyframes spin {
          0% {
            transform: rotate(0deg);
          }
          100% {
            transform: rotate(360deg);
          }
        }

        .disabled {
          opacity: 0.65;
          cursor: not-allowed;
          pointer-events: none;
        }

        .btn-icon-only {
          background: transparent !important;
          border: none;
          padding: 0;
          box-shadow: none;
        }

        .btn-icon-only:hover {
          background: transparent !important;
          box-shadow: none !important;
        }

        .btn-icon-only:hover .btn-icon-content {
          transform: scale(1.1);
        }

        .btn-deleteIcon .btn-icon-content,
        .btn-deleteIcon {
          color: #dc3545 !important;
          background: transparent !important;
          border: none;
          padding: 0;
          box-shadow: none;
        }
        .btn-deleteIcon:hover .btn-icon-content,
        .btn-deleteIcon:hover {
          color: #dc3545 !important;
          background: transparent !important;
        }

        .btn-editIcon .btn-icon-content,
        .btn-editIcon {
          color: #2ab0c5 !important;
          background: transparent !important;
          border: none;
          padding: 0;
          box-shadow: none;
        }
        .btn-editIcon:hover .btn-icon-content,
        .btn-editIcon:hover {
          color: #2ab0c5 !important;
          background: transparent !important;
        }

        .btn-yellow {
          background-color: yellow !important;
          color: black !important;
        }

        .btn-yellow:hover {
          background-color: #ffd700 !important; /* Darker yellow */
        }

        .btn-orange {
          background-color: orange !important;
          color: white !important;
        }

        .btn-orange:hover {
          background-color: #ff8c00 !important; /* Darker orange */
        }
      `}</style>
    </>
  );
};

export default CancelButton;
