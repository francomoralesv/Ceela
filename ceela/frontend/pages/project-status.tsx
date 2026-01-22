import axios from "axios";
import "bootstrap/dist/css/bootstrap.min.css";
import { useRouter } from "next/router";
import React, { useEffect, useState } from "react";
import Breadcrumb from "../src/components/common/Breadcrumb";
import Card from "../src/components/common/Card";
import CustomButton from "../src/components/common/CustomButton";
import DataTable from "../src/components/DataTable"; //
import Title from "../src/components/Title";
import useAuth from "../src/hooks/useAuth";

interface Divisions {
  department?: string;
  province?: string;
  district?: string;
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
  residential_type?: string;
  number_levels?: number;
  number_homes_per_level?: number;
  built_surface?: number;
  latitude?: number;
  longitude?: number;
  [key: string]: unknown;
}

// Función para obtener el estilo según el estado, usando los colores indicados
const getStatusStyle = (status: string | undefined) => {
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

// Función auxiliar para renderizar el tag de estado con los estilos definidos
const getStatusTag = (status?: string): React.ReactElement => {
  const style = getStatusStyle(status);
  return (
    <span
      style={{
        ...style,
        padding: "2px 8px",
        borderRadius: "4px",
        fontWeight: "bold",
      }}
    >
      {status?.toUpperCase()}
    </span>
  );
};

const toUpperCase = (value?: string): string => (value ? value.toUpperCase() : "");

const formatValue = (value: unknown): string => {
  if (value === 0 || value === undefined || value === null || value === '') {
    return '-';
  }
  return String(value);
};

const ProjectListStatusEditPage = () => {
  useAuth();
  const router = useRouter();
  console.log("[ProjectListStatusEditPage] Página cargada y sesión validada.");

  const [projects, setProjects] = useState<Project[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async (): Promise<void> => {
    setLoading(true);
    const token = localStorage.getItem("token");
    if (!token) {
      console.error("[fetchProjects] No estás autenticado. Inicia sesión nuevamente.");
      setError("No estás autenticado. Inicia sesión nuevamente.");
      setLoading(false);
      return;
    }
    try {
      console.log("[fetchProjects] Obteniendo proyectos...");
      const response = await axios.get(`/api/projects`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setProjects(response.data.projects);
    } catch (err: unknown) {
      console.error("[fetchProjects] Error al obtener los proyectos:", err);
      if (axios.isAxiosError(err) && err.response) {
        setError((err.response.data as { detail?: string }).detail || "Error al obtener los proyectos.");
      } else {
        setError("Error de conexión con el servidor.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleViewProject = (project_view: Project) => {
    localStorage.setItem("project_id", project_view.id.toString());
    localStorage.setItem("project_name_view", toUpperCase(project_view.name_project) || "N/A");
    localStorage.setItem(
      "project_department_view",
      toUpperCase(project_view.divisions?.department) || "N/A"
    );
    router.push(`/workflow-part1-view?id=${project_view.id}`);
  };

  // Definición de columnas para el DataTable, con la columna "Estado" en segunda posición
  const columns = [
    { 
      id: "id", 
      label: "ID", 
      minWidth: 50,
      headerStyle: { whiteSpace: 'nowrap', display: 'flex', alignItems: 'center' }
    },
    {
      id: "status",
      label: "Estado",
      minWidth: 100,
      headerStyle: { whiteSpace: 'nowrap', display: 'flex', alignItems: 'center' },
      cell: ({ row }: { row: Project }) => (
        <div className="text-center">{getStatusTag(row.status)}</div>
      )
    },
    {
      id: "name_project",
      label: "Nombre del proyecto",
      minWidth: 150,
      headerStyle: { whiteSpace: 'nowrap', display: 'flex', alignItems: 'center' },
      cell: ({ row }: { row: Project }) => <span>{toUpperCase(row.name_project)}</span>
    },
    {
      id: "owner_name",
      label: "Propietario",
      minWidth: 100,
      headerStyle: { whiteSpace: 'nowrap', display: 'flex', alignItems: 'center' },
      cell: ({ row }: { row: Project }) => <span>{toUpperCase(row.owner_name) || '-'}</span>
    },
    {
      id: "building_type",
      label: "Tipo de edificación",
      minWidth: 100,
      headerStyle: { whiteSpace: 'nowrap', display: 'flex', alignItems: 'center' },
      cell: ({ row }: { row: Project }) => <span>{toUpperCase(row.building_type) || '-'}</span>
    },
    {
      id: "residential_type",
      label: "Tipo de residencial",
      minWidth: 100,
      headerStyle: { whiteSpace: 'nowrap', display: 'flex', alignItems: 'center' },
      cell: ({ row }: { row: Project }) => <span>{toUpperCase(row.residential_type) || '-'}</span>
    },
    { 
      id: "number_levels", 
      label: "Número de niveles", 
      minWidth: 100,
      headerStyle: { whiteSpace: 'nowrap', display: 'flex', alignItems: 'center' },
      cell: ({ row }: { row: Project }) => <span>{formatValue(row.number_levels)}</span>
    },
    { 
      id: "number_homes_per_level", 
      label: "Número de viviendas", 
      minWidth: 100,
      headerStyle: { whiteSpace: 'nowrap', display: 'flex', alignItems: 'center' },
      cell: ({ row }: { row: Project }) => <span>{formatValue(row.number_homes_per_level)}</span>
    },
    { 
      id: "built_surface", 
      label: "Superficie construida (M²)", 
      minWidth: 100,
      headerStyle: { whiteSpace: 'nowrap', display: 'flex', alignItems: 'center' },
      cell: ({ row }: { row: Project }) => <span>{formatValue(row.built_surface)}</span>
    },
    {
      id: "actions",
      label: "Acciones",
      minWidth: 100,
      sortable: false,
      headerStyle: { whiteSpace: 'nowrap', display: 'flex', alignItems: 'center' },
      cell: ({ row }: { row: Project }) => (
        <div className="text-center">
          <CustomButton
            variant="viewIcon"
            onClick={() => handleViewProject(row)}
            style={{
              backgroundColor: "var(--primary-color)",
              padding: "0.5rem",
              width: "40px",
              height: "40px",
              borderRadius: "4px"
            }}
          />
        </div>
      )
    }
  ];

  return (
    <div>
      <Card>
        <div className="d-flex align-items-center w-100">
          <Title text="Administrar proyectos" />
          <Breadcrumb
            items={[
              { title: "Administrar proyectos", href: "/project-status", active: true }
            ]}
          />
        </div>
      </Card>
      {/* El DataTable se encarga de mostrar la búsqueda, paginación y tabla */}
      <DataTable
        data={projects}
        columns={columns}
        loading={loading}
        pageSize={10}
      />
      {error && (
        <Card>
          <p className="text-danger px-4 pt-4" style={{ fontWeight: "normal" }}>
            {error}
          </p>
        </Card>
      )}
    </div>
  );
};

export default ProjectListStatusEditPage;
