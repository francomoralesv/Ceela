import React from "react";
import AcceptCancelButtons from "../src/components/common/ActionButtonsConfirm";



const TestPage: React.FC = () => {
  const handleAccept = () => {
    alert("¡Has aceptado!");
  };

  const handleCancel = () => {
    alert("¡Has cancelado!");
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Página de Prueba</h1>
      <p>Prueba las acciones de aceptar y cancelar haciendo clic en los botones:</p>
      <AcceptCancelButtons onAccept={handleAccept} onCancel={handleCancel} />
    </div>
  );
};

export default TestPage;
