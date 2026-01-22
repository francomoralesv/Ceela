import React from 'react';
import { useRouter } from 'next/router';
import { Tooltip } from 'react-tooltip';
import CustomButton from './common/CustomButton';
import { ArrowLeft, Save } from 'lucide-react';

interface CreateButtonProps {
  backRoute?: string;
  useRouterBack?: boolean; // Si es true, se usará router.back() en vez de router.push
  backText?: string;       // Si se proporciona, se mostrará en el botón; de lo contrario, se muestra el ícono de flecha
  onSaveClick?: () => void;
  submitType?: boolean;
  saveText?: string;
  backTooltip?: string;
  saveTooltip?: string;
}

const CreateButton: React.FC<CreateButtonProps> = ({
  backRoute = "/",
  useRouterBack = false,
  backText,
  onSaveClick,
  submitType = true,
  saveText = "Crear",
  backTooltip = "Volver",
  saveTooltip = "Guardar",
}) => {
  const router = useRouter();

  const handleSaveClick = (e: React.MouseEvent) => {
    if (!submitType && onSaveClick) {
      e.preventDefault();
      onSaveClick();
    }
  };

  const handleBackClick = () => {
    if (useRouterBack) {
      router.back();
    } else {
      router.push(backRoute);
    }
  };

  // Estilos para que la altura sea fija y el ancho se ajuste al contenido
  const buttonStyle = {
    height: "40px",          // Altura fija
    padding: "0 20px",       // Espaciado horizontal para que se ajuste al contenido
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  };

  return (
    <div className="d-flex gap-2">
      <div data-tip={backTooltip}>
        <CustomButton
          type="button"
          onClick={handleBackClick}
          style={buttonStyle}
          color='red'
        >
          {backText ? backText : <ArrowLeft className="w-4 h-4 mr-1" />}
        </CustomButton>
      </div>
      
      <div data-tip={saveTooltip}>
        <CustomButton
          type={submitType ? "submit" : "button"}
          variant="save"
          onClick={!submitType ? handleSaveClick : undefined}
          style={buttonStyle}
        >
          <Save className="w-4 h-4 mr-1" />
          <span className="d-none d-sm-inline">{saveText}</span>
        </CustomButton>
      </div>
      
      <Tooltip />
    </div>
  );
};

export default CreateButton;
