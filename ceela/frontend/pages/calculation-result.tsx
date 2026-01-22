import Breadcrumb from "@/components/common/Breadcrumb";
import Card from "@/components/common/Card";
import CustomButton from "@/components/common/CustomButton";
import ProjectInfoHeader from "@/components/common/ProjectInfoHeader";

import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import Results from "../src/components/projects/Results";

const CalculationResultPage = () => {
  const [projectNameFromStorage, setProjectNameFromStorage] = useState("");
  const [regionFromStorage, setRegionFromStorage] = useState("");
  const [projectIdFromStorage, setProjectIdFromStorage] = useState("");

  const router = useRouter();
  const { id } = router.query;
  useEffect(() => {
    const storedProjectName = localStorage.getItem("project_name") || "";
    const storedRegion = localStorage.getItem("project_department") || "";
    const storedProjectId = id as string;
    setProjectNameFromStorage(storedProjectName);
    setRegionFromStorage(storedRegion);
    setProjectIdFromStorage(storedProjectId);
  }, []);

  const handleBack = () => {
    window.history.back();
  };

  return (
    <div className="py-4">
      <Card>
        <div>
          <div className="d-flex align-items-center" style={{ gap: "10px" }}>
            <ProjectInfoHeader
              projectName={projectNameFromStorage}
              region={regionFromStorage}
              project_id={projectIdFromStorage}
            />
            <Breadcrumb
              items={[
                {
                  title: "Editar",
                  href: "/",
                  active: true,
                },
              ]}
            />
          </div>
        </div>
      </Card>{" "}
      <Card>
        <Results />
        <div className="d-flex justify-content-between">
          <CustomButton variant="back" onClick={handleBack}>
            Regresar
          </CustomButton>
          {/*<CustomButton*/}
          {/*  onClick={() => console.log("guardar resultados")}*/}
          {/*  style={{*/}
          {/*    display: "inline-flex",*/}
          {/*    alignItems: "center",*/}
          {/*    justifyContent: "center",*/}
          {/*    transition: "all 0.2s ease-in-out",*/}
          {/*    backgroundColor: "var(--primary-color)",*/}
          {/*    border: "none",*/}
          {/*    fontSize: "14px",*/}
          {/*    borderRadius: "8px",*/}
          {/*    padding: "10px 16px",*/}
          {/*    cursor: "pointer",*/}
          {/*    boxShadow: "0 2px 4px rgba(0, 0, 0, 0.1)",*/}
          {/*    fontWeight: 500,*/}
          {/*    letterSpacing: "0.3px",*/}
          {/*    minWidth: "max-content",*/}
          {/*    whiteSpace: "normal",*/}
          {/*    lineHeight: 1.5,*/}
          {/*    height: "auto",*/}
          {/*    width: "100px",*/}
          {/*  }}*/}
          {/*  className="btn btn-sm mt-2 m-2 hover:opacity-80 transition-opacity duration-200"*/}
          {/*>*/}
          {/*  Guardar Cálculos*/}
          {/*</CustomButton>*/}
        </div>
      </Card>

    </div>
  );
};

export default CalculationResultPage;
