import ActionButtons from "@/components/common/ActionButtons";
import ActionButtonsConfirm from "@/components/common/ActionButtonsConfirm";
import TablesParameters from "@/components/tables/TablesParameters";
import { constantUrlApiEndpoint } from "@/utils/constant-url-endpoint";
import { notify } from "@/utils/notify";
import "bootstrap/dist/css/bootstrap.min.css";
import { Plus } from "lucide-react";
import React, { ChangeEvent, useEffect, useState } from "react";
import CustomButton from "../common/CustomButton";
import ModalCreate from "../common/ModalCreate";
import ThermalBridgesWallModal from "../modals/ThermalBridgesWallModal";
import { azimutRangeToOrientation } from "@/utils/azimut";

import useFetchAngleOptions from "@/hooks/useFetchAngleOptions";
import { displayValue } from "@/utils/formatters";
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

// Interfaz para puentes térmicos
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

// Interfaz para las opciones de desplegable (tanto para muros como para elementos de puente térmico)
interface WallDetail {
  type: string;
  id: number;
  info: any;
  value_u: number;
  created_status: string;
  name_detail: string;
  project_id: number;
}

// Interfaz para la data fusionada (muro + puente) con propiedad bridgeId para el id del puente
interface MergedWall extends Omit<Wall, "wall_id">, Partial<ThermalBridge> {
  wall_id: number;
  bridgeId?: number | null;
}

const TabMuroCreate: React.FC = () => {
  // Función auxiliar para prevenir ingreso de guion "-"
  const preventDash = (
    e: React.KeyboardEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    if (e.key === "-") e.preventDefault();
  };

  // Estados de modales
  const [isWallModalOpen, setIsWallModalOpen] = useState<boolean>(false);
  // Modal de confirmación para eliminación de muro
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState<boolean>(false);
  const [wallToDelete, setWallToDelete] = useState<Wall | null>(null);
  // Modal de confirmación para eliminación de puente térmico
  const [isDeleteBridgeModalOpen, setIsDeleteBridgeModalOpen] =
    useState<boolean>(false);
  const [bridgeToDelete, setBridgeToDelete] = useState<ThermalBridge | null>(
    null
  );

  // Estados de datos de la API
  const [murosData, setMurosData] = useState<Wall[]>([]);
  const [puentesData, setPuentesData] = useState<ThermalBridge[]>([]);
  // Data fusionada para la tabla unificada
  const [mergedData, setMergedData] = useState<MergedWall[]>([]);

  // Estados para edición de muros
  const [editingWallId, setEditingWallId] = useState<number | null>(null);
  const [editingWallData, setEditingWallData] = useState<Wall | null>(null);

  // Estados para edición de puentes térmicos
  const [editingBridgeId, setEditingBridgeId] = useState<number | null>(null);
  const [editingBridgeData, setEditingBridgeData] =
    useState<ThermalBridge | null>(null);

  // Otras opciones y datos de formularios
  const [angleOptions] = useFetchAngleOptions();
  const [wallOptions, setWallOptions] = useState<WallDetail[]>([]);
  const [detailOptions, setDetailOptions] = useState<WallDetail[]>([]);
  const [projectId, setProjectId] = useState<string | null>(null);

  // Formularios para creación
  const [newWall, setNewWall] = useState<Wall>({
    wall_id: 0,
    name: "",
    characteristics: "",
    angulo_azimut: "",
    area: 0,
  });
  const [newThermalBridge, setNewThermalBridge] = useState<ThermalBridge>({
    id: 0,
    wall_id: 0,
    po1_length: 0,
    po1_id_element: 0,
    po2_length: 0,
    po2_id_element: 0,
    po3_length: 0,
    po3_id_element: 0,
    po4_length: 0,
    po4_e_aislacion: 0,
    po4_id_element: 0,
  });

  //ThermalBridgesModal OPEN
  const [showModalThermicBridges, setShowModalThermicBridges] =
    useState<boolean>(false);
  //ThermalBridgesModal FIN

  // Obtener el project_id desde localStorage
  useEffect(() => {
    const storedProjectId = localStorage.getItem("project_id");
    if (storedProjectId) {
      setProjectId(storedProjectId);
    }
  }, []);

  // Cargar datos cuando se active el projectId
  useEffect(() => {
    if (projectId) {
      fetchData();
    }
  }, [projectId]);

  // Función para obtener token y enclosure_id
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

  // Obtener opciones para muros (desplegable)
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

  // Obtener opciones de detalles (elementos para puente térmico)
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
      // Obtener muros
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

      // Obtener puentes térmicos
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

      // Mantener el orden original usando el ID como referencia
      setMurosData(muros);
      setPuentesData(puentes);

      // Fusionar datos manteniendo el orden original de muros
      const merged = muros.map((muro: Wall) => {
        const puente = puentes.find(
          (p: ThermalBridge & { wall_id?: number }) => p.wall_id === muro.id
        );
        return {
          ...muro,
          ...puente,
          id: muro.id,
          bridgeId: puente ? puente.id : null,
        };
      });

      // Si hay datos existentes, mantener el orden anterior
      if (mergedData.length > 0) {
        const orderedMerged = merged.sort((a: MergedWall, b: MergedWall) => {
          const aIndex = mergedData.findIndex((item) => item.id === a.id);
          const bIndex = mergedData.findIndex((item) => item.id === b.id);
          if (aIndex === -1) return 1;
          if (bIndex === -1) return -1;
          return aIndex - bIndex;
        });
        setMergedData(orderedMerged);
      } else {
        setMergedData(merged);
      }
    } catch (error) {
      notify("Error al cargar los datos");
      console.error(error);
    }
  };

  // Funciones de edición de muro (en línea)
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

  // Modal de eliminación de muro
  const handleOpenDeleteModal = (wall: Wall) => {
    setWallToDelete(wall);
    setIsDeleteModalOpen(true);
  };

  const handleConfirmDeleteWall = async () => {
    if (!wallToDelete) return;
    const authData = getAuthData();
    if (!authData) return;
    try {
      const response = await fetch(
        `${constantUrlApiEndpoint}/wall-enclosures-delete/${wallToDelete.id}`,
        {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${authData.token}`,
          },
        }
      );
      if (!response.ok) throw new Error("Error al eliminar muro");
      const data = await response.json();
      notify(data.mensaje || "Muro eliminado exitosamente.");
      setIsDeleteModalOpen(false);
      setWallToDelete(null);
      fetchData();
    } catch (error) {
      notify("Error al eliminar muro");
      console.error(error);
    }
  };

  const handleCancelDelete = () => {
    setIsDeleteModalOpen(false);
    setWallToDelete(null);
  };

  // Funciones de edición de puente térmico (en línea)
  const handleEditBridge = (bridgeId: number) => {
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

  const handleAcceptEditBridge = async (bridgeId: number) => {
    if (!editingBridgeData) return;
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

  // Modal de eliminación de puente térmico
  const handleOpenDeleteBridgeModal = (bridge: ThermalBridge) => {
    setBridgeToDelete(bridge);
    setIsDeleteBridgeModalOpen(true);
  };

  const handleConfirmDeleteBridge = async () => {
    if (!bridgeToDelete) return;
    const authData = getAuthData();
    if (!authData) return;
    try {
      const response = await fetch(
        `${constantUrlApiEndpoint}/thermal-bridge-delete/${bridgeToDelete.id}`,
        {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${authData.token}`,
          },
        }
      );
      if (!response.ok) throw new Error("Error al eliminar puente térmico");
      const data = await response.json();
      notify(data.mensaje || "Puente térmico eliminado exitosamente.");
      setIsDeleteBridgeModalOpen(false);
      setBridgeToDelete(null);
      fetchData();
    } catch (error) {
      notify("Error al eliminar puente térmico");
      console.error(error);
    }
  };

  const handleCancelDeleteBridge = () => {
    setIsDeleteBridgeModalOpen(false);
    setBridgeToDelete(null);
  };
  function handleThermicBridgesWall(bridgeId: number) {
    // console.log("Puentes térmicos para el bridgeId:", bridgeId);
    // console.log("puentesData", puentesData);
    handleEditBridge(bridgeId);
    // console.log("editingBridgeData", editingBridgeData);
    // console.log("detailOptions", detailOptions);
    setShowModalThermicBridges(true);
  }
  const handleCloseEditBridge = () => {
    setShowModalThermicBridges(false);
    setEditingBridgeId(null);
    setEditingBridgeData(null);
  };

  // --- Unificación de Tablas ---
  // Las columnas de muros
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
              onKeyDown={preventDash}
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
              onKeyDown={preventDash}
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
              onChange={handleEditWallChange}
              onKeyDown={preventDash}
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
        const area = Number(row.area);
        return area === 0 ? "-" : displayValue(area, true);
      },
    },
    {
      headerName: "U [W/m²K]",
      field: "u",
      renderCell: (row: MergedWall) => {
        const u = row.u;
        if (u === 0 || u === undefined || u === null || typeof u === "string") {
          return <span>-</span>;
        }
        return <span>{Number(u).toFixed(2)}</span>;
      },
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
          <ActionButtons
            onEdit={() => handleEditWall(row.id!)}
            onDelete={() => handleOpenDeleteModal(row)}
            onThermalBridge={() => handleThermicBridgesWall(row.bridgeId!)}
          />
        );
      },
    },
  ];

  // Las columnas para los campos de puente térmico
  const puentesColumns = [
    {
      headerName: "L[m]",
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
              onChange={handleEditBridgeChange}
              onKeyDown={preventDash}
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
        const len = Number(row.po1_length);
        return len === 0 ? "-" : len.toFixed(2);
      },
    },
    {
      headerName: "Elemento",
      field: "po1_id_element",
      renderCell: (row: MergedWall) => {
        if (row.bridgeId === editingBridgeId && editingBridgeData) {
          return (
            <select
              name="po1_id_element"
              value={editingBridgeData.po1_id_element}
              onChange={handleEditBridgeChange}
              onKeyDown={preventDash}
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
        return element === 0 || element === "N/A" ? "-" : element;
      },
    },
    {
      headerName: "L[m]",
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
              onChange={handleEditBridgeChange}
              onKeyDown={preventDash}
              className="form-control form-control-sm"
            />
          );
        }
        const len = Number(row.po2_length);
        return len === 0 ? "-" : len.toString();
      },
    },
    {
      headerName: "Elemento",
      field: "po2_id_element",
      renderCell: (row: MergedWall) => {
        if (row.bridgeId === editingBridgeId && editingBridgeData) {
          return (
            <select
              name="po2_id_element"
              value={editingBridgeData.po2_id_element}
              onChange={handleEditBridgeChange}
              onKeyDown={preventDash}
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
        return element === 0 || element === "N/A" ? "-" : element;
      },
    },
    {
      headerName: "L[m]",
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
              onChange={handleEditBridgeChange}
              onKeyDown={preventDash}
              className="form-control form-control-sm"
            />
          );
        }
        const len = Number(row.po3_length);
        return len === 0 ? "-" : len.toString();
      },
    },
    {
      headerName: "Elemento",
      field: "po3_id_element",
      renderCell: (row: MergedWall) => {
        if (row.bridgeId === editingBridgeId && editingBridgeData) {
          return (
            <select
              name="po3_id_element"
              value={editingBridgeData.po3_id_element}
              onChange={handleEditBridgeChange}
              onKeyDown={preventDash}
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
        return element === 0 || element === "N/A" ? "-" : element;
      },
    },
    {
      headerName: "L[m]",
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
              onChange={handleEditBridgeChange}
              onKeyDown={preventDash}
              className="form-control form-control-sm"
            />
          );
        }
        const len = Number(row.po4_length);
        return len === 0 ? "-" : len.toString();
      },
    },
    {
      headerName: "e Aislación [cm]",
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
              onChange={handleEditBridgeChange}
              onKeyDown={preventDash}
              className="form-control form-control-sm"
            />
          );
        }
        const espesor = Number(row.po4_e_aislacion);
        return espesor === 0 ? "-" : espesor.toString();
      },
    },
    {
      headerName: "Elemento",
      field: "po4_id_element",
      renderCell: (row: MergedWall) => {
        if (row.bridgeId === editingBridgeId && editingBridgeData) {
          return (
            <select
              name="po4_id_element"
              value={editingBridgeData.po4_id_element}
              onChange={handleEditBridgeChange}
              onKeyDown={preventDash}
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
        return element === 0 || element === "N/A" ? "-" : element;
      },
    },
    {
      headerName: "Acciones",
      field: "acciones_thermal",
      renderCell: (row: MergedWall) => {
        const currentBridgeId = row.bridgeId;
        const isEditing = currentBridgeId === editingBridgeId;
        return isEditing ? (
          <ActionButtonsConfirm
            onAccept={() => handleAcceptEditBridge(currentBridgeId!)}
            onCancel={handleCancelEditBridge}
          />
        ) : currentBridgeId ? (
          <CustomButton
            variant="editIcon"
            onClick={() => handleEditBridge(currentBridgeId)}
          ></CustomButton>
        ) : null;
      },
    },
  ];

  // Fusionar las columnas: primero las de muros y luego las de puentes térmicos
  // const mergedColumns = [...murosColumns, ...puentesColumns];
  const mergedColumns = [...murosColumns];

  // Crear un multiheader unificado (primer fila con título global y segunda fila con las etiquetas en orden)
  const mergedMultiHeader = {
    rows: [
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

  // Renderizar la tabla unificada y mostrar un único botón para "Nuevo Muro"
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

  // Manejo del formulario en modal para crear muro
  const handleWallInputChange = (
    e: ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setNewWall((prev) => ({
      ...prev,
      [name]: name === "wall_id" || name === "area" ? Number(value) : value,
    }));
  };

  // Manejo del formulario en modal para crear puente térmico (aunque en la tabla unificada se elimina el botón de creación)
  const handleThermalBridgeInputChange = (
    e: ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setNewThermalBridge((prev) => ({
      ...prev,
      [name]: Number(value),
    }));
  };

  // Función para crear muro (modal de creación)
  const handleCreateWall = async () => {
    if (
      newWall.wall_id === 0 ||
      newWall.characteristics.trim() === "" ||
      newWall.angulo_azimut.trim() === "" ||
      newWall.area === 0
    ) {
      notify("Todos los campos son obligatorios para crear el muro");
      return;
    }
    const authData = getAuthData();
    if (!authData) return;
    const { token, enclosure_id } = authData;
    const url = `${constantUrlApiEndpoint}/wall-enclosures-create/${enclosure_id}`;
    try {
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

  // (Opcionalmente, se podrían mantener las funciones de creación y eliminación de puente térmico)
  // Renderizamos los modales (se mantienen los de eliminación)
  return (
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
                onKeyDown={preventDash}
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
                onKeyDown={preventDash}
              >
                <option value="">Seleccione...</option>
                <option value="Exterior">Exterior</option>
                <option value="Interior climatizado">Interior climatizado</option>
                <option value="Interior no climatizado">
                  Interior no climatizado
                </option>
              </select>
            </div>
          </div>
          <div className="row align-items-center mb-3">
            <label htmlFor="angulo_azimut" className="col-sm-3 col-form-label">
              Orientación [°]
            </label>
            <div className="col-sm-9">
              <select
                id="angulo_azimut"
                name="angulo_azimut"
                className="form-control form-control-sm"
                value={newWall.angulo_azimut}
                onChange={handleWallInputChange}
                onKeyDown={preventDash}
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
                type="number"
                name="area"
                className="form-control form-control-sm"
                value={newWall.area}
                min="0"
                onKeyDown={(e) => {
                  if (e.key === "-") {
                    e.preventDefault();
                  }
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
        saveLabel="Eliminar"
        title="Confirmar Eliminación"
      >
        {wallToDelete && (
          <p>
            ¿Está seguro de eliminar el muro{" "}
            <strong>{wallToDelete.name}</strong>?
          </p>
        )}
      </ModalCreate>
      <ModalCreate
        isOpen={isDeleteBridgeModalOpen}
        onClose={handleCancelDeleteBridge}
        onSave={handleConfirmDeleteBridge}
        saveLabel="Eliminar"
        title="Confirmar Eliminación"
      >
        {bridgeToDelete && (
          <p>
            ¿Está seguro de eliminar el puente térmico con id{" "}
            <strong>{bridgeToDelete.id}</strong>?
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
  );
};

export default TabMuroCreate;
