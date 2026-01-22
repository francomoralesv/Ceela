import ActionButtons from "@/components/common/ActionButtons";
import ActionButtonsConfirm from "@/components/common/ActionButtonsConfirm";
import TablesParameters from "@/components/tables/TablesParameters";
import { constantUrlApiEndpoint } from "@/utils/constant-url-endpoint";
import { notify } from "@/utils/notify";
import "bootstrap/dist/css/bootstrap.min.css";
import React, { ChangeEvent, useEffect, useState } from "react";
import CustomButton from "../common/CustomButton";
import ModalCreate from "../common/ModalCreate";
//ThermicBridgesModal
import ThermalBridgesWallModal from "@/components/modals/ThermalBridgesWallModal";
import useFetchAngleOptions from "@/hooks/useFetchAngleOptions";
import { Plus } from "lucide-react";
import GoogleIcons from "public/GoogleIcons";
import { preventDash } from "@/lib/utils";

// Interfaz para muros
interface Wall {
  id?: number;
  wall_id: number;
  name: string;
  characteristics: string;
  angulo_azimut: string;
  area: number;
  orientation?: string;
  u?: number;
}

// Interfaz para puentes térmicos, se agregó wall_id para relacionar con el muro
interface ThermalBridge {
  id: number;
  wall_id: number; // Identifica el muro asociado
  po1_length: number;
  po1_id_element: number;
  po1_element_name?: string;
  po2_length: number;
  po2_id_element: number;
  po2_element_name?: string;
  po3_length: number;
  po3_id_element: number;
  po3_element_name?: string;
  po4_length: number;
  po4_e_aislacion: number;
  po4_id_element: number;
  po4_element_name?: string;
}

// Interfaz para las opciones de desplegable (usada tanto para muros como para elementos de puente térmico)
interface WallDetail {
  type: string;
  id: number;
  info: any;
  value_u: number;
  created_status: string;
  name_detail: string;
  project_id: number;
}

// Definición de la data fusionada (muro + puente) con propiedad bridgeId para el id del puente térmico
interface MergedWall extends Omit<Wall, "wall_id">, Partial<ThermalBridge> {
  wall_id: number;
  bridgeId?: number | null;
}

const TabMuroCreate: React.FC = () => {
  // Función helper para formatear valores
  const formatValue = (value: any, fixed?: number): string => {
    if (value === 0 || value === "0" || value === "N/A") {
      return "-";
    }
    if (typeof value === "number" && fixed !== undefined) {
      return value.toFixed(fixed);
    }
    return value;
  };

  // Estados de modales (solo para muros)
  const [isWallModalOpen, setIsWallModalOpen] = useState<boolean>(false);
  // Modal de confirmación para eliminación de muro
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState<boolean>(false);

  //ThermalBridgesModal OPEN
  const [showModalThermicBridges, setShowModalThermicBridges] =
    useState<boolean>(false);
  //ThermalBridgesModal FIN

  const [wallToDelete, setWallToDelete] = useState<Wall | null>(null);

  // Estados de datos: muros, puentes y data fusionada
  const [murosData, setMurosData] = useState<Wall[]>([]);
  const [puentesData, setPuentesData] = useState<ThermalBridge[]>([]);
  const [mergedData, setMergedData] = useState<MergedWall[]>([]);

  // Estados para edición de muros
  const [editingWallId, setEditingWallId] = useState<number | null>(null);
  const [editingWallData, setEditingWallData] = useState<Wall | null>(null);

  // Estados para edición de puentes térmicos (dentro de la misma tabla)
  const [editingBridgeId, setEditingBridgeId] = useState<number | null>(null);
  const [editingBridgeData, setEditingBridgeData] =
    useState<ThermalBridge | null>(null);

  // Otras opciones y datos del formulario
  const [angleOptions, setAngleOptions] = useFetchAngleOptions();
  const [wallOptions, setWallOptions] = useState<WallDetail[]>([]);
  const [detailOptions, setDetailOptions] = useState<WallDetail[]>([]);
  const [projectId, setProjectId] = useState<string | null>(null);

  // Formularios para nuevo muro
  const [newWall, setNewWall] = useState<Wall>({
    wall_id: 0,
    name: "",
    characteristics: "",
    angulo_azimut: "",
    area: 0,
  });

  // Obtener el project_id desde localStorage
  useEffect(() => {
    const storedProjectId = localStorage.getItem("project_id");
    if (storedProjectId) {
      setProjectId(storedProjectId);
    }
  }, []);

  // Activar project id y cargar datos
  useEffect(() => {
    if (projectId) {
      fetchData();
    }
  }, [projectId]);

  // Función para obtener token y enclosure_id desde localStorage
  const getAuthData = () => {
    const token = localStorage.getItem("token");
    const enclosure_id = localStorage.getItem("recinto_id");
    if (!token) {
      notify("Error: No se encontró el token en el localStorage.");
      return null;
    }
    if (!enclosure_id) {
      return null;
    }
    return { token, enclosure_id };
  };

  // Obtener opciones de muros para el desplegable
  useEffect(() => {
    const fetchWallOptions = async () => {
      if (!projectId) return;
      try {
        const authData = getAuthData();
        const headers: HeadersInit = { "Content-Type": "application/json" };
        if (authData) headers.Authorization = `Bearer ${authData.token}`;
        const response = await fetch(
          `${constantUrlApiEndpoint}/project/${projectId}/details/Muro`,
          { headers }
        );
        if (!response.ok) throw new Error("Error al obtener detalles de muros");
        const walls: WallDetail[] = await response.json();
        setWallOptions(walls);
      } catch (error) {
        console.error(error);
      }
    };
    fetchWallOptions();
  }, [projectId]);

  // Obtener todas las opciones de detalles para los elementos del puente térmico
  useEffect(() => {
    const fetchDetailOptions = async () => {
      if (!projectId) return;
      try {
        const authData = getAuthData();
        const headers: HeadersInit = { "Content-Type": "application/json" };
        if (authData) headers.Authorization = `Bearer ${authData.token}`;
        const response = await fetch(
          `${constantUrlApiEndpoint}/project/${projectId}/details`,
          { headers }
        );
        if (!response.ok) throw new Error("Error al obtener detalles");
        const details: WallDetail[] = await response.json();
        setDetailOptions(details);
      } catch (error) {
        console.error(error);
      }
    };
    fetchDetailOptions();
  }, [projectId]);


  // Función para obtener datos de la API (muros y puentes térmicos)
  const fetchData = async () => {
    const authData = getAuthData();
    if (!authData) return;
    const { token, enclosure_id } = authData;
    try {
      // Muros
      const responseMuros = await fetch(
        `${constantUrlApiEndpoint}/wall-enclosures/${enclosure_id}`,
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        }
      );
      if (!responseMuros.ok) throw new Error("Error al obtener muros");
      const muros = await responseMuros.json();
      setMurosData(muros);

      // Puentes térmicos
      const responsePuentes = await fetch(
        `${constantUrlApiEndpoint}/thermal-bridge/${enclosure_id}`,
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        }
      );
      if (!responsePuentes.ok)
        throw new Error("Error al obtener puentes térmicos");
      const puentes = await responsePuentes.json();
      setPuentesData(puentes);

      // Fusionar datos manteniendo el orden original de muros
      const merged = muros
        .map((muro: Wall) => {
          const puente = puentes.find(
            (p: ThermalBridge) => p.wall_id === muro.id
          );
          return {
            ...muro,
            ...puente,
            id: muro.id,
            bridgeId: puente ? puente.id : null,
          };
        })
        .sort((a: MergedWall, b: MergedWall) => (a.id && b.id ? a.id - b.id : 0)); // Mantener orden por ID

      setMergedData(merged);
    } catch (error) {
      notify("Error al cargar los datos");
      console.error(error);
    }
  };

  // Funciones para edición de muros
  const handleEditWall = (id: number) => {
    const wallToEdit = murosData.find((w) => w.id === id);
    if (wallToEdit) {
      setEditingWallId(id);
      setEditingWallData({ ...wallToEdit });
    }
  };

  const handleEditWallChange = (
    e: ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setEditingWallData((prev) =>
      prev
        ? {
          ...prev,
          [name]:
            name === "wall_id" || name === "area" ? Number(value) : value,
        }
        : null
    );
  };

  const handleAcceptEditWall = async (id: number) => {
    if (!editingWallData) return;
    const authData = getAuthData();
    if (!authData) return;
    const updateId = editingWallData.id || id;
    try {
      const response = await fetch(
        `${constantUrlApiEndpoint}/wall-enclosures-update/${updateId}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${authData.token}`,
          },
          body: JSON.stringify({
            wall_id: editingWallData.wall_id,
            characteristics: editingWallData.characteristics,
            angulo_azimut: editingWallData.angulo_azimut,
            area: editingWallData.area,
          }),
        }
      );
      if (!response.ok) throw new Error("Error al actualizar muro");
      notify("Muro actualizado exitosamente");
      setEditingWallId(null);
      setEditingWallData(null);
      fetchData();
    } catch (error) {
      notify("Error al actualizar muro");
      console.error(error);
    }
  };

  const handleCancelEditWall = () => {
    setEditingWallId(null);
    setEditingWallData(null);
  };

  // Abrir modal de confirmación para eliminación de muro
  const handleOpenDeleteModal = (wall: Wall) => {
    setWallToDelete(wall);
    setIsDeleteModalOpen(true);
  };

  // Función para eliminar el muro y su puente térmico asociado (si lo tiene)
  const handleConfirmDeleteWall = async () => {
    if (!wallToDelete) return;
    const authData = getAuthData();
    if (!authData) return;
    try {
      // Eliminar el muro
      const responseWall = await fetch(
        `${constantUrlApiEndpoint}/wall-enclosures-delete/${wallToDelete.id}`,
        {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${authData.token}`,
          },
        }
      );
      if (!responseWall.ok) throw new Error("Error al eliminar muro");
      // Si existe puente asociado se elimina también
      const thermalBridgeAsociado = puentesData.find(
        (bridge) => bridge.wall_id === wallToDelete.id
      );
      if (thermalBridgeAsociado) {
        const responseBridge = await fetch(
          `${constantUrlApiEndpoint}/thermal-bridge-delete/${thermalBridgeAsociado.id}`,
          {
            method: "DELETE",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${authData.token}`,
            },
          }
        );
        if (!responseBridge.ok)
          throw new Error("Error al eliminar puente térmico");
      }
      notify("Muro y puente térmico eliminados exitosamente.");
      setIsDeleteModalOpen(false);
      setWallToDelete(null);
      fetchData();
    } catch (error) {
      notify("Error al eliminar muro o puente térmico");
      console.error(error);
    }
  };

  const handleCancelDelete = () => {
    setIsDeleteModalOpen(false);
    setWallToDelete(null);
  };

  // Funciones para edición de puentes térmicos (dentro de la misma tabla)
  const handleEditBridge = (bridgeId: number | null) => {
    if (!bridgeId) return;
    const bridgeToEdit = puentesData.find((b) => b.id === bridgeId);
    if (bridgeToEdit) {
      setEditingBridgeId(bridgeId);
      setEditingBridgeData({ ...bridgeToEdit });
    }
  };

  const handleEditBridgeChange = (
    e: ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setEditingBridgeData((prev) =>
      prev
        ? { ...prev, [name]: name.startsWith("po") ? Number(value) : value }
        : null
    );
  };

  const handleAcceptEditBridge = async (bridgeId: number | null) => {
    if (!bridgeId || !editingBridgeData) return;
    const authData = getAuthData();
    if (!authData) return;
    try {
      const response = await fetch(
        `${constantUrlApiEndpoint}/thermal-bridge-update/${bridgeId}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${authData.token}`,
          },
          body: JSON.stringify(editingBridgeData),
        }
      );
      if (!response.ok) throw new Error("Error al actualizar puente térmico");
      notify("Puente térmico actualizado exitosamente");
      setEditingBridgeId(null);
      setEditingBridgeData(null);
      fetchData();
    } catch (error) {
      notify("Error al actualizar puente térmico");
      console.error(error);
    }
  };

  const handleCancelEditBridge = () => {
    setEditingBridgeId(null);
    setEditingBridgeData(null);
  };

  const handleCloseEditBridge = () => {
    setShowModalThermicBridges(false);
    setEditingBridgeId(null);
    setEditingBridgeData(null);
  };

  // Columnas para la tabla de muros
  const murosColumns = [
    {
      headerName: "Muros",
      field: "name",
      renderCell: (row: MergedWall) => {
        if (row.id === editingWallId && editingWallData) {
          return (
            <select
              name="wall_id"
              value={editingWallData.wall_id}
              onChange={handleEditWallChange}
              className="form-control form-control-sm"
            >
              <option value="">Seleccione...</option>
              {wallOptions.map((wall) => (
                <option key={wall.id} value={wall.id}>
                  {wall.name_detail}
                </option>
              ))}
            </select>
          );
        }
        return row.name;
      },
    },
    {
      headerName: "Caracteristicas",
      field: "characteristics",
      renderCell: (row: MergedWall) => {
        if (row.id === editingWallId && editingWallData) {
          return (
            <select
              name="characteristics"
              value={editingWallData.characteristics}
              onChange={handleEditWallChange}
              className="form-control form-control-sm"
            >
              <option value="">Seleccione...</option>
              <option value="Exterior">Exterior</option>
              <option value="Interior climatizado">Interior climatizado</option>
              <option value="Interior no climatizado">
                Interior no climatizado
              </option>
            </select>
          );
        }
        return row.characteristics;
      },
    },

    {
      headerName: "Ángulo Azimut",
      field: "angulo_azimut",
      renderCell: (row: MergedWall) => {
        return row.angulo_azimut;
      },
    },
    {
      headerName: "Orientación",
      field: "orientation",
      renderCell: (row: MergedWall) => {
        const value = row.orientation;
        if (row.id === editingWallId && editingWallData) {
          return (
              <select
                  name="angulo_azimut"
                  value={editingWallData.angulo_azimut}
                  onChange={handleEditWallChange}
                  onKeyDown={preventDash}
                  className="form-control form-control-sm"
              >
                <option value="">Seleccione...</option>
                {angleOptions.map((option, index) => (
                    <option key={index} value={option.azimut}>
                      {option.orientation}
                    </option>
                ))}
              </select>
          );
        }
        return value === "N/A" ||
        value === "0" ||
        value?.toString() === "0" ||
        !value
            ? "-"
            : value;
      },
    },
    {
      headerName: "Área [m²]",
      field: "area",
      renderCell: (row: MergedWall) => {
        if (row.id === editingWallId && editingWallData) {
          return (
            <input
              type="number"
              name="area"
              min="0"
              step="0.01"
              value={editingWallData.area}
              onKeyDown={(e) => {
                if (e.key === "-") {
                  e.preventDefault();
                }
              }}
              onChange={handleEditWallChange}
              onBlur={(e) => {
                const rounded = parseFloat(e.target.value).toFixed(2);
                setEditingWallData({
                  ...editingWallData,
                  area: Number(rounded),
                });
              }}
              className="form-control form-control-sm"
            />
          );
        }
        return formatValue(row.area, 2);
      },
    },
    {
      headerName: "U [W/m²K]",
      field: "u",
      renderCell: (row: MergedWall) => formatValue(row.u, 2),
    },
    {
      headerName: "Acciones",
      field: "acciones",
      renderCell: (row: MergedWall) => {
        const isEditing = row.id === editingWallId;
        return isEditing ? (
          <ActionButtonsConfirm
            onAccept={() => handleAcceptEditWall(row.id!)}
            onCancel={handleCancelEditWall}
          />
        ) : (
          //Open ThermalBridgesModal
          <ActionButtons
            onEdit={() => handleEditWall(row.id!)}
            onDelete={() => handleOpenDeleteModal(row)}
            onThermalBridge={() =>
              handleThermicBridgesWall(row.bridgeId ?? null)
            }
          />
        );
      },
    },
  ];

  // Columnas para los campos de puentes térmicos
  const puentesColumns = [
    {
      headerName: "P01 - L[m]",
      field: "po1_length",
      renderCell: (row: MergedWall) => {
        if (row.bridgeId === editingBridgeId && editingBridgeData) {
          return (
            <input
              type="number"
              name="po1_length"
              min="0"
              step="0.01"
              value={editingBridgeData.po1_length}
              onKeyDown={(e) => {
                if (e.key === "-") e.preventDefault();
              }}
              onChange={handleEditBridgeChange}
              onBlur={(e) => {
                const rounded = parseFloat(e.target.value).toFixed(2);
                setEditingBridgeData({
                  ...editingBridgeData,
                  po1_length: Number(rounded),
                });
              }}
              className="form-control form-control-sm"
            />
          );
        }
        return formatValue(row.po1_length, 2);
      },
    },
    {
      headerName: "P01 - Elemento",
      field: "po1_id_element",
      renderCell: (row: MergedWall) => {
        if (row.bridgeId === editingBridgeId && editingBridgeData) {
          return (
            <select
              name="po1_id_element"
              value={editingBridgeData.po1_id_element}
              onChange={handleEditBridgeChange}
              className="form-control form-control-sm"
            >
              <option value="">Seleccione...</option>
              {detailOptions.map((detail) => (
                <option key={detail.id} value={detail.id}>
                  {detail.name_detail}
                </option>
              ))}
            </select>
          );
        }
        const element = row.po1_element_name || row.po1_id_element;
        return formatValue(element);
      },
    },
    {
      headerName: "P02 - L[m]",
      field: "po2_length",
      renderCell: (row: MergedWall) => {
        if (row.bridgeId === editingBridgeId && editingBridgeData) {
          return (
            <input
              type="number"
              name="po2_length"
              min="0"
              step="0.01"
              value={editingBridgeData.po2_length}
              onKeyDown={(e) => {
                if (e.key === "-") e.preventDefault();
              }}
              onChange={handleEditBridgeChange}
              onBlur={(e) => {
                const rounded = parseFloat(e.target.value).toFixed(2);
                setEditingBridgeData({
                  ...editingBridgeData,
                  po2_length: Number(rounded),
                });
              }}
              className="form-control form-control-sm"
            />
          );
        }
        return formatValue(row.po2_length, 2);
      },
    },
    {
      headerName: "P02 - Elemento",
      field: "po2_id_element",
      renderCell: (row: MergedWall) => {
        if (row.bridgeId === editingBridgeId && editingBridgeData) {
          return (
            <select
              name="po2_id_element"
              value={editingBridgeData.po2_id_element}
              onChange={handleEditBridgeChange}
              className="form-control form-control-sm"
            >
              <option value="">Seleccione...</option>
              {detailOptions.map((detail) => (
                <option key={detail.id} value={detail.id}>
                  {detail.name_detail}
                </option>
              ))}
            </select>
          );
        }
        const element = row.po2_element_name || row.po2_id_element;
        return formatValue(element);
      },
    },
    {
      headerName: "P03 - L[m]",
      field: "po3_length",
      renderCell: (row: MergedWall) => {
        if (row.bridgeId === editingBridgeId && editingBridgeData) {
          return (
            <input
              type="number"
              name="po3_length"
              min="0"
              step="0.01"
              value={editingBridgeData.po3_length}
              onKeyDown={(e) => {
                if (e.key === "-") e.preventDefault();
              }}
              onChange={handleEditBridgeChange}
              onBlur={(e) => {
                const rounded = parseFloat(e.target.value).toFixed(2);
                setEditingBridgeData({
                  ...editingBridgeData,
                  po3_length: Number(rounded),
                });
              }}
              className="form-control form-control-sm"
            />
          );
        }
        return formatValue(row.po3_length, 2);
      },
    },
    {
      headerName: "P03 - Elemento",
      field: "po3_id_element",
      renderCell: (row: MergedWall) => {
        if (row.bridgeId === editingBridgeId && editingBridgeData) {
          return (
            <select
              name="po3_id_element"
              value={editingBridgeData.po3_id_element}
              onChange={handleEditBridgeChange}
              className="form-control form-control-sm"
            >
              <option value="">Seleccione...</option>
              {detailOptions.map((detail) => (
                <option key={detail.id} value={detail.id}>
                  {detail.name_detail}
                </option>
              ))}
            </select>
          );
        }
        const element = row.po3_element_name || row.po3_id_element;
        return formatValue(element);
      },
    },
    {
      headerName: "P04 - L[m]",
      field: "po4_length",
      renderCell: (row: MergedWall) => {
        if (row.bridgeId === editingBridgeId && editingBridgeData) {
          return (
            <input
              type="number"
              name="po4_length"
              min="0"
              step="0.01"
              value={editingBridgeData.po4_length}
              onKeyDown={(e) => {
                if (e.key === "-") e.preventDefault();
              }}
              onChange={handleEditBridgeChange}
              onBlur={(e) => {
                const rounded = parseFloat(e.target.value).toFixed(2);
                setEditingBridgeData({
                  ...editingBridgeData,
                  po4_length: Number(rounded),
                });
              }}
              className="form-control form-control-sm"
            />
          );
        }
        return formatValue(row.po4_length, 2);
      },
    },
    {
      headerName: "P04 - e Aislación [cm]",
      field: "po4_e_aislacion",
      renderCell: (row: MergedWall) => {
        if (row.bridgeId === editingBridgeId && editingBridgeData) {
          return (
            <input
              type="number"
              name="po4_e_aislacion"
              min="0"
              step="0.01"
              value={editingBridgeData.po4_e_aislacion}
              onKeyDown={(e) => {
                if (e.key === "-") e.preventDefault();
              }}
              onChange={handleEditBridgeChange}
              onBlur={(e) => {
                const rounded = parseFloat(e.target.value).toFixed(2);
                setEditingBridgeData({
                  ...editingBridgeData,
                  po4_e_aislacion: Number(rounded),
                });
              }}
              className="form-control form-control-sm"
            />
          );
        }
        return formatValue(row.po4_e_aislacion, 2);
      },
    },
    {
      headerName: "P04 - Elemento",
      field: "po4_id_element",
      renderCell: (row: MergedWall) => {
        if (row.bridgeId === editingBridgeId && editingBridgeData) {
          return (
            <select
              name="po4_id_element"
              value={editingBridgeData.po4_id_element}
              onChange={handleEditBridgeChange}
              className="form-control form-control-sm"
            >
              <option value="">Seleccione...</option>
              {detailOptions.map((detail) => (
                <option key={detail.id} value={detail.id}>
                  {detail.name_detail}
                </option>
              ))}
            </select>
          );
        }
        const element = row.po4_element_name || row.po4_id_element;
        return formatValue(element);
      },
    },
    {
      headerName: "Acciones",
      field: "acciones_thermal",
      cellStyle: {
        position: "sticky",
        right: "0px",
        background: "#fff",
        zIndex: 1,
      },
      renderCell: (row: MergedWall) => {
        // Usamos la propiedad bridgeId para identificar el puente
        const currentBridgeId = row.bridgeId;
        const isEditing = currentBridgeId === editingBridgeId;
        return isEditing ? (
          <ActionButtonsConfirm
            onAccept={() => handleAcceptEditBridge(currentBridgeId)}
            onCancel={handleCancelEditBridge}
          />
        ) : // Solo mostramos el botón si existe un puente asociado (bridgeId no es null)
          currentBridgeId ? (
            <CustomButton
              variant="editIcon"
              onClick={() => handleEditBridge(currentBridgeId)}
            >
              Editar FAV
            </CustomButton>
          ) : null;
      },
    },
  ];

  // Fusionar las columnas de muros y puentes térmicos en el orden actual
  // const mergedColumns = [...murosColumns, ...puentesColumns];
  const mergedColumns = [...murosColumns];

  // Crear un multiheader único
  const mergedMultiHeader = {
    rows: [
      // [{ label: "Muros", colSpan: mergedColumns.length }],
      [
        ...[
          { label: "Muros" },
          { label: "Características espacio contiguo al elemento" },
          { label: "Ángulo Azimut" },
          { label: "Orientación" },
          { label: "Área[m²]" },
          { label: "U [W/m²K]" },
          { label: "Acciones" },
        ],
      ],
    ],
  };

  // Renderizado único: se muestra solo la tabla fusionada y el botón de “Nuevo Muro”
  const renderContent = () => (
    <div className="col-12">
      <div className="d-flex justify-content-end gap-2 mt-3 w-100">
        <CustomButton variant="save" onClick={() => setIsWallModalOpen(true)}>
          <Plus className="me-1" size={16} />
          Nuevo Muro
        </CustomButton>
      </div>
      <div className="table-responsive">
        <TablesParameters
          columns={mergedColumns}
          data={mergedData}
          multiHeader={mergedMultiHeader}
        />
      </div>
    </div>
  );

  // Manejo del formulario del modal para creación de muro
  const handleWallInputChange = (
    e: ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setNewWall((prev) => ({
      ...prev,
      [name]: name === "wall_id" || name === "area" ? Number(value) : value,
    }));
  };

  // Función para crear un muro
  const handleCreateWall = async () => {
    if (
      newWall.wall_id <= 0 ||
      newWall.characteristics.trim() === "" ||
      newWall.angulo_azimut.trim() === "" ||
      newWall.area <= 0
    ) {
      notify("Debe completar todos los campos del muro");
      return;
    }
    const authData = getAuthData();
    if (!authData) return;
    const { token, enclosure_id } = authData;
    const url = `${constantUrlApiEndpoint}/wall-enclosures-create/${enclosure_id}`;
    console.log("url", url);
    try {
      console.log("url dentro del try", url);
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(newWall),
      });
      if (!response.ok) throw new Error("Error en la creación del muro.");
      notify("Muro creado exitosamente");
      setIsWallModalOpen(false);
      setNewWall({
        wall_id: 0,
        name: "",
        characteristics: "",
        angulo_azimut: "",
        area: 0,
      });
      fetchData();
    } catch (error) {
      notify("Error al crear el muro");
      console.error(error);
    }
  };

  //thermalBridges Button on Actions
  function handleThermicBridgesWall(bridgeId: number | null) {
    // console.log("Puentes térmicos para el bridgeId:", bridgeId);
    // console.log("puentesData", puentesData);
    handleEditBridge(bridgeId);
    // console.log("editingBridgeData", editingBridgeData);
    // console.log("detailOptions", detailOptions);
    setShowModalThermicBridges(true);
  }

  return (
    <>
      <GoogleIcons />
      <div className="container-fluid">
        {renderContent()}
        <ModalCreate
          isOpen={isWallModalOpen}
          onClose={() => setIsWallModalOpen(false)}
          onSave={handleCreateWall}
          title="Crear Nuevo Muro"
          saveLabel="Crear Muro"
        >
          <form>
            <div className="row align-items-center mb-3">
              <label htmlFor="wall_id" className="col-sm-3 col-form-label">
                Muro
              </label>
              <div className="col-sm-9">
                <select
                  id="wall_id"
                  name="wall_id"
                  className="form-control form-control-sm"
                  value={newWall.wall_id || ""}
                  onChange={handleWallInputChange}
                >
                  <option value="">Seleccione...</option>
                  {wallOptions.map((wall) => (
                    <option key={wall.id} value={wall.id}>
                      {wall.name_detail}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="row align-items-center mb-3">
              <label
                htmlFor="characteristics"
                className="col-sm-3 col-form-label"
              >
                Características del recinto continuo
              </label>
              <div className="col-sm-9">
                <select
                  id="characteristics"
                  name="characteristics"
                  className="form-control form-control-sm"
                  value={newWall.characteristics}
                  onChange={handleWallInputChange}
                >
                  <option value="">Seleccione...</option>
                  <option value="Exterior">Exterior</option>
                  <option value="Interior climatizado">
                    Interior climatizado
                  </option>
                  <option value="Interior no climatizado">
                    Interior no climatizado
                  </option>
                </select>
              </div>
            </div>
            <div className="row align-items-center mb-3">
              <label
                htmlFor="angulo_azimut"
                className="col-sm-3 col-form-label"
              >
                Orientación [°]
              </label>
              <div className="col-sm-9">
                <select
                  id="angulo_azimut"
                  name="angulo_azimut"
                  className="form-control form-control-sm"
                  value={newWall.angulo_azimut}
                  onChange={handleWallInputChange}
                >
                  <option value="">Seleccione...</option>
                  {angleOptions.map((option, index) => (
                    <option key={index} value={option.azimut}>
                       {option.orientation}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="row align-items-center mb-3">
              <label htmlFor="area" className="col-sm-3 col-form-label">
                Área [m²]
              </label>
              <div className="col-sm-9">
                <input
                  id="area"
                  min="0"
                  type="number"
                  name="area"
                  className="form-control form-control-sm"
                  value={newWall.area}
                  onKeyDown={(e) => {
                    if (e.key === "-") e.preventDefault();
                  }}
                  onChange={handleWallInputChange}
                />
              </div>
            </div>
          </form>
        </ModalCreate>
        <ModalCreate
          isOpen={isDeleteModalOpen}
          onClose={handleCancelDelete}
          onSave={handleConfirmDeleteWall}
          title="Confirmar Eliminación"
          saveLabel="Eliminar"
        >
          {wallToDelete && (
            <p>
              ¿Está seguro de eliminar el muro{" "}
              <strong>{wallToDelete.name}</strong>?
            </p>
          )}
        </ModalCreate>
        <ThermalBridgesWallModal
          isOpen={showModalThermicBridges}
          handleClose={handleCloseEditBridge}
          bridgeId={editingBridgeId}
          bridgeData={editingBridgeData}
          detailOptions={detailOptions}
          onSaveSuccess={fetchData} // Pass the fetch function as a callback
        />
      </div>
    </>
  );
};

export default TabMuroCreate;
