import WelcomeCard from "@/components/CardWelcome";
import ChartProjectCreated from "@/components/ChartProjectCreated";
import Breadcrumb from "@/components/common/Breadcrumb";
import ModalCreate from "@/components/common/ModalCreate";
import { useApiNext } from "@/hooks/useApiNext";
import { validateProject } from "@/service/validate-project";
import { notify } from "@/utils/notify";
import axios from "axios";
import { useRouter } from "next/router";
import React, { useEffect, useState } from "react";
import Card from "../src/components/common/Card";
import CustomButton from "../src/components/common/CustomButton";
import DataTable from "../src/components/DataTable";
import Title from "../src/components/Title";
import useAuth from "../src/hooks/useAuth";
import { constantUrlApiEndpoint } from "../src/utils/constant-url-endpoint";

interface Divisions {
  department?: string;
  province?: string;
  district?: string;
  region?: string; // Add region to divisions
}

export interface Project {
  id: number;
  status?: string;
  name_project?: string;
  owner_name?: string;
  designer_name?: string;
  director_name?: string;
  address?: string;
  country?: string;
  divisions?: Divisions;
  owner_lastname?: string;
  building_type?: string;
  main_use_type?: string;
  number_levels?: number;
  number_homes_per_level?: number;
  built_surface?: number;
  latitude?: number;
  longitude?: number;
}



const ProjectListPage = () => {
  useAuth();
  console.log("[ProjectListPage] Página cargada y sesión validada.");

  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
  const [, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Estados para controlar el modal de eliminación
  const [showDeleteModal, setShowDeleteModal] = useState<boolean>(false);
  const [projectToDelete, setProjectToDelete] = useState<{
    id: number;
    name: string;
  } | null>(null);

  const { get } = useApiNext();
  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async (): Promise<void> => {
    setLoading(true);
    try {
      const response = await get("api/projects_user");
      // Aplanamos divisions.region en una propiedad region
      const projectsConRegion = response.projects.map((p: Project) => ({
        ...p,
        region: p.divisions?.region || "No disponible",
      }));
      setProjects(projectsConRegion);
    } catch (err) {
      console.error("Error al cargar proyectos:", err);
      setError("Error al cargar los proyectos. Por favor, inténtelo de nuevo.");
    } finally {
      setLoading(false);
    }
  };


  const handleGoToWorkflow = (project_edit: Project): void => {
    console.log(
      "[handleGoToWorkflow] Navegando al workflow para el proyecto:",
      project_edit.id
    );
    localStorage.setItem("project_id", String(project_edit.id));
    localStorage.setItem(
      "project_department_edit",
      project_edit.divisions?.department || ""
    );
    localStorage.setItem("project_name_edit", project_edit.name_project || "");
    router.push(`/workflow-part1-edit?id=${project_edit.id}`);
  };
  const handleCalculateResults = async (project: Project): Promise<void> => {
    const projectId = project.id;
    try {
      const validationResult = await validateProject(projectId.toString(), true);

      if (validationResult?.valid) {
        router.push(`/calculation-result2?id=${projectId}`);
      } else {
        console.log("Project validation failed:", validationResult);
        let errorMessage = "El proyecto no cumple con todos los requisitos necesarios para el cálculo:";
        
        if (validationResult?.additional_validations?.climate_file?.valid === false) {
          const climateError = validationResult.additional_validations.climate_file.info?.error || "El archivo climático no es válido o falta.";
          errorMessage += `\n- ${climateError}`;
        }

        if (validationResult?.failed_enclosures && validationResult.failed_enclosures.length > 0) {
          errorMessage += "\n\n- Hay recintos sin los elementos constructivos requeridos.";
        }

        notify(errorMessage, "error");
      }
    } catch (error) {
      console.error("Error validating project:", error);
      notify("Error al validar el proyecto. Inténtelo nuevamente.", "error");
    }
  };

  // Función para abrir el modal de confirmación
  const handleDelete = (projectId: number, projectName: string): void => {
    setProjectToDelete({ id: projectId, name: projectName });
    setShowDeleteModal(true);
  };

  // Función que se ejecuta al confirmar la eliminación en el modal
  const confirmDelete = async (): Promise<void> => {
    if (!projectToDelete) return;

    const token: string | null = localStorage.getItem("token");
    if (!token) {
      setError("No estás autenticado. Inicia sesión nuevamente.");
      setShowDeleteModal(false);
      return;
    }
    try {
      const url = `${constantUrlApiEndpoint}/project/${projectToDelete.id}/delete`;
      await axios.delete<void>(url, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });
      notify("¡Proyecto eliminado exitosamente!");
      fetchProjects();
    } catch (err: unknown) {
      console.error("[confirmDelete] Error al eliminar proyecto:", err);
      setError("No se pudo eliminar el proyecto.");
      notify("No se pudo eliminar el proyecto.");
    } finally {
      setShowDeleteModal(false);
      setProjectToDelete(null);
    }
  };

  const getStatusStyle = (status: string | undefined): React.CSSProperties => {
    const s = status?.toLowerCase();
    if (s === "finalizado") {
      return { backgroundColor: "#ffe8e8", color: "#e45f5f" };
    }
    if (s === "registrado") {
      return { backgroundColor: "#e8ffed", color: "#a9dfb4" };
    }
    if (s === "en proceso") {
      return { backgroundColor: "#fff9e8", color: "#edc68c" };
    }
    return {};
  };

  // Definición de columnas para el DataTable
  const tableColumns = [
    { id: "id", label: "ID", minWidth: 50 },
    {
      id: "status",
      label: "Estado",
      minWidth: 100,
      cell: ({ row }: { row: Project }) => (
        <span
          className="badge status-badge"
          style={{
            ...getStatusStyle(row.status),
            display: "inline-block",
            fontSize: "0.8rem",
            fontWeight: "normal",
            padding: "8px 16px",
            borderRadius: "0.5rem",
          }}
        >
          {row.status ? row.status.toUpperCase() : "NO DISPONIBLE"}
        </span>
      ),
    },
    {
      id: "name_project",
      label: "Nombre proyecto",
      minWidth: 150,
    },
    {
      id: "owner_name",
      label: "Propietario",
      minWidth: 100,
    },
    {
      id: "building_type",
      label: "Tipo de edificación",
      minWidth: 100,
    },
    {
      id: "region",
      label: "Región",
      minWidth: 100,
      cell: ({ row }: { row: Project }) =>
        row.divisions?.region || "No disponible", // Change department to region
    },
    {
      id: "actions",
      label: "Acciones",
      minWidth: 100,
      sortable: false,
      cell: ({ row }: { row: Project }) => (
        <div>
          {/* Botón de IFC */}
          {row.status === "registrado" && (
            <CustomButton
              className="btn-table-list"
              onClick={() => router.push("/ifc?id=" + row.id)}
              title="Adjuntar archivo .ifc"
            >
              <span className="material-icons" style={{ fontSize: "24px" }}>
                apartment
              </span>
            </CustomButton>
          )}

          {/* Botón Calcular Resultados */}
          {row.status?.toLowerCase() === 'en proceso' && (
            <CustomButton
              className="btn-table-list"
              color="orange"
              onClick={() => handleCalculateResults(row)}
              title="Realizar el calculo de resultados"
            >
              <span className="material-icons">calculate</span>
            </CustomButton>
          )}

          {/* Botón de Editar */}
          <CustomButton
            variant="editIcon"
            className="btn-table-list"
            onClick={() => handleGoToWorkflow(row)}
            title="Editar en Workflow"
          />

          {/* Botón de Eliminar */}
          <CustomButton
            variant="deleteIcon"
            className="btn-table-list"
            onClick={() => handleDelete(row.id, row.name_project || "N/D")}
          />
        </div>
      ),
    },
  ];

  return (
    <>
      <div>
        <Card>
          <div className="d-flex align-items-center w-100">
            <Title text="Listado de Proyectos" />
            <Breadcrumb
              items={[
                { title: "Proyectos", href: "/project-list", active: true },
              ]}
            />
          </div>
        </Card>

        <DataTable
          data={projects}
          columns={tableColumns}
          loading={loading}
          createText="Nuevo Proyecto"
          createUrl="/workflow-part1-create"
          pageSize={10}
          showButton={true}
        />

        {/* Se movieron los charts debajo de la tabla */}
        <div className="row mt-4 mb-4">
          <div className="col-md-6">
            <WelcomeCard />
          </div>
          <div className="col-md-6">
            <ChartProjectCreated />
          </div>
        </div>
      </div>

      {showDeleteModal && projectToDelete && (
        <ModalCreate
          isOpen={showDeleteModal}
          onClose={() => {
            setShowDeleteModal(false);
            setProjectToDelete(null);
          }}
          onSave={confirmDelete}
          title="Confirmar eliminación"
          saveLabel="Eliminar"
        >
          <p>
            ¿Estás seguro de eliminar el proyecto{" "}
            <strong>{projectToDelete.name}</strong> (ID: {projectToDelete.id})?{" "}
            <br />
            Esta acción no se puede deshacer.
          </p>
        </ModalCreate>
      )}

      <style jsx>{`
        .status-badge {
          font-family: var(--font-family-base);
        }
        .row.mt-4.mb-4 {
          max-height: calc(100vh - 200px);
          overflow-y: auto;
        }
      `}</style>
    </>
  );
};

export default ProjectListPage;
