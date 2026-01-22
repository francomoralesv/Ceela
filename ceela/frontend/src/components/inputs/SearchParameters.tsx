import React from "react";
import CustomButton from "../common/CustomButton";

interface SearchParametersProps {
  value: string;
  onChange: (newValue: string) => void;
  placeholder: string;
  onNew: () => void;
  newButtonText?: string;
  style?: React.CSSProperties;
  showNewButton?: boolean;
}

const SearchParameters: React.FC<SearchParametersProps> = ({
  value,
  onChange,
  placeholder,
  onNew,
  newButtonText = "Nuevo",
  style,
  showNewButton = true,
}) => {
  return (
    <div className="row g-2 align-items-center" style={style}>
      {/* Columna para el input */}
      <div className="col-12 col-md">
        <input
          type="text"
          className="form-control"
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          style={{ height: "40px" }}
        />
      </div>

      {/* Columna para el botón, solo si se muestra el botón Nuevo */}
      {showNewButton && (
        <div className="col-12 col-md-auto d-flex justify-content-center justify-content-md-start">
          <CustomButton variant="save" onClick={onNew} style={{ height: "40px" }}>
            <span className="material-icons">add</span> {newButtonText}
          </CustomButton>
        </div>
      )}
    </div>
  );
};

export default SearchParameters;
