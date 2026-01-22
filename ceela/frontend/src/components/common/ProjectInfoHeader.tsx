import CustomButton from "@/components/common/CustomButton";
import { constantUrlApiEndpoint } from "@/utils/constant-url-endpoint";
import Image from "next/image";
import { BarChart3 } from "lucide-react";
import { useRouter } from "next/router";
import React, { useEffect, useState } from "react";

interface Props {
  projectName: string;
  region: string;
  project_id?: string | number;
  disableclick?: boolean;
  projectStatus?: string;
}

const ProjectInfoHeader: React.FC<Props> = ({
  projectName,
  region,
  project_id,
  projectStatus: initialProjectStatus,
}) => {
  const router = useRouter();
  const [_currentRegion, setCurrentRegion] = useState(region);
  const [projectStatus, setProjectStatus] = useState(initialProjectStatus);

  const fetchProjectDetails = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!project_id) return;

      const response = await fetch(`${constantUrlApiEndpoint}/projects/${project_id}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'accept': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        if (data.divisions && data.divisions.region) {
          setCurrentRegion(data.divisions.region);
        }
        if (data.status) {
          setProjectStatus(data.status);
        }
      }
    } catch (error) {
      console.error('Error fetching project details:', error);
    }
  };

  useEffect(() => {
    fetchProjectDetails();
  }, [project_id]);

  useEffect(() => {
    const actualizarRegion = () => {
      const sel = localStorage.getItem("selected_region");
      if (sel) setCurrentRegion(sel);
    };

    window.addEventListener("storage", (e) => {
      if (e.key === "selected_region") actualizarRegion();
    });
    window.addEventListener("selectedRegionChanged", actualizarRegion);

    actualizarRegion();

    return () => {
      window.removeEventListener("storage", actualizarRegion);
      window.removeEventListener("selectedRegionChanged", actualizarRegion);
    };
  }, []);

  const handleProjectClick = () => {
    router.push(`/workflow-part1-edit?id=${project_id}&step=1`);
    localStorage.setItem("project_name_edit", projectName);
    localStorage.setItem("project_department_edit", region);
  };
  const handleRegionClick = () => {
    router.push(`/workflow-part1-edit?id=${project_id}&step=2`);
    localStorage.setItem("project_department_edit", region);
    localStorage.setItem("project_name_edit", projectName);
  };

  const handleIfcClick = () => {
    router.push(`/ifc?id=${project_id}`);
  };

  return (
    <div className="d-flex flex-column flex-md-row align-items-center gap-4">
      <span style={{ fontWeight: "normal", fontFamily: "var(--font-family-base)" }}>
        Proyecto:
      </span>
      <CustomButton
        variant="save"
        style={{ padding: "0.8rem 3rem", cursor: "pointer" }}
        onClick={handleProjectClick}
      >
        {`Nombre del proyecto: ${projectName}`}
      </CustomButton>
      <CustomButton
        variant="save"
        style={{ padding: "0.8rem 3rem", cursor: "pointer" }}
        onClick={handleRegionClick}
      >
        {`Región: ${region}`}
      </CustomButton>
      {projectStatus === "registrado" && (
        <CustomButton
          color="orange"
          style={{ padding: "0.8rem 3rem", cursor: "pointer", display: "flex", alignItems: "center", gap: "0.5rem" }}
          onClick={handleIfcClick}
        >
          <BarChart3 size={20} />
          Adjuntar IFC
        </CustomButton>
      )}
    </div>
  );
};

export default ProjectInfoHeader;
