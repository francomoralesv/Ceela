// RecintoCaractersComponentEdit.tsx
import React, { useState } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import HorizontalTabs from "@/components/common/HorizontalTabs";
import TabMuroCreate from "@/components/tab_recint_create_edit/TabMuroCreate"; 
import TabWindowCreate from "@/components/tab_recint_create_edit/TabWindowCreate"; 
import TabFloorCreate from "@/components/tab_recint_create_edit/TabFloorCreate";
import TabRoofCreate from "@/components/tab_recint_create_edit/TabRoofCreate";
import TabDoorCreate from "@/components/tab_recint_create_edit/TabDoorCreate";
import TabObstructionsCreate from "@/components/tab_recint_create_edit/TabObstructionsCreate"; // Se importa el nuevo componente

type TabStep = "muros" | "ventanas" | "puertas" | "techumbre" | "pisos" | "obstrucciones"; // Se añade "obstrucciones"

const RecintoCaractersComponentEdit: React.FC = () => {
  const [tabStep, setTabStep] = useState<TabStep>("muros");

  // Configuración de tabs para HorizontalTabs
  const tabs = [
    { key: "muros", label: "Muros" },
    { key: "ventanas", label: "Ventanas" },
    { key: "puertas", label: "Puertas" },
    { key: "techumbre", label: "Techumbre" },
    { key: "pisos", label: "Pisos" },
    { key: "obstrucciones", label: "Obstrucciones" }
  ];

  const renderTabContent = () => {
    switch (tabStep) {
      case "muros":
        return <TabMuroCreate />;
      case "ventanas":
        return <TabWindowCreate />;
      case "puertas":
        return <TabDoorCreate />;
      case "techumbre":
        return <TabRoofCreate />;
      case "pisos":
        return <TabFloorCreate />;
      case "obstrucciones":
        return <TabObstructionsCreate />; // Renderiza el componente de obstrucciones
      default:
        return null;
    }
  };



  return (
    <div className="container-fluid">
      <HorizontalTabs
        tabs={tabs}
        currentTab={tabStep}
        onTabChange={(tab) => setTabStep(tab as TabStep)}
        className="mb-3"
      />
      <div className="mt-3">{renderTabContent()}</div>
    </div>
  );
};

export default RecintoCaractersComponentEdit;
