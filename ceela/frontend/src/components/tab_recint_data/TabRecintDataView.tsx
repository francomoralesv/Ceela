// TabRecintDataView.tsx
import CustomButton from "@/components/common/CustomButton";
import TablesParameters from "@/components/tables/TablesParameters";
import { constantUrlApiEndpoint } from "@/utils/constant-url-endpoint";
import { useRouter } from "next/router";
import React, { useEffect, useState } from "react";

interface EnclosureGeneralData {
  id: number;
  occupation_profile_id: number;
  height: number;
  co2_sensor: string;
  project_id: number;
  region_id: number;
  zona_termica: string;
  name_enclosure: string;
  comuna_id: number;
  nombre_comuna: string;
  nombre_region: string;
  district: string; // Add this field
  perfil_uso: string;
  level_id: number;
  usage_profile_name:string;
}

const TabRecintDataView: React.FC = () => {
  const router = useRouter();
  const token = typeof window !== "undefined" ? localStorage.getItem("token") ?? null : null;
  const [projectId, setProjectId] = useState<string | null>(
    typeof window !== "undefined" ? localStorage.getItem("project_id") : null
  );
  const [data, setData] = useState<EnclosureGeneralData[]>([]);

  useEffect(() => {
    if (!token || !projectId) return;
    const fetchAllData = async () => {
      try {
        const headers = {
          accept: "application/json",
          Authorization: `Bearer ${token}`,
        };

        const enclosureRes = await fetch(
          `${constantUrlApiEndpoint}/enclosure-generals/${projectId}`,
          { headers }
        );

        if (enclosureRes.ok) {
          const enclosureData: EnclosureGeneralData[] = await enclosureRes.json();
          setData(enclosureData);
        }
      } catch (error) {
        console.error("Error al cargar los datos:", error);
      }
    };

    fetchAllData();
  }, [projectId, token]);

  // Al hacer clic, redirige a la página "recinto-view" pasando el id del recinto 
  // y guardando el enclosure_id en el LocalStorage (asegúrate de tener ese valor disponible)
  const handleViewProject = (row: EnclosureGeneralData) => {
    // Guarda el enclosure_id en el localStorage. Por ejemplo, si row.id es el enclosure_id:
    localStorage.setItem("enclosure_id", row.id.toString());
    router.push({
      pathname: "/recinto-view",
      query: { id: row.id }
    });
  };

  const columns = [
    {
      headerName: "Cod",
      field: "id",
      renderCell: (row: EnclosureGeneralData) => ("REC-" + row.id),
    },
    {
      headerName: "Nombre Recinto",
      field: "name_enclosure",
      renderCell: (row: EnclosureGeneralData) => row.name_enclosure,
    },
    {
      headerName: "Perfil Ocupación",
      field: "usage_profile_name",
      renderCell: (row: EnclosureGeneralData) => row.usage_profile_name,
    },
    {
      headerName: "Altura (m)",
      field: "height",
      renderCell: (row: EnclosureGeneralData) => row.height?.toFixed(2),
    },
    {
      headerName: "Sensor CO2",
      field: "co2_sensor",
      renderCell: (row: EnclosureGeneralData) => row.co2_sensor,
    },
    {
      headerName: "Nivel de Recinto",
      field: "level_id",
      renderCell: (row: EnclosureGeneralData) => row.level_id,
    },
    {
      headerName: "Región",
      field: "nombre_region",
      renderCell: (row: EnclosureGeneralData) => row.nombre_region,
    },
    {
      headerName: "Distrito/Municipio",
      field: "district",
      renderCell: (row: EnclosureGeneralData) => row.district,
    },
    {
      headerName: "Acciones",
      field: "acciones",
      renderCell: (row: EnclosureGeneralData) => (
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
      <TablesParameters columns={columns} data={data} />
      {data.length === 0 && (
        <div style={{ textAlign: "center", padding: "1rem" }}>
          No hay datos para mostrar
        </div>
      )}
    </div>
  );
};

export default TabRecintDataView;
