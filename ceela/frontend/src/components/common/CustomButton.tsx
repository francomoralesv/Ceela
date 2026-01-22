import { LucideIcon } from 'lucide-react';
import GoogleIcons from 'public/GoogleIcons';
import React, { ButtonHTMLAttributes, FC } from 'react';
import { Tooltip } from 'react-tooltip';

interface CustomButtonProps extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'type'> {
  variant?:
  | 'save'
  | 'back'
  | 'delete'
  | 'editIcon'
  | 'deleteIcon'
  | 'backIcon'
  | 'forwardIcon'
  | 'addIcon'
  | 'listIcon'
  | 'cancelIcon'
  | 'viewIcon'
  | 'closed'
  | 'layersIcon'
  | 'borderless'
  | 'gray';
  type?: 'button' | 'submit';
  isLoading?: boolean;
  margin?: string;
  icon?: LucideIcon;
  iconSize?: number; 
  color?: 'yellow' | 'orange' | 'red' | 'gray'; 
}

const CustomButton: FC<CustomButtonProps> = ({
  variant = 'save',
  isLoading = false,
  children,
  className = '',
  disabled,
  margin = '0.5rem',
  icon: Icon,
  iconSize = 24, // Puedes cambiar el valor por defecto aquí
  type = 'button',
  color,
  ...rest
}) => {
  const renderAnimatedIcon = (iconName: string) => (
    <span
      className="btn-icon-content material-icons animate__animated"
      onMouseEnter={(e) => e.currentTarget.classList.add('animate__pulse')}
      onAnimationEnd={(e) => e.currentTarget.classList.remove('animate__pulse')}
      style={{ fontSize: `${iconSize}px` }}
    >
      {iconName}
    </span>
  );

  let content: React.ReactNode = children;
  let tooltipText = '';

  if (variant === 'editIcon') {
    content = renderAnimatedIcon('edit');
    tooltipText = 'Editar';
  } else if (variant === 'deleteIcon') {
    content = renderAnimatedIcon('delete');
    tooltipText = 'Eliminar';
  } else if (variant === 'backIcon') {
    content = (
      <span className="btn-icon-content material-icons" style={{ fontSize: `${iconSize}px` }}>
        arrow_back
      </span>
    );
    tooltipText = 'Volver';
  } else if (variant === 'forwardIcon') {
    content = (
      <span className="btn-icon-content material-icons" style={{ fontSize: `${iconSize}px` }}>
        arrow_forward
      </span>
    );
    tooltipText = 'Siguiente';
  } else if (variant === 'addIcon') {
    content = (
      <span className="btn-icon-content material-icons" style={{ fontSize: `${iconSize}px` }}>
        add
      </span>
    );
    tooltipText = 'Agregar';
  } else if (variant === 'listIcon') {
    content = (
      <span className="btn-icon-content material-icons" style={{ fontSize: `${iconSize}px` }}>
        format_list_bulleted
      </span>
    );
    tooltipText = 'Ver lista';
  } else if (variant === 'layersIcon') {
    content = (
      <span className="btn-icon-content material-icons" style={{ fontSize: `${iconSize}px` }}>
        layers
      </span>
    );
    tooltipText = 'Ver lista';
  } else if (variant === 'cancelIcon') {
    content = (
      <span className="btn-icon-content material-icons" style={{ fontSize: `${iconSize}px` }}>
        close
      </span>
    );
    tooltipText = 'Cancelar';
  } else if (variant === 'viewIcon') {
    content = (
      <span className="btn-icon-content material-icons" style={{ fontSize: `${iconSize}px` }}>
        visibility
      </span>
    );
    tooltipText = 'Ver detalles';
  }

  // Determinamos si es un botón solo con ícono
  const isIconOnly = variant === 'editIcon' || variant === 'deleteIcon';

  // Asignamos clases específicas según el variant
  const variantClass =
    variant === 'deleteIcon'
      ? 'btn-icon-only btn-deleteIcon'
      : variant === 'editIcon'
        ? 'btn-icon-only btn-editIcon'
        : isIconOnly
          ? 'btn-icon-only'
          : variant === 'borderless'
            ? 'btn-borderless'
            : variant === 'gray'
              ? 'btn-gray'
              : `btn-${variant}`;

  const disabledClass = disabled || isLoading ? 'disabled' : '';
  const buttonId = variant === 'cancelIcon' ? 'grabar-datos-btn' : undefined;
  const colorClass = color === 'yellow' ? 'btn-yellow' : color === 'orange' ? 'btn-orange' : color === 'red' ? 'btn-red' : '';

  return (
    <>
      <GoogleIcons />
      <button
        id={buttonId}
        type={type}
        disabled={disabled || isLoading}
        aria-busy={isLoading}
        style={{ margin }}
        className={`button btn-small px-2 btn btn-primary ${variantClass} ${colorClass} ${className} ${disabledClass}`}
        title={tooltipText}
        {...rest}
      >
        {isLoading ? (
          <span className="loading">Cargando...</span>
        ) : (
          <>
            {Icon && <Icon size={iconSize} className="me-2" />}
            {content}
          </>
        )}
      </button>
      {variant === 'cancelIcon' && (
        <Tooltip anchorSelect={`#${buttonId}`} place="top">
          Cancelar
        </Tooltip>
      )}
      <style jsx>{`
        .btn {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s ease-in-out;
          background-color: var(--primary-color) !important;
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
          background-color: var(--btn-save-hover-bg) !important;
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

        .btn-red {
          background-color: red !important;
          color: white !important;
        }

        .btn-red:hover {
          background-color: #b22222 !important; /* Darker red */
        }

        .btn-gray {
          background-color: #6c757d !important;
          color: white !important;
        }

        .btn-gray:hover {
          background-color: #5a6268 !important; /* Darker gray */
        }

        .btn-gray:disabled {
          background-color: #adb5bd !important;
          color: #6c757d !important;
          cursor: not-allowed;
        }
      `}</style>
    </>
  );
};

export default CustomButton;
