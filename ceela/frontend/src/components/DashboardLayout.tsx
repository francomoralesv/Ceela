"use client";
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap-icons/font/bootstrap-icons.css";
import { useState } from "react";
import Navbar from "./layout/Navbar";
import TopBar from "./layout/TopBar";

const Dashboard = () => {
  const [activeView, setActiveView] = useState("projects"); // manejar las vistas
  const [sidebarWidth, ] = useState("300px");

  // Renderiza la vista activa
  const renderContent = () => {
    return (
      <div className="text-center mt-5">
        {/* Uso sin sentido de activeView para eliminar el error */}
        <h1 className="fw-bold text-primary">¡Bienvenido a {activeView}!</h1>
        <p>Gestiona tus proyectos de manera eficiente.</p>
        <i
          className="bi bi-bar-chart-fill text-primary"
          style={{ fontSize: "50px" }}
        ></i>
      </div>
    );
  };

  return (
    <div className="d-flex">
      {/* Barra lateral: Se envían ambas props obligatorias */}
      <Navbar setActiveView={setActiveView}  />

      {/* Contenedor principal: Se pasa la propiedad "sidebarWidth" a TopBar */}
      <div className="d-flex flex-column flex-grow-1">
        <TopBar sidebarWidth={sidebarWidth} />
        <div className="content p-4" style={{ marginTop: "60px" }}>
          {renderContent()}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
