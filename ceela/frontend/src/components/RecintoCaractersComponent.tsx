// RecintoCaractersComponent.tsx
import React, { useState } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import HorizontalTabs from "@/components/common/HorizontalTabs";
import TabMuroCreate from "@/components/tab_recint_create/TabMuroCreate"; 
import TabWindowCreate from "@/components/tab_recint_create/TabWindowCreate"; 
import TabFloorCreate from "@/components/tab_recint_create/TabFloorCreate";
import TabRoofCreate from "@/components/tab_recint_create/TabRoofCreate";
import TabDoorCreate from "@/components/tab_recint_create/TabDoorCreate";
import TabObstructionsCreate from "@/components/tab_recint_create/TabObstructionsCreate";

type TabStep = "muros" | "techumbre" | "pisos" | "ventanas" | "puertas" | "obstrucciones";

const RecintoCaractersComponent: React.FC = () => {
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
        return <TabObstructionsCreate />;
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

export default RecintoCaractersComponent;
