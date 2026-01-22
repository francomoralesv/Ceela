import ActionButtons from "@/components/common/ActionButtons";
import ModalCreate from "@/components/common/ModalCreate";
import SearchFilter from "@/components/inputs/SearchFilter";
import TablesParameters from "@/components/tables/TablesParameters";
import { constantUrlApiEndpoint } from "@/utils/constant-url-endpoint";
import { notify } from "@/utils/notify";
import { useRouter } from "next/router";
import React, { useEffect, useState } from "react";

// ===========================================================
// Interfaces
// ===========================================================
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
  district: string; // Add this field
  nombre_region: string;
  perfil_uso: string;
  level_id: string;
  usage_profile_name?: string; 
}

interface OccupationProfile {
  id: number;
  code?: string;
  name: string;
}

interface IFormData {
  nombreRecinto: string;
  perfilOcupacion: number;
  alturaPromedio: string;
  sensorCo2: boolean;
  levelId: string;
}
const searchKeys = [
  "name_enclosure",   // nombre
  "id",               // código REC-##
  "nombre_comuna",
  "nombre_region",
  "occupation_profile_id",
  "co2_sensor",
  "height",
  "zona_termica",
] as const;
const LOCAL_STORAGE_KEY = "recintoFormData";

// ===========================================================
// Hook para obtener el token
// ===========================================================
const useAuthToken = () => {
  const [token, setToken] = useState("");
  useEffect(() => {
    if (typeof window !== "undefined") {
      const storedToken = localStorage.getItem("token");
      if (storedToken) setToken(storedToken);
    }
  }, []);
  return token;
};

// ===========================================================
// Componente principal
// ===========================================================
const TabRecintDataCreate: React.FC = () => {
  const router = useRouter();
  const token = useAuthToken();

  const [projectId, setProjectId] = useState("44");

  useEffect(() => {
    if (typeof window !== "undefined") {
      const storedProjectId = localStorage.getItem("last_created_project") || "44";
      setProjectId(storedProjectId);
    }
  }, []);

  const [data, setData] = useState<EnclosureGeneralData[]>([]);
  const [occupationProfiles, setOccupationProfiles] = useState<OccupationProfile[]>([]);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [itemToDelete, setItemToDelete] = useState<EnclosureGeneralData | null>(null);

  // ===========================================================
  // 1. Fetch de datos
  // ===========================================================
  const fetchEnclosureGenerals = async () => {
    if (!token || !projectId) return;
    try {
      const url = `${constantUrlApiEndpoint}/enclosure-generals/${projectId}`;
      const response = await fetch(url, {
        method: "GET",
        headers: {
          accept: "application/json",
          Authorization: `Bearer ${token}`,
        },
      });
      if (!response.ok) return;
      const responseData: EnclosureGeneralData[] = await response.json();
      setData(responseData);
    } catch (error) {
      console.error(error);
    }
  };

  const fetchOccupationProfiles = async () => {
    try {
      const url = `${constantUrlApiEndpoint}/user/enclosures-typing/`;
      const response = await fetch(url, {
        method: "GET",
        headers: {
          accept: "application/json",
          Authorization: `Bearer ${token}`,
        },
      });
      if (!response.ok) throw new Error();
      const result: OccupationProfile[] = await response.json();
      setOccupationProfiles(result);
    } catch (error) {
      notify("Error al cargar perfiles de ocupación");
    }
  };

  // ===========================================================
  // 2. useEffect inicial
  // ===========================================================
  useEffect(() => {
    if (token && projectId) {
      fetchEnclosureGenerals();
      fetchOccupationProfiles();
    }
  }, [token, projectId]);

  // ===========================================================
  // 3. Funciones
  // ===========================================================
  const handleCreate = () => {
    // Validar que no haya más de 3 recintos
    if (data.length >= 3) {
      notify("No se puede crear más de 3 recintos por proyecto", "error");
      return;
    }
    localStorage.removeItem(LOCAL_STORAGE_KEY);
    localStorage.removeItem("recinto_id");
    router.push("/recinto-create");
  };

  const handleEditWithRedirect = (row: EnclosureGeneralData) => {
    const formData: IFormData = {
      nombreRecinto: row.name_enclosure,
      perfilOcupacion: row.occupation_profile_id,
      alturaPromedio: row.height.toString(),
      sensorCo2: row.co2_sensor === "Si",
      levelId: row.level_id,
    };
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(formData));
    localStorage.setItem("recinto_id", row.id.toString());
    notify("Datos del recinto cargados para edición");
    router.push("/recinto-edit-mode-create");
  };

  const handleDelete = (row: EnclosureGeneralData) => {
    setItemToDelete(row);
    setShowDeleteModal(true);
  };

  const confirmDelete = async () => {
    if (!itemToDelete) return;
    const url = `${constantUrlApiEndpoint}/enclosure-generals-delete/${projectId}/${itemToDelete.id}`;
    try {
      const response = await fetch(url, {
        method: "DELETE",
        headers: {
          accept: "application/json",
          Authorization: `Bearer ${token}`,
        },
      });
      if (!response.ok) throw new Error();
      notify("Recinto eliminado exitosamente");
      setData((prevData) => prevData.filter((item) => item.id !== itemToDelete.id));
      setShowDeleteModal(false);
      setItemToDelete(null);
      await fetchEnclosureGenerals();
    } catch (error) {
      console.error(error);
      notify("Error al eliminar");
    }
  };

  const cancelDelete = () => {
    setShowDeleteModal(false);
    setItemToDelete(null);
  };

  // ===========================================================
  // 4. Columnas tabla
  // ===========================================================
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
      renderCell: (row: EnclosureGeneralData) =>
        row.usage_profile_name,
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
      field: "region_id",
      renderCell: (row: EnclosureGeneralData) =>
        row.nombre_region || row.region_id,
    },
    {
      headerName: "Distrito/Municipio",
      field: "comuna_id",
      renderCell: (row: EnclosureGeneralData) =>
        row.district || row.nombre_comuna || row.comuna_id,
    },
    {
      headerName: "Acciones",
      field: "acciones",
      sortable: false,
      renderCell: (row: EnclosureGeneralData) => (
        <ActionButtons
          onEdit={() => handleEditWithRedirect(row)}
          onDelete={() => handleDelete(row)}
        />
      ),
    },
  ];
  const renderTable = (rows: EnclosureGeneralData[]) => (
    <>
      <div style={{
        width: '100%',
        overflowX: 'auto',
        position: 'relative',
        WebkitOverflowScrolling: 'touch',
        minHeight: '200px'
      }}>
        <TablesParameters columns={columns} data={rows} />
      </div>
      {rows.length === 0 && (
        <div style={{ textAlign: "center", padding: "1rem" }}>
          No hay datos para mostrar
        </div>
      )}
    </>
  );
  return (
    <div>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "1rem",
          gap: "1rem",
        }}
      >
        {/* 🔍  NUEVO: filtro */}
        <div style={{ flex: 1 /* que crezca */ }}>
          <SearchFilter
            data={data as unknown as Record<string, unknown>[]}
            searchKeys={[...searchKeys]}
            placeholder="Buscar recinto…"
            showNewButton          // ← activa el botón
            onNew={handleCreate}
          >
            {(
              filteredRows,             // array filtrado
              /* query, setQuery */     // (los recibes por si los necesitas)
            ) => renderTable(filteredRows as unknown as EnclosureGeneralData[])}
          </SearchFilter>
        </div>

        {/* ➕  botón “Nuevo” */}

      </div>


      <ModalCreate
        isOpen={showDeleteModal}
        onClose={cancelDelete}
        onSave={confirmDelete}
        saveLabel="Eliminar"
        title="Confirmar Eliminación"
      >
        <div className="container">
          <div className="row mb-3">
            <div className="col-12 text-center">
              <p>¿Está seguro que desea eliminar el siguiente recinto?</p>
              <h5 className="mt-3 mb-3">
                {itemToDelete?.name_enclosure || "Sin nombre"}
              </h5>
            </div>
          </div>
        </div>
      </ModalCreate>
    </div>
  );
};

export default TabRecintDataCreate;
