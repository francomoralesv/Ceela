// pages/test-toast.tsx
import React from "react";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const TestToast: React.FC = () => {
  // Notificación de éxito
  const notifySuccess = () => {
    toast.dismiss(); // Elimina notificaciones previas
    toast.success("¡Operación exitosa!", {
      autoClose: 2000,
      pauseOnHover: false,
    });
  };

  // Notificación de error
  const notifyError = () => {
    toast.dismiss();
    toast.error("¡Ocurrió un error!", {
      autoClose: 2000,
      pauseOnHover: false,
    });
  };

  // Notificación informativa
  const notifyInfo = () => {
    toast.dismiss();
    toast.info("Esta es una información.", {
      autoClose: 2000,
      pauseOnHover: false,
    });
  };

  // Notificación de advertencia
  const notifyWarning = () => {
    toast.dismiss();
    toast.warning("Advertencia: revise sus datos.", {
      autoClose: 2000,
      pauseOnHover: false,
    });
  };

  // Notificación por defecto
  const notifyDefault = () => {
    toast.dismiss();
    toast("Mensaje por defecto.", {
      autoClose: 2000,
      pauseOnHover: false,
    });
  };

  // Notificación personalizada con callback y sin auto-cierre
  const notifyCustom = () => {
    toast.dismiss();
    toast("Esta notificación tiene callback y no se cierra automáticamente.", {
      autoClose: false,
      onClick: () => alert("¡Haz hecho clic en la notificación!"),
    });
  };

  return (
    <div className="container">
      <div className="content">
        <h1>Prueba de Notificaciones</h1>
        <p>Presiona los botones para ver cada tipo de notificación:</p>
        <div className="buttons">
          <button onClick={notifySuccess}>Mostrar Éxito</button>
          <button onClick={notifyError}>Mostrar Error</button>
          <button onClick={notifyInfo}>Mostrar Información</button>
          <button onClick={notifyWarning}>Mostrar Advertencia</button>
          <button onClick={notifyDefault}>Mostrar Default</button>
          <button onClick={notifyCustom}>Mostrar Custom</button>
        </div>
      </div>
      <style jsx>{`
        .container {
          display: flex;
          align-items: center;
          justify-content: center;
          min-height: 100vh;
          background: #f0f2f5;
          padding: 20px;
        }
        .content {
          text-align: center;
          background: #fff;
          padding: 30px;
          border-radius: 8px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        h1 {
          margin-bottom: 10px;
          font-size: 2rem;
          color: #333;
        }
        p {
          margin-bottom: 20px;
          color: #555;
        }
        .buttons {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }
        button {
          padding: 10px 15px;
          font-size: 1rem;
          cursor: pointer;
          border: none;
          border-radius: 4px;
          transition: background 0.3s;
        }
        button:hover {
          opacity: 0.9;
        }
        /* Diferentes colores para cada botón */
        button:nth-child(1) {
          background: #4caf50;
          color: #fff;
        }
        button:nth-child(2) {
          background: #f44336;
          color: #fff;
        }
        button:nth-child(3) {
          background: #2196f3;
          color: #fff;
        }
        button:nth-child(4) {
          background: #ff9800;
          color: #fff;
        }
        button:nth-child(5) {
          background: #607d8b;
          color: #fff;
        }
        button:nth-child(6) {
          background: #9c27b0;
          color: #fff;
        }
      `}</style>
    </div>
  );
};

export default TestToast;
