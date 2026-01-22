import React from "react";

interface SidebarItemComponentProps {
  stepNumber: number;
  iconName: string;
  title: string;
  activeStep: number;
  onClickAction?: () => void;
}

const SidebarItemComponent: React.FC<SidebarItemComponentProps> = ({
  stepNumber,
  iconName,
  title,
  activeStep,
  onClickAction,
}) => {
  const primaryColor = "#3ca7b7";
  const inactiveColor = "#ccc";
  const isActive = activeStep === stepNumber;

  // Constantes de dimensiones
  const internalSidebarWidth = 380;
  const sidebarItemHeight = 100;
  const sidebarItemBorderSize = 1;
  const leftPadding = 50;

  return (
    <>
      <li
        className="sidebar-item"
        style={{
          cursor: "pointer",
          width: `${internalSidebarWidth}px`,
          padding: "20px",
          boxSizing: "border-box",
          borderRight: `1px solid ${inactiveColor}`, // Borde derecho (puedes quitarlo si no lo deseas)
          fontSize: "0.9rem",
        }}
        onClick={onClickAction}
      >
        <div
          className={`sidebar-item-content ${isActive ? "active" : ""}`}
          style={{
            width: "100%",
            height: `${sidebarItemHeight * 0.7}px`,
            // El borde del contenedor cambia según si está activo o no
            border: `${sidebarItemBorderSize}px solid ${
              isActive ? primaryColor : inactiveColor
            }`,
            borderRadius: "4px",
            marginBottom: "-1.8rem",
            display: "flex",
            alignItems: "center",
            justifyContent: "flex-start",
            paddingLeft: `${leftPadding * 0.8}px`,
            // Color del texto e icono (si no quieres que el icono herede este color,
            // lo puedes manejar aparte en el CSS)
            color: isActive ? primaryColor : inactiveColor,
            fontFamily: "var(--font-family-base)",
            position: "relative",
            overflow: "hidden",
            fontSize: "0.8rem",
            fontWeight: "normal",
          }}
        >
          <span
            className="icon-wrapper"
            style={{ marginRight: "15px", fontSize: "2rem" }}
          >
            <span className="material-icons">{iconName}</span>
          </span>
          <span className="title-wrapper">{title}</span>
        </div>
      </li>
      <style jsx global>{`
        /* Animación de aparición */
        @keyframes sidebarItemAppear {
          0% {
            opacity: 0;
            transform: translateX(-30px) scale(0.9);
          }
          60% {
            transform: translateX(5px) scale(1.02);
          }
          100% {
            opacity: 1;
            transform: translateX(0) scale(1);
          }
        }

        .sidebar-item {
          perspective: 1000px;
          transform-style: preserve-3d;
          animation: sidebarItemAppear 0.8s cubic-bezier(0.34, 1.56, 0.64, 1)
            forwards;
          animation-delay: calc(var(--item-index, 0) * 0.1s);
        }

        .sidebar-item-content {
          transform: translateX(0) translateZ(0);
          transition: transform 0.3s ease-out, box-shadow 0.3s ease-out;
        }

        /* Efecto hover: se desplaza a la derecha y un poco hacia el frente */
        .sidebar-item-content:hover {
          transform: translateX(8px) translateZ(10px);
          box-shadow: 0 4px 25px rgba(60, 167, 183, 0.1),
            0 1px 5px rgba(0, 0, 0, 0.1);
        }

        /* Efecto presionado: solo mientras se mantiene el click */
        .sidebar-item:active .sidebar-item-content {
          transform: translateX(8px) translateY(10px) translateZ(10px);
        }

        /* -- Cuando está activo, le damos el borde circular al ícono -- */
        /* -- Cuando está activo, le damos el borde circular y fondo relleno al ícono -- */
        .sidebar-item-content.active .icon-wrapper {
          border: 2px solid ${primaryColor};
          border-radius: 50%;
          padding: 5px;
          background: ${primaryColor}; /* Fondo relleno del color primario */
          color: #fff; /* Ícono en color blanco */
        }

        .icon-wrapper {
          transition: transform 0.3s ease-out, filter 0.3s ease-out;
          transform-origin: center;
        }

        .sidebar-item-content:hover .icon-wrapper {
          transform: scale(1.2) rotate(8deg);
          filter: drop-shadow(0 2px 4px rgba(60, 167, 183, 0.3));
        }

        .title-wrapper {
          transition: transform 0.3s ease-out, letter-spacing 0.3s ease-out;
          transform-origin: left;
          position: relative;
        }

        .title-wrapper::before {
          content: "";
          position: absolute;
          left: 0;
          bottom: -2px;
          width: 100%;
          height: 2px;
          background: ${primaryColor};
          transform: scaleX(0);
          transition: transform 0.3s ease;
          transform-origin: right;
        }

        .sidebar-item-content:hover .title-wrapper {
          transform: translateX(5px) scale(1.02);
          letter-spacing: 0.2px;
        }

        .sidebar-item-content:hover .title-wrapper::before {
          transform: scaleX(1);
          transform-origin: left;
        }
      `}</style>
    </>
  );
};

export default SidebarItemComponent;
