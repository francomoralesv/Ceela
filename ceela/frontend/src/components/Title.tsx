import React from "react";

interface TitleProps {
  text: string;
  fontSize?: string; // Permite configurar el tamaño de fuente de forma personalizada
  variant?: "title" | "subtitle"; // Permite definir si es un título principal o un subtítulo
  className?: string; // Clases adicionales para personalizar
}

const Title: React.FC<TitleProps> = ({ text, fontSize, variant = "title", className }) => {
  // Define tamaños de fuente por defecto según el variant
  const defaultFontSize = variant === "subtitle" ? "1rem" : "1.25rem";

  return (
    <div className="col-sm-6 p-0 mt-0">
      <h4
        className={`title font-weight-bold ${className || ""}`}
        style={{ fontSize: fontSize || defaultFontSize }}
      >
        {text}
      </h4>
    </div>
  );
};

export default Title;
