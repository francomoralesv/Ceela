// noinspection LanguageDetectionInspection

import HorizontalTabs from "@/components/common/HorizontalTabs";
import ProjectInfoHeader from "@/components/common/ProjectInfoHeader";
import NewHeaderButton from "@/components/constructive_details/NewHeaderButton";
import SearchParameters from "@/components/inputs/SearchParameters";
import { notify } from "@/utils/notify";
import axios from "axios";
import "bootstrap/dist/css/bootstrap.min.css";
import { useRouter } from "next/router";
import React, { useCallback, useEffect, useState } from "react";
import "react-toastify/dist/ReactToastify.css";
import Swal from "sweetalert2";
import GooIcons from "../public/GoogleIcons";
import Title from "../src/components/Title";
import { AdminSidebar } from "../src/components/administration/AdminSidebar";
import Card from "../src/components/common/Card";
import CustomButton from "../src/components/common/CustomButton";
import useAuth from "../src/hooks/useAuth";
import { constantUrlApiEndpoint } from "../src/utils/constant-url-endpoint";

import Breadcrumb from "@/components/common/Breadcrumb";
import ModalCreate from "@/components/common/ModalCreate";
import TabRecintDataCreate from "../src/components/tab_recint_data/TabRecintDataEdit";
import TablesParameters from "../src/components/tables/TablesParameters";

import ActionButtonsConfirm from "@/components/common/ActionButtonsConfirm";
import AddDetailOnLayer from "@/components/projects/AddDetailOnLayer";
import ProjectStatus from "@/components/projects/ProjectStatus";
import { useApi } from "@/hooks/useApi";

interface MultiHeader {
  rows: {
    label: string;
    field?: string;
    rowSpan?: number;
    colSpan?: number;
    sortable?: boolean;
  }[][];
}

import DeleteDetailButton from "@/components/common/DeleteDetailButton";
import AguaCalienteSanitaria from "@/components/projects/tabs/AguaCalienteSanitaria";
import ConfiguracionEnergiaTab from "@/components/projects/tabs/ConfiguracionEnergiaTab";
import { steps } from "@/constants/steps";
import { IDetail } from "@/shared/interfaces/detail.interface";

// Funciones auxiliares para formatear valores
const formatValue = (value: number | null | undefined): string => {
  if (
    value === undefined ||
    value === null ||
    value === 0 ||
    isNaN(Number(value))
  ) {
    return "-";
  }
  return Number(value).toFixed(2);
};

const formatPercentage = (value: number | null | undefined): string => {
  if (
    value === undefined ||
    value === null ||
    value === 0 ||
    isNaN(Number(value))
  ) {
    return "-";
  }
  return (Number(value) * 100).toFixed(2);
};

// -----------------------
// Modal de Detalles Individuales
// -----------------------
export interface Detail {
  id_detail: number;
  scantilon_location: string;
  name_detail: string;
  id_material: number;
  material: string;
  layer_thickness: number;
  created_status: string;
}

interface DetailModalProps {
  detail: Detail | null;
  show: boolean;
  onClose: () => void;
}

export const DetailModal: React.FC<DetailModalProps> = ({
  detail,
  show,
  onClose,
}) => {
  if (!detail) return null;
  const textStyle =
    detail.created_status === "created"
      ? { color: "var(--primary-color)", fontWeight: "bold" }
      : {};
  return (
    <ModalCreate
      detail={null}
      isOpen={show}
      onClose={onClose}
      onSave={onClose}
      title="Detalles Generales"
      hideFooter={false}
    >
      <p>
        <strong>Ubicación:</strong>{" "}
        <span style={textStyle}>{detail.scantilon_location}</span>
      </p>
      <p>
        <strong>Nombre:</strong>{" "}
        <span style={textStyle}>{detail.name_detail}</span>
      </p>
      <p>
        <strong>Material:</strong>{" "}
        <span style={textStyle}>{detail.material}</span>
      </p>
      <p>
        <strong>Espesor de capa:</strong>{" "}
        <span style={textStyle}>{detail.layer_thickness} cm</span>
      </p>
    </ModalCreate>
  );
};

// -----------------------
// Interfaces adicionales
// -----------------------
interface TabItem {
  code_ifc?: string;
  id_detail?: number;
  id?: number;
  name_detail: string;
  value_u?: number;
  info?: {
    surface_color?: {
      exterior?: { name: string; value?: number };
      interior?: { name: string; value?: number };
    };
    aislacion_bajo_piso?: {
      lambda?: number;
      e_aisl?: number;
    };
    ref_aisl_vertical?: {
      lambda?: number;
      e_aisl?: number;
      d?: number;
    };
    ref_aisl_horizontal?: {
      lambda?: number;
      e_aisl?: number;
      d?: number;
    };
  };
  scantilon_location?: string;
  material?: string;
  layer_thickness?: number;
}

interface Material {
  id: number;
  name: string;
}

interface Constant {
  create_status: string;
  name: string;
  type: string;
  id: number;
  atributs: {
    name: string;
    density: number;
    conductivity: number;
    specific_heat: number;
  };
  is_deleted: boolean;
}

type TabStep4 =
  | "detalles"
  | "muros"
  | "techumbre"
  | "pisos"
  | "ventanas"
  | "puertas";

interface Ventana {
  id: number;
  name_element: string;
  created_status?: string;
  atributs?: {
    u_vidrio?: number;
    fs_vidrio?: number;
    frame_type?: string;
    clousure_type?: string;
  };
  u_marco?: number;
  fm?: number;
}

interface Puerta {
  id: number;
  name_element: string;
  created_status?: string;
  atributs?: {
    u_puerta_opaca?: number;
    name_ventana?: string;
    porcentaje_vidrio?: number;
  };
  u_marco?: number;
  fm?: number;
}

// -----------------------
// Componente principal
// -----------------------
const WorkFlowpar2editPage: React.FC = () => {
  useAuth();
  const router = useRouter();
  const api = useApi();

  const [detailList, SetDetailsList] = useState<any>();
  const [selectedItem, SetSelectedItem] = useState<any>();


  const fetchDetailModal = (detail_id: any) => {
    api.get(`detail-part/${detail_id}`).then((data) => {
      SetDetailsList(data);
    });
  };


  const OnDetailOpened = (e: any) => {
    setShowDetallesModal(true);
    SetSelectedItem(e);
    fetchDetailModal(e?.id);
  };

  // ===================== ESTADOS GENERALES ======================
  const [projectId, setProjectId] = useState<number | null>(null);
  const [hasLoaded, setHasLoaded] = useState(false);
  const [step, setStep] = useState<number>(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      const stepParam = params.get('step');
      return stepParam ? parseInt(stepParam, 10) : 3;
    }
    return 3;
  });
  // Sincroniza el estado step con el query param de la URL
  useEffect(() => {
    if (router.query.step) {
      const stepParam = parseInt(router.query.step as string, 10);
      if (!isNaN(stepParam) && step !== stepParam) {
        setStep(stepParam);
      }
    }
  }, [router.query.step]);
  const [primaryColor, setPrimaryColor] = useState("#3ca7b7");
  const [searchQuery, setSearchQuery] = useState("");
  const [projectStatus, setProjectStatus] = useState("En proceso");

  // Estados para almacenar nombre de proyecto y región desde localStorage
  const [projectName, setProjectName] = useState("");
  const [region, setRegion] = useState("");

  // ===================== ESTADOS DETALLES ======================
  const [fetchedDetails, setFetchedDetails] = useState<Detail[]>([]);
  const [showNewDetailRow, setShowNewDetailRow] = useState(false);
  const [newDetailForm, setNewDetailForm] = useState<{
    scantilon_location: string;
    name_detail: string;
    material_id: number;
    layer_thickness: number | null;
  }>({
    scantilon_location: "",
    name_detail: "",
    material_id: 0,
    layer_thickness: null,
  });
  const [showTabsInStep4, setShowTabsInStep4] = useState(true);
  const [tabStep4, setTabStep4] = useState<TabStep4>("detalles");

  // ===================== ESTADOS PARA MODALES Y EDICIÓN ======================
  const [selectedDetail, setSelectedDetail] = useState<Detail | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showDetallesModal, setShowDetallesModal] = useState(false);
  const [editingDetail, setEditingDetail] = useState<IDetail | null>(null);

  // ===================== ESTADOS PARA VENTANAS, PUERTAS Y DEMÁS ======================
  interface ExtendedTabItem extends TabItem {
    created_status?: string;
  }

  const [murosTabList, setMurosTabList] = useState<ExtendedTabItem[]>([]);
  const [techumbreTabList, setTechumbreTabList] = useState<TabItem[]>([]);
  const [pisosTabList, setPisosTabList] = useState<TabItem[]>([]);
  const [ventanasTabList, setVentanasTabList] = useState<Ventana[]>([]);
  const [puertasTabList, setPuertasTabList] = useState<Puerta[]>([]);
  const [materials, setMaterials] = useState<Material[]>([]);

  // ===================== EDICIÓN MUROS / TECHUMBRE ======================
  const [editingRowId, setEditingRowId] = useState<number | null>(null);
  const [editingColors, setEditingColors] = useState<{
    interior: string;
    exterior: string;
    nombreAbreviado: string;
  }>({
    interior: "Intermedio",
    exterior: "Intermedio",
    nombreAbreviado: "",
  });
  const [editingTechRowId, setEditingTechRowId] = useState<number | null>(null);
  const [editingTechColors, setEditingTechColors] = useState<{
    interior: string;
    exterior: string;
    nombreAbreviado: string;
  }>({
    interior: "Intermedio",
    exterior: "Intermedio",
    nombreAbreviado: "",
  });
  // ===================== EDICIÓN PISOS ======================
  const [editingPisosRowId, setEditingPisosRowId] = useState<number | null>(
    null
  );
  const [editingPisosData, setEditingPisosData] = useState<{
    ref_aisl_vertical: { lambda: string; e_aisl: string; d: string };
    ref_aisl_horizontal: { lambda: string; e_aisl: string; d: string };
    nombre: string;
  }>({
    ref_aisl_vertical: { lambda: "", e_aisl: "", d: "" },
    ref_aisl_horizontal: { lambda: "", e_aisl: "", d: "" },
    nombre: "",
  });

  // ===================== EDICIÓN VENTANAS / PUERTAS ======================
  const [editingVentana, setEditingVentana] = useState<Ventana | null>(null);
  const [editingPuerta, setEditingPuerta] = useState<Puerta | null>(null);

  // ===================== MODAL DE CONFIRMACIÓN DE ELIMINACIÓN (NUEVO) ======================
  const [showDeleteLayerModal, setShowDeleteLayerModal] = useState(false);
  const [selectedDeleteDetailId, setSelectedDeleteDetailId] = useState<
    number | null
  >(null);

  // ===================== FETCH PROJECT DATA ======================
  const fetchProjectData = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) return;
      const { data: projectData } = await axios.get(
        `${constantUrlApiEndpoint}/projects/${projectId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setProjectStatus(projectData?.status || "En proceso");
    } catch (error: unknown) {
      console.error("Error fetching project data", error);
    }
  };

  useEffect(() => {
    if (projectId) {
      fetchProjectData();
    }
  }, [projectId]);

  // ===================== INIT ======================
  useEffect(() => {
    const storedProjectId =router.query.id || localStorage.getItem("project_id");
    if (storedProjectId) {
      setProjectId(Number(storedProjectId));
    }
    const storedProjectName = localStorage.getItem("project_name_edit") || "";
    const storedRegion = localStorage.getItem("project_department_edit") || "";
    setProjectName(storedProjectName);
    setRegion(storedRegion);
    setHasLoaded(true);
  }, []);

  useEffect(() => {
    if (hasLoaded && projectId === null) {
      Swal.fire(
        "Ningún proyecto está seleccionado",
        "Serás redirigido a la creación de proyecto",
        "warning"
      ).then(() => {
        router.push("/workflow-part1-edit");
      });
    }
  }, [hasLoaded, projectId, router]);



  useEffect(() => {
    const pColor =
      getComputedStyle(document.documentElement)
        .getPropertyValue("--primary-color")
        .trim() || "#3ca7b7";
    setPrimaryColor(pColor);
  }, []);

  // ===================== FUNCIONES AUXILIARES ======================
  const getToken = () => {
    const token = localStorage.getItem("token");
    if (!token) {
      Swal.fire("Token no encontrado", "Inicia sesión.");
    }
    return token;
  };

  const fetchData = useCallback(
    async <T,>(endpoint: string, setter: (data: T) => void) => {
      if (!projectId) return;
      const token = getToken();
      if (!token) return;
      try {
        const headers = { Authorization: `Bearer ${token}` };
        const response = await axios.get(endpoint, { headers });
        setter(response.data);
      } catch (error: unknown) {
        console.error(`Error al obtener datos desde ${endpoint}:`, error);
      }
    },
    [projectId]
  );

  // ===================== OBTENCIÓN DE DATOS ======================
  const fetchFetchedDetails = useCallback(async () => {
    const token = getToken();
    if (!token) return;
    try {
      const url = `${constantUrlApiEndpoint}/user/details/?project_id=${projectId}`;
      const headers = { Authorization: `Bearer ${token}` };
      const response = await axios.get(url, { headers });
      setFetchedDetails(response.data || []);
    } catch (error: unknown) {
      console.error("Error al obtener detalles:", error);
      Swal.fire("Error", "Error al obtener detalles. Ver consola.");
    }
  }, [projectId]);

  const fetchMurosDetails = useCallback(() => {
    if (!projectId) return;
    fetchData<TabItem[]>(
      `${constantUrlApiEndpoint}/project/${projectId}/details/Muro`,
      (data) => {
        setMurosTabList(data);
      }
    );
  }, [projectId, fetchData]);

  const fetchTechumbreDetails = useCallback(() => {
    fetchData<TabItem[]>(
      `${constantUrlApiEndpoint}/project/${projectId}/details/Techo`,
      setTechumbreTabList
    );
  }, [projectId, fetchData]);

  const fetchPisosDetails = useCallback(() => {
    fetchData<TabItem[]>(
      `${constantUrlApiEndpoint}/project/${projectId}/details/Piso`,
      setPisosTabList
    );
  }, [projectId, fetchData]);

  const fetchVentanasDetails = useCallback(() => {
    const token = getToken();
    if (!token) return;
    axios
      .get(`${constantUrlApiEndpoint}/user/elements/?type=window`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((response) => setVentanasTabList(response.data))
      .catch((error) => {
        console.error("Error al obtener datos de ventanas:", error);
        notify("Reinicie sesion, por favor.");
      });
  }, []);

  const fetchPuertasDetails = useCallback(() => {
    const token = getToken();
    if (!token) return;
    axios
      .get(`${constantUrlApiEndpoint}/user/elements/?type=door`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((response) => setPuertasTabList(response.data))
      .catch((error) => {
        console.error("Error al obtener datos de puertas:", error);
        notify("Reinicie sesion por favor.");
      });
  }, []);

  const fetchMaterials = async () => {
    const token = getToken();
    if (!token) return;
    try {
      const url = `${constantUrlApiEndpoint}/user/constants/?page=1&per_page=700`;
      const headers = { Authorization: `Bearer ${token}` };
      const response = await axios.get(url, { headers });
      const allConstants: Constant[] = response.data.constants || [];
      const materialsList: Material[] = allConstants
        .filter(
          (c: Constant) =>
            c.name === "materials" && c.type === "definition materials"
        )
        .map((c: Constant) => ({
          id: c.id,
          name: c.atributs.name,
        }));
      setMaterials(materialsList);
    } catch (error: unknown) {
      console.error("Error al obtener materiales:", error);
      notify("Reinicie sesion y vuelvalo a intentar.");
    }
  };

  // ===================== EFFECTS ======================
  useEffect(() => {
    if (step === 4 && projectId !== null) {
      fetchFetchedDetails();
    }
  }, [step, fetchFetchedDetails, projectId]);

  useEffect(() => {
    if (showTabsInStep4) {
      setTabStep4("muros");
    }
  }, [showTabsInStep4]);

  useEffect(() => {
    if (showTabsInStep4 && projectId !== null) {
      if (tabStep4 === "muros") fetchMurosDetails();
      else if (tabStep4 === "techumbre") fetchTechumbreDetails();
      else if (tabStep4 === "pisos") fetchPisosDetails();
      else if (tabStep4 === "ventanas") fetchVentanasDetails();
      else if (tabStep4 === "puertas") fetchPuertasDetails();
    }
  }, [
    showTabsInStep4,
    tabStep4,
    projectId,
    fetchMurosDetails,
    fetchTechumbreDetails,
    fetchPisosDetails,
    fetchVentanasDetails,
    fetchPuertasDetails,
  ]);

  // ===================== CREAR DETALLE INICIAL ======================
  const handleCreateNewDetail = async () => {
    if (!showNewDetailRow) return;
    if (
      !newDetailForm.scantilon_location ||
      !newDetailForm.name_detail ||
      !newDetailForm.material_id
    ) {
      notify("Por favor complete todos los campos de Detalle.");
      return;
    }
    const token = getToken();
    if (!token) return;
    try {
      const createUrl = `${constantUrlApiEndpoint}/user/details/create?project_id=${projectId}`;
      const headers = {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      };
      const response = await axios.post(createUrl, newDetailForm, { headers });
      const newDetailId = response.data.detail.id;
      if (!newDetailId) {
        notify("Reinicie sesion y vuelvalo a intentar.");
        return;
      }
      if (projectId) {
        const selectUrl = `${constantUrlApiEndpoint}/projects/${projectId}/details/select`;
        const detailIds = [newDetailId];
        try {
          await axios.post(selectUrl, detailIds, { headers });
          notify("Detalle creado y añadido al proyecto exitosamente.");
        } catch (selectError: unknown) {
          if (
            axios.isAxiosError(selectError) &&
            selectError.response?.data?.detail ===
            "Todos los detalles ya estaban en el proyecto"
          ) {
            notify("Detalle creado exitosamente.");
          } else {
            console.error("Error al añadir detalle al proyecto:", selectError);
            notify("Detalle creado pero no se añadio al proyecto.");
          }
        }
      } else {
        notify("No se añadio el detalle al proyecto.");
      }
      fetchFetchedDetails();
      if (newDetailForm.scantilon_location.toLowerCase() === "muro") {
        fetchMurosDetails();
      } else if (newDetailForm.scantilon_location.toLowerCase() === "techo") {
        fetchTechumbreDetails();
      } else if (newDetailForm.scantilon_location.toLowerCase() === "piso") {
        fetchPisosDetails();
      }
      setShowNewDetailRow(false);
      setNewDetailForm({
        scantilon_location: "",
        name_detail: "",
        material_id: 0,
        layer_thickness: null,
      });
    } catch (error: unknown) {
      if (axios.isAxiosError(error)) {
        console.error(
          "Error en la creación del detalle:",
          error.response?.data
        );
        notify("Reinicie sesion y vuelvalo a intentar.");
      }
    }
  };

  const handleConfirmEditDetail = async () => {
    if (!editingDetail) return;
    if (
      !editingDetail.scantilon_location.trim() ||
      !editingDetail.name_detail.trim()
    ) {
      notify(
        "Los campos 'Ubicación Detalle' y 'Nombre Detalle' no pueden estar vacíos."
      );
      return;
    }
    if (!editingDetail.material_id || editingDetail.material_id <= 0) {
      notify("Por favor, seleccione un material válido.");
      return;
    }
    if (
      editingDetail.layer_thickness === null ||
      editingDetail.layer_thickness <= 0
    ) {
      notify("El 'Espesor de la capa' debe ser un valor mayor a 0.");
      return;
    }
    const token = getToken();
    if (!token || !projectId) return;
    try {
      const url = `${constantUrlApiEndpoint}/user/detail-update/${editingDetail.id_detail || editingDetail?.id
        }`;
      const headers = {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      };
      const payload = {
        scantilon_location: editingDetail.scantilon_location,
        name_detail: editingDetail.name_detail,
        material_id: editingDetail.material_id,
        layer_thickness: editingDetail.layer_thickness,
      };
      await axios.patch(url, payload, { headers });
      notify("Detalle actualizado exitosamente");
      // Se refrescan todas las tablas involucradas
      fetchFetchedDetails();
      fetchMurosDetails();
      fetchTechumbreDetails();
      fetchPisosDetails();
      setEditingDetail(null);
      setShowDetallesModal(true);
    } catch (error: unknown) {
      console.error("Error al actualizar el detalle:", error);
      notify("Error al actualizar el Detalle.");
    }
  };

  // ---------------------------------------
  // ESTADO / FUNCIÓN para CREAR DETALLE con POST /user/detail-create/{detail_part_id}
  // (Reemplazo del botón + Nuevo en el Modal)
  // ---------------------------------------
  const [showCreateDetailModal, setShowCreateDetailModal] = useState(false);
  const [newDetailData, setNewDetailData] = useState({
    scantilon_location: "",
    name_detail: "",
    material_id: 0,
    layer_thickness: 0,
  });

  useEffect(() => {
    if (showCreateDetailModal) {
      fetchMaterials();
    }
  }, [showCreateDetailModal]);

  const handleCreateDetail = async () => {
    try {
      const token = getToken();
      if (!token) return;

      if (!selectedItem?.id) {
        notify("Falta el detail_part_id para crear el detalle.");
        return;
      }

      const url = `${constantUrlApiEndpoint}/user/detail-create/${selectedItem.id}`;
      const headers = {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      };

      const payload = {
        ...newDetailData,
      };

      await axios.post(url, payload, { headers });

      notify("Detalle creado con éxito");
      setShowCreateDetailModal(false);

      // Refresca la tabla en el modal
      fetchDetailModal(selectedItem.id);

      // Actualiza los detalles en la tabla principal según el tipo
      if (tabStep4 === "muros") {
        fetchMurosDetails();
      } else if (tabStep4 === "techumbre") {
        fetchTechumbreDetails();
      } else if (tabStep4 === "pisos") {
        fetchPisosDetails();
      }

      // Resetea formulario
      setNewDetailData({
        scantilon_location: "",
        name_detail: "",
        material_id: 0,
        layer_thickness: 0,
      });
    } catch (error) {
      console.error("Error al crear detalle", error);
      notify("Error al crear detalle");
    }
  };

  const handleConfirmInlineEdit = async (detail: IDetail) => {
    const uniqueId = detail.id_detail || Number(detail.id);
    if (editingDetailData.material_id <= 0) {
      notify("Por favor, seleccione un material válido.");
      return;
    }
    if (editingDetailData.layer_thickness <= 0) {
      notify("El 'Espesor de capa' debe ser un valor mayor a 0.");
      return;
    }
    try {
      const url = `/user/detail-update/${uniqueId}`;
      await api.patch(url, {
        scantilon_location: detail.scantilon_location,
        name_detail: detail.name_detail,
        material_id: editingDetailData.material_id,
        layer_thickness: editingDetailData.layer_thickness,
      });
      notify("Detalle actualizado exitosamente");
      // Se refrescan todos los detalles
      fetchDetailModal(selectedItem?.id);
      fetchMurosDetails();
      fetchTechumbreDetails();
      fetchPisosDetails();
    } catch (error) {
      console.error("Error al actualizar el detalle:", error);
      notify("Error al actualizar el detalle.");
    }
    setEditingDetailId(null);
  };

  const [editingDetailData, setEditingDetailData] = useState<{
    material_id: number;
    layer_thickness: number;
  }>({
    material_id: 0,
    layer_thickness: 0,
  });
  const [editingDetailId, setEditingDetailId] = useState<number | null>(null);

  // ===================== NUEVA FUNCIÓN: abrir modal de confirmación de borrado para Muro/Techo/Piso =====================
  const handleDeleteConfirm = (e: React.MouseEvent, detailId?: number) => {
    e.stopPropagation();
    if (detailId) setSelectedDeleteDetailId(detailId);
    console.log("ID del detalle a eliminar:", detailId);
    setShowDeleteLayerModal(true);
  };

  // ===================== NUEVA FUNCIÓN: invocar DELETE /detail-general/{detail_id}/true y refrescar =====================
  const handleDeleteLayer = async () => {
    if (!selectedDeleteDetailId) return;
    const token = getToken();
    if (!token) return;

    try {
      const url = `${constantUrlApiEndpoint}/detail-general/${selectedDeleteDetailId}/true`;
      console.log("Intentando eliminar detail_id:", selectedDeleteDetailId);

      const headers = { Authorization: `Bearer ${token}` };
      await axios.delete(url, { headers });

      notify("Detalle eliminado con éxito");

      // Actualizamos la tabla según la pestaña activa:
      if (tabStep4 === "muros") {
        fetchMurosDetails();
      } else if (tabStep4 === "techumbre") {
        fetchTechumbreDetails();
      } else if (tabStep4 === "pisos") {
        fetchPisosDetails();
      }
    } catch (error) {
      console.error("Error al eliminar el detalle:", error);
      notify("Ocurrió un error al eliminar el detalle");
    } finally {
      setShowDeleteLayerModal(false);
      setSelectedDeleteDetailId(null);
    }
  };

  const confirmDelete = async () => {
    // Esta es la función que ya tenías para eliminar otras cosas (ventanas, puertas, etc.)
    // NO la borramos; la dejamos tal cual para no quitar funciones.
    // ...
  };

  // ===================== RENDER DEL MODAL PARA DETALLES GENERALES ======================
  const renderDetallesModalContent = () => {
    const columnsDetails = [
      { headerName: "Nombre Detalle", field: "name_detail" },
      { headerName: "Material", field: "material" },
      { headerName: "Espesor capa (cm)", field: "layer_thickness" },
      { headerName: "Acción", field: "accion" },
    ];

    const handleInlineEdit = (detail: IDetail) => {
      const uniqueId = detail.id_detail || detail.id;
      setEditingDetailId(uniqueId);
      setEditingDetailData({
        material_id: detail.material_id,
        layer_thickness: detail.layer_thickness,
      });
    };

    const handleCancelInlineEdit = () => {
      setEditingDetailId(null);
    };

    const data = detailList?.map((det: any) => {
      const uniqueId = det.id_detail || det.id;
      const textStyle =
        det.created_status === "created"
          ? { color: "var(--primary-color)", fontWeight: "bold" }
          : {};
      const isEditing = editingDetailId === uniqueId;
      return {
        scantilon_location: (
          <span style={textStyle}>{det.scantilon_location}</span>
        ),
        name_detail: <span style={textStyle}>{det.name_detail}</span>,
        material: isEditing ? (
          <select
            className="form-control"
            value={editingDetailData.material_id}
            onChange={(e) =>
              setEditingDetailData((prev) => ({
                ...prev,
                material_id: Number(e.target.value),
              }))
            }
            onClick={fetchMaterials}
          >
            <option value={0}>Seleccione un material</option>
            {materials.map((mat) => (
              <option key={mat.id} value={mat.id}>
                {mat.name}
              </option>
            ))}
          </select>
        ) : (
          <span style={textStyle}>
            {det.material &&
              det.material !== "0" &&
              det.material.toUpperCase() !== "N/A"
              ? det.material
              : "-"}
          </span>
        ),
        layer_thickness: isEditing ? (
          <input
            type="number"
            className="form-control"
            min="0"
            step="any"
            value={editingDetailData.layer_thickness}
            onKeyDown={(e) => {
              if (e.key === "-") e.preventDefault();
            }}
            onChange={(e) =>
              setEditingDetailData((prev) => ({
                ...prev,
                layer_thickness: Number(e.target.value),
              }))
            }
          />
        ) : (
          <span style={textStyle}>
            {det.layer_thickness && det.layer_thickness > 0
              ? det.layer_thickness
              : "-"}
          </span>
        ),
        accion: isEditing ? (
          <ActionButtonsConfirm
            onAccept={() => handleConfirmInlineEdit(det)}
            onCancel={handleCancelInlineEdit}
          />
        ) : det.created_status === "default" ||
          det.created_status === "global" ? (
          <span>-</span>
        ) : (
          <>
            <CustomButton
              className="btn-table"
              variant="editIcon"
              onClick={() => handleInlineEdit(det)}
              disabled={
                det.created_status === "default" ||
                det.created_status === "global"
              }
            >
              Editar
            </CustomButton>
            {/* Botón eliminar con tu DeleteDetailButton (no se elimina) */}
            <DeleteDetailButton
              disabled={
                det.created_status === "default" ||
                det.created_status === "global"
              }
              detailId={det.id}
              onDelete={() => {
                fetchMurosDetails();
                fetchPisosDetails();
                fetchTechumbreDetails();
                fetchFetchedDetails();
                fetchDetailModal(selectedItem?.id);
              }}
            />
          </>
        ),
      };
    });

    return (
      <>
        <div
          style={{
            display: "flex",
            justifyContent: "flex-end",
            marginBottom: "1rem",
          }}
        >
          {/* Solo mostrar el botón si NO es un detalle por defecto o global */}
          {selectedItem &&
            selectedItem.created_status !== "default" &&
            selectedItem.created_status !== "global" && (
              <CustomButton
                variant="save"
                onClick={() => {
                  const locationValue =
                    tabStep4 === "muros"
                      ? "Muro"
                      : tabStep4 === "techumbre"
                        ? "Techo"
                        : tabStep4 === "pisos"
                          ? "Piso"
                          : "";

                  setNewDetailData({
                    scantilon_location: locationValue,
                    name_detail: selectedItem?.name_detail || "",
                    material_id: 0,
                    layer_thickness: 0,
                  });
                  setShowCreateDetailModal(true);
                }}
              >
                + Nuevo
              </CustomButton>
            )}
        </div>
        <TablesParameters columns={columnsDetails} data={data} />
      </>
    );
  };

  // Helper function for search filtering
  const matchSearch = (value: string | number | null | undefined) => {
    // convierte cualquier cosa a texto, sin romper tipos
    const normalized = String(value ?? "")
      .toLowerCase()
      // opcional: elimina tildes si lo necesitas
      // .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
      .trim();

    return normalized.includes(searchQuery.trim().toLowerCase());
  };

  // ===================== RENDER INICIAL DETALLES (sin pestañas) ======================
  const renderInitialDetails = () => {
    if (showTabsInStep4) return null;
    const filteredData = fetchedDetails.filter((det) => {
      const searchLower = searchQuery.toLowerCase();
      return (
        det.scantilon_location.toLowerCase().includes(searchLower) ||
        det.name_detail.toLowerCase().includes(searchLower) ||
        det.material.toLowerCase().includes(searchLower) ||
        det.layer_thickness.toString().includes(searchLower)
      );
    });
    const columns = [
      { headerName: "Nombre Detalle", field: "name_detail" },
      { headerName: "Material", field: "material" },
      { headerName: "Espesor capa (cm)", field: "layer_thickness" },
    ];
    const data = filteredData.map((det) => {
      const textStyle =
        det.created_status === "created"
          ? { color: "var(--primary-color)", fontWeight: "bold" }
          : {};
      return {
        scantilon_location: (
          <span style={textStyle}>{det.scantilon_location}</span>
        ),
        name_detail: <span style={textStyle}>{det.name_detail}</span>,
        material: <span style={textStyle}>{det.material}</span>,
        layer_thickness: <span style={textStyle}>{det.layer_thickness}</span>,
      };
    });
    return (
      <div style={{ maxHeight: "400px", overflowY: "auto" }}>
        <TablesParameters columns={columns} data={data} />
      </div>
    );
  };

  // ===================== RENDER MUROS ======================
  // const { handleSort: onMurosSort } = SortHandler({
  //   data: murosTabList,
  //   onSort: (sortedData) => setMurosTabList(sortedData),
  // });
  const renderMurosParameters = () => {
    const columnsMuros = [
      {
        headerName: "Nombre Abreviado",
        field: "nombreAbreviado",
        // headerClick: () => onMurosSort("name_detail"),
      },
      {
        headerName: "Valor U (W/m²K)",
        field: "valorU",
        // headerClick: () => onMurosSort("value_u"),
      },
      {
        headerName: "Color Exterior",
        field: "colorExterior",
        // headerClick: () => onMurosSort("info.surface_color.exterior.name"),
      },
      {
        headerName: "Color Interior",
        field: "colorInterior",
        // headerClick: () => onMurosSort("info.surface_color.interior.name"),
      },
      { headerName: "Acciones", field: "acciones", sortable: false },
    ];

    const murosData = murosTabList
      .filter(
        (item) =>
          matchSearch(item.name_detail) ||
          matchSearch(item.info?.surface_color?.exterior?.name ?? "") ||
          matchSearch(item.info?.surface_color?.interior?.name ?? "")
      )
      .map((item) => {
        const isEditing = editingRowId === item.id;
        return {
          __detail: item,
          code_ifc: item.code_ifc || "-",
          nombreAbreviado: isEditing ? (
            "created_status" in item &&
              (item.created_status === "default" ||
                item.created_status === "global") ? (
              <input
                type="text"
                className="form-control"
                value={editingColors.nombreAbreviado}
                readOnly
                disabled
              />
            ) : (
              <input
                type="text"
                className="form-control"
                value={editingColors.nombreAbreviado}
                onClick={(e) => e.stopPropagation()}
                onChange={(e) =>
                  setEditingColors((prev) => ({
                    ...prev,
                    nombreAbreviado: e.target.value,
                  }))
                }
              />
            )
          ) : (
            <span
              style={
                "created_status" in item && item.created_status === "created"
                  ? { color: "var(--primary-color)", fontWeight: "bold" }
                  : {}
              }
            >
              {item.name_detail}
            </span>
          ),
          valorU: formatValue(item.value_u),
          colorExterior: isEditing ? (
            <select
              value={editingColors.exterior}
              onClick={(e) => e.stopPropagation()}
              onChange={(e) =>
                setEditingColors((prev) => ({
                  ...prev,
                  exterior: e.target.value,
                }))
              }
            >
              <option value="Claro">Claro</option>
              <option value="Oscuro">Oscuro</option>
              <option value="Intermedio">Intermedio</option>
            </select>
          ) : (
            item.info?.surface_color?.exterior?.name || "Desconocido"
          ),
          colorInterior: isEditing ? (
            <select
              value={editingColors.interior}
              onClick={(e) => e.stopPropagation()}
              onChange={(e) =>
                setEditingColors((prev) => ({
                  ...prev,
                  interior: e.target.value,
                }))
              }
            >
              <option value="Claro">Claro</option>
              <option value="Oscuro">Oscuro</option>
              <option value="Intermedio">Intermedio</option>
            </select>
          ) : (
            item.info?.surface_color?.interior?.name || "Desconocido"
          ),
          acciones: isEditing ? (
            <div onClick={(e) => e.stopPropagation()}>
              <ActionButtonsConfirm
                onAccept={async () => {
                  if (!item.id || !projectId) return;
                  const token = getToken();
                  if (!token) return;
                  try {
                    const url = `${constantUrlApiEndpoint}/project/${projectId}/update_details/Muro/${item.id}`;
                    const headers = { Authorization: `Bearer ${token}` };
                    const payload = {
                      ...item,
                      name_detail: editingColors.nombreAbreviado,
                      info: {
                        ...item.info,
                        surface_color: {
                          exterior: { name: editingColors.exterior },
                          interior: { name: editingColors.interior },
                        },
                      },
                    };
                    await axios.put(url, payload, { headers });
                    notify("Muro actualizado exitosamente");
                    fetchMurosDetails();
                    setEditingRowId(null);
                  } catch (error) {
                    console.error("Error updating muro:", error);
                    notify("Ya existe un detalle con el nombre asignado.");
                  }
                }}
                onCancel={() => {
                  setEditingRowId(null);
                  setEditingColors({
                    interior: "Intermedio",
                    exterior: "Intermedio",
                    nombreAbreviado: "",
                  });
                }}
              />
            </div>
          ) : (
            <div>
              <AddDetailOnLayer item={item} OnDetailOpened={OnDetailOpened} />
              <CustomButton
                disabled={
                  ("created_status" in item &&
                    item.created_status === "default") ||
                  ("created_status" in item && item.created_status === "global")
                }
                className="btn-table"
                variant="editIcon"
                onClick={(e) => {
                  e.stopPropagation();
                  setEditingRowId(item.id || null);
                  setEditingColors({
                    interior:
                      item.info?.surface_color?.interior?.name || "Intermedio",
                    exterior:
                      item.info?.surface_color?.exterior?.name || "Intermedio",
                    nombreAbreviado: item.name_detail || "",
                  });
                  console.log("ID del muro a editar:", item.id);
                }}
              >
                Editar
              </CustomButton>

              {/* NUEVO botón de eliminar MURO con modal de confirmación */}
              <CustomButton
                disabled={
                  ("created_status" in item &&
                    item.created_status === "default") ||
                  ("created_status" in item && item.created_status === "global")
                }
                variant="deleteIcon"
                onClick={(e: React.MouseEvent) =>
                  handleDeleteConfirm(e, item?.id)
                }
              >
                <span className="material-icons">delete</span>
              </CustomButton>
            </div>
          ),
        };
      });
    return (
      <div>
        {murosTabList.length > 0 ? (
          <TablesParameters columns={columnsMuros} data={murosData} />
        ) : (
          <p>No hay datos</p>
        )}
      </div>
    );
  };

  // ===================== RENDER TECHUMBRES ======================
  const renderTechumbreParameters = () => {
    const columnsTech = [
      {
        headerName: "Código IFC",
        field: "code_ifc",
      },
      { headerName: "Nombre Abreviado", field: "nombreAbreviado" },
      { headerName: "Valor U (W/m²K)", field: "valorU" },
      { headerName: "Color Exterior", field: "colorExterior" },
      { headerName: "Color Interior", field: "colorInterior" },
      { headerName: "Acciones", field: "acciones", sortable: false },
    ];
    const techData = techumbreTabList
      .filter(
        (item) =>
          matchSearch(item.name_detail) ||
          matchSearch(item.info?.surface_color?.exterior?.name ?? "") ||
          matchSearch(item.info?.surface_color?.interior?.name ?? "")
      )
      .map((item) => {
        const isEditing = editingTechRowId === item.id;
        return {
          __detail: item,
          code_ifc: item.code_ifc || "-",
          nombreAbreviado: isEditing ? (
            "created_status" in item &&
              (item.created_status === "default" ||
                item.created_status === "global") ? (
              <input
                type="text"
                className="form-control"
                value={editingTechColors.nombreAbreviado}
                readOnly
                disabled
              />
            ) : (
              <input
                type="text"
                className="form-control"
                value={editingTechColors.nombreAbreviado}
                onClick={(e) => e.stopPropagation()}
                onChange={(e) =>
                  setEditingTechColors((prev) => ({
                    ...prev,
                    nombreAbreviado: e.target.value,
                  }))
                }
              />
            )
          ) : (
            <span
              style={
                "created_status" in item && item.created_status === "created"
                  ? { color: "var(--primary-color)", fontWeight: "bold" }
                  : {}
              }
            >
              {item.name_detail}
            </span>
          ),
          valorU: formatValue(item.value_u),
          colorExterior: isEditing ? (
            <select
              value={editingTechColors.exterior}
              onClick={(e) => e.stopPropagation()}
              onChange={(e) =>
                setEditingTechColors((prev) => ({
                  ...prev,
                  exterior: e.target.value,
                }))
              }
            >
              <option value="Claro">Claro</option>
              <option value="Oscuro">Oscuro</option>
              <option value="Intermedio">Intermedio</option>
            </select>
          ) : (
            item.info?.surface_color?.exterior?.name || "Desconocido"
          ),
          colorInterior: isEditing ? (
            <select
              value={editingTechColors.interior}
              onClick={(e) => e.stopPropagation()}
              onChange={(e) =>
                setEditingTechColors((prev) => ({
                  ...prev,
                  interior: e.target.value,
                }))
              }
            >
              <option value="Claro">Claro</option>
              <option value="Oscuro">Oscuro</option>
              <option value="Intermedio">Intermedio</option>
            </select>
          ) : (
            item.info?.surface_color?.interior?.name || "Desconocido"
          ),
          acciones: isEditing ? (
            <div onClick={(e) => e.stopPropagation()}>
              <ActionButtonsConfirm
                onAccept={async () => {
                  if (!item.id || !projectId) return;
                  const token = getToken();
                  if (!token) return;
                  try {
                    const url = `${constantUrlApiEndpoint}/project/${projectId}/update_details/Techo/${item.id}`;
                    const headers = { Authorization: `Bearer ${token}` };
                    const payload = {
                      ...item,
                      name_detail: editingTechColors.nombreAbreviado,
                      info: {
                        ...item.info,
                        surface_color: {
                          exterior: { name: editingTechColors.exterior },
                          interior: { name: editingTechColors.interior },
                        },
                      },
                    };
                    await axios.put(url, payload, { headers });
                    notify("Techumbre actualizada exitosamente");
                    fetchTechumbreDetails();
                    setEditingTechRowId(null);
                  } catch (error) {
                    console.error("Error updating techumbre:", error);
                    notify("Ya existe un detalle con el nombre asignado.");
                  }
                }}
                onCancel={() => {
                  setEditingTechRowId(null);
                  setEditingTechColors({
                    interior: "Intermedio",
                    exterior: "Intermedio",
                    nombreAbreviado: "",
                  });
                }}
              />
            </div>
          ) : (
            <div>
              <AddDetailOnLayer item={item} OnDetailOpened={OnDetailOpened} />
              <CustomButton
                disabled={
                  ("created_status" in item &&
                    item.created_status === "default") ||
                  ("created_status" in item && item.created_status === "global")
                }
                variant="editIcon"
                className="btn-table"
                onClick={(e) => {
                  e.stopPropagation();
                  setEditingTechRowId(item.id || null);
                  setEditingTechColors({
                    interior:
                      item.info?.surface_color?.interior?.name || "Intermedio",
                    exterior:
                      item.info?.surface_color?.exterior?.name || "Intermedio",
                    nombreAbreviado: item.name_detail || "",
                  });
                }}
              >
                Editar
              </CustomButton>

              {/* NUEVO botón de eliminar TECHO con modal de confirmación */}
              <CustomButton
                disabled={
                  ("created_status" in item &&
                    item.created_status === "default") ||
                  ("created_status" in item && item.created_status === "global")
                }
                variant="deleteIcon"
                onClick={(e: React.MouseEvent) =>
                  handleDeleteConfirm(e, item.id!)
                }
              >
                <span className="material-icons">delete</span>
              </CustomButton>
            </div>
          ),
        };
      });
    return (
      <div>
        {techumbreTabList.length > 0 ? (
          <TablesParameters columns={columnsTech} data={techData} />
        ) : (
          <p>No hay datos</p>
        )}
      </div>
    );
  };

  // ===================== RENDER PISOS ======================
  const renderPisosParameters = () => {
    const columnsPisos = [
      {
        headerName: "Código IFC",
        field: "code_ifc",
      },
      { headerName: "Nombre", field: "nombre" },
      { headerName: "U [W/m²K]", field: "uValue" },
      { headerName: "I [W/mK] (bajo piso)", field: "bajoPisoLambda" },
      { headerName: "e Aisl [cm] (bajo piso)", field: "bajoPisoEAisl" },
      { headerName: "I [W/mK] (vert)", field: "vertLambda" },
      { headerName: "e Aisl [cm] (vert)", field: "vertEAisl" },
      { headerName: "D [cm] (vert)", field: "vertD" },
      { headerName: "I [W/mK] (horiz)", field: "horizLambda" },
      { headerName: "e Aisl [cm] (horiz)", field: "horizEAisl" },
      { headerName: "D [cm] (horiz)", field: "horizD" },
      { headerName: "Acciones", field: "acciones", rowSpan: 2, colSpan: 3 },
    ];
    console.log("pisos");
    console.log(pisosTabList);
    const multiHeaderPisos: MultiHeader = {
      rows: [
        // Fila 1
        [
          { label: "Código IFC", field: "code_ifc", rowSpan: 2, sortable: true },
          { label: "Nombre", field: "nombre", rowSpan: 2, sortable: true },
          { label: "U [W/m²K]", field: "uValue", rowSpan: 2, sortable: true },
          { label: "Aislamiento bajo piso", colSpan: 2 },
          { label: "Ref Aisl Vert.", colSpan: 3 },
          { label: "Ref Aisl Horiz.", colSpan: 3 },
          { label: "Acciones", field: "acciones", rowSpan: 2, sortable: false },
        ],
        // Fila 2 (subcolumnas)
        [
          { label: "λ [W/mK]", field: "bajoPisoLambda", sortable: true },
          { label: "e Aisl [cm]", field: "bajoPisoEAisl", sortable: true },
          { label: "λ [W/mK]", field: "vertLambda", sortable: true },
          { label: "e Aisl [cm]", field: "vertEAisl", sortable: true },
          { label: "D [cm]", field: "vertD", sortable: true },
          { label: "λ [W/mK]", field: "horizLambda", sortable: true },
          { label: "e Aisl [cm]", field: "horizEAisl", sortable: true },
          { label: "D [cm]", field: "horizD", sortable: true },
        ],
      ],
    };

    const pisosData = pisosTabList
      .filter(
        (item) =>
          matchSearch(item.name_detail) ||
          matchSearch(item.info?.aislacion_bajo_piso?.lambda ?? "") ||
          matchSearch(item.info?.ref_aisl_vertical?.lambda ?? "") ||
          matchSearch(item.info?.ref_aisl_horizontal?.lambda ?? "")
      )
      .map((item) => {
        const isEditing = editingPisosRowId === item.id;
        const vertical = isEditing
          ? editingPisosData.ref_aisl_vertical
          : item.info?.ref_aisl_vertical || {};
        const horizontal = isEditing
          ? editingPisosData.ref_aisl_horizontal
          : item.info?.ref_aisl_horizontal || {};
        return {
          __detail: item,
          id: item.id,
          code_ifc: item.code_ifc || "-",

          nombre: isEditing ? (
            "created_status" in item &&
              (item.created_status === "default" ||
                item.created_status === "global") ? (
              <input
                type="text"
                className="form-control"
                value={editingPisosData.nombre}
                readOnly
                disabled
              />
            ) : (
              <input
                type="text"
                className="form-control"
                value={editingPisosData.nombre}
                onClick={(e) => e.stopPropagation()}
                onChange={(e) =>
                  setEditingPisosData((prev) => ({
                    ...prev,
                    nombre: e.target.value,
                  }))
                }
              />
            )
          ) : (
            <span
              style={
                "created_status" in item && item.created_status === "created"
                  ? { color: "var(--primary-color)", fontWeight: "bold" }
                  : {}
              }
            >
              {item.name_detail}
            </span>
          ),
          uValue: formatValue(item.value_u),
          bajoPisoLambda: formatValue(item.info?.aislacion_bajo_piso?.lambda),
          bajoPisoEAisl: formatValue(item.info?.aislacion_bajo_piso?.e_aisl),
          vertLambda: isEditing ? (
            <input
              type="number"
              min="0"
              className="form-control form-control-sm"
              value={vertical.lambda}
              onClick={(e) => e.stopPropagation()}
              onKeyDown={(e) => {
                if (e.key === "-") {
                  e.preventDefault();
                }
              }}
              onChange={(e) => {
                const newValue = e.target.value;
                if (newValue.includes("-")) {
                  return;
                }
                setEditingPisosData((prev) => ({
                  ...prev,
                  ref_aisl_vertical: {
                    ...prev.ref_aisl_vertical,
                    lambda: newValue,
                  },
                }));
              }}
            />
          ) : (
            <>{formatValue(Number(vertical.lambda))}</>
          ),
          vertEAisl: isEditing ? (
            <input
              type="number"
              min="0"
              className="form-control form-control-sm"
              value={vertical.e_aisl}
              onClick={(e) => e.stopPropagation()}
              onKeyDown={(e) => {
                if (e.key === "-") {
                  e.preventDefault();
                }
              }}
              onChange={(e) => {
                const newValue = e.target.value;
                if (newValue.includes("-")) {
                  return;
                }
                setEditingPisosData((prev) => ({
                  ...prev,
                  ref_aisl_vertical: {
                    ...prev.ref_aisl_vertical,
                    e_aisl: newValue,
                  },
                }));
              }}
            />
          ) : (
            <>{formatValue(Number(vertical.e_aisl))}</>
          ),
          vertD: isEditing ? (
            <input
              type="number"
              min="0"
              className="form-control form-control-sm"
              value={vertical.d}
              onClick={(e) => e.stopPropagation()}
              onKeyDown={(e) => {
                if (e.key === "-") {
                  e.preventDefault();
                }
              }}
              onChange={(e) => {
                const newValue = e.target.value;
                if (newValue.includes("-")) {
                  return;
                }
                setEditingPisosData((prev) => ({
                  ...prev,
                  ref_aisl_vertical: { ...prev.ref_aisl_vertical, d: newValue },
                }));
              }}
            />
          ) : (
            <>{formatValue(Number(vertical.d))}</>
          ),
          horizLambda: isEditing ? (
            <input
              type="number"
              min="0"
              className="form-control form-control-sm"
              value={horizontal.lambda}
              onClick={(e) => e.stopPropagation()}
              onKeyDown={(e) => {
                if (e.key === "-") {
                  e.preventDefault();
                }
              }}
              onChange={(e) => {
                const newValue = e.target.value;
                if (newValue.includes("-")) {
                  return;
                }
                setEditingPisosData((prev) => ({
                  ...prev,
                  ref_aisl_horizontal: {
                    ...prev.ref_aisl_horizontal,
                    lambda: newValue,
                  },
                }));
              }}
            />
          ) : (
            <>{formatValue(Number(horizontal.lambda))}</>
          ),
          horizEAisl: isEditing ? (
            <input
              type="number"
              min="0"
              className="form-control form-control-sm"
              value={horizontal.e_aisl}
              onClick={(e) => e.stopPropagation()}
              onKeyDown={(e) => {
                if (e.key === "-") {
                  e.preventDefault();
                }
              }}
              onChange={(e) => {
                const newValue = e.target.value;
                if (newValue.includes("-")) {
                  return;
                }
                setEditingPisosData((prev) => ({
                  ...prev,
                  ref_aisl_horizontal: {
                    ...prev.ref_aisl_horizontal,
                    e_aisl: newValue,
                  },
                }));
              }}
            />
          ) : (
            <>{formatValue(Number(horizontal.e_aisl))}</>
          ),
          horizD: isEditing ? (
            <input
              type="number"
              min="0"
              className="form-control form-control-sm"
              value={horizontal.d}
              onClick={(e) => e.stopPropagation()}
              onKeyDown={(e) => {
                if (e.key === "-") {
                  e.preventDefault();
                }
              }}
              onChange={(e) => {
                const newValue = e.target.value;
                if (newValue.includes("-")) {
                  return;
                }
                setEditingPisosData((prev) => ({
                  ...prev,
                  ref_aisl_horizontal: {
                    ...prev.ref_aisl_horizontal,
                    d: newValue,
                  },
                }));
              }}
            />
          ) : (
            <>{formatValue(Number(horizontal.d))}</>
          ),
          acciones: isEditing ? (
            <div
              style={{ width: "160px" }}
              onClick={(e) => e.stopPropagation()}
            >
              <ActionButtonsConfirm
                onAccept={async () => {
                  if (!item.id || !projectId) return;
                  const token = getToken();
                  if (!token) return;
                  try {
                    const url = `${constantUrlApiEndpoint}/project/${projectId}/update_details/Piso/${item.id}`;
                    const headers = { Authorization: `Bearer ${token}` };
                    const payload = {
                      ...item,
                      name_detail: editingPisosData.nombre,
                      info: {
                        ...item.info,
                        ref_aisl_vertical: {
                          lambda: parseFloat(
                            editingPisosData.ref_aisl_vertical.lambda
                          ),
                          e_aisl: parseFloat(
                            editingPisosData.ref_aisl_vertical.e_aisl
                          ),
                          d: parseFloat(editingPisosData.ref_aisl_vertical.d),
                        },
                        ref_aisl_horizontal: {
                          lambda: parseFloat(
                            editingPisosData.ref_aisl_horizontal.lambda
                          ),
                          e_aisl: parseFloat(
                            editingPisosData.ref_aisl_horizontal.e_aisl
                          ),
                          d: parseFloat(editingPisosData.ref_aisl_horizontal.d),
                        },
                      },
                    };
                    await axios.put(url, payload, { headers });
                    notify("Piso actualizado exitosamente");
                    fetchPisosDetails();
                    setEditingPisosRowId(null);
                  } catch (error) {
                    console.error("Error updating piso:", error);
                    notify("Ya existe un detalle con el nombre asignado.");
                  }
                }}
                onCancel={() => {
                  setEditingPisosRowId(null);
                  setEditingPisosData({
                    ref_aisl_vertical: { lambda: "", e_aisl: "", d: "" },
                    ref_aisl_horizontal: { lambda: "", e_aisl: "", d: "" },
                    nombre: "",
                  });
                }}
              />
            </div>
          ) : (
            <div style={{ width: "160px" }}>
              <AddDetailOnLayer item={item} OnDetailOpened={OnDetailOpened} />
              <CustomButton
                disabled={
                  ("created_status" in item &&
                    item.created_status === "default") ||
                  ("created_status" in item && item.created_status === "global")
                }
                className="btn-table"
                variant="editIcon"
                onClick={(e) => {
                  e.stopPropagation();
                  setEditingPisosRowId(item.id || null);
                  setEditingPisosData({
                    ref_aisl_vertical: {
                      lambda:
                        item.info?.ref_aisl_vertical?.lambda?.toString() || "",
                      e_aisl:
                        item.info?.ref_aisl_vertical?.e_aisl?.toString() || "",
                      d: item.info?.ref_aisl_vertical?.d?.toString() || "",
                    },
                    ref_aisl_horizontal: {
                      lambda:
                        item.info?.ref_aisl_horizontal?.lambda?.toString() ||
                        "",
                      e_aisl:
                        item.info?.ref_aisl_horizontal?.e_aisl?.toString() ||
                        "",
                      d: item.info?.ref_aisl_horizontal?.d?.toString() || "",
                    },
                    nombre: item.name_detail || "",
                  });
                }}
              >
                Editar
              </CustomButton>

              {/* NUEVO botón de eliminar PISO con modal de confirmación */}
              <CustomButton
                disabled={
                  ("created_status" in item &&
                    item.created_status === "default") ||
                  ("created_status" in item && item.created_status === "global")
                }
                variant="deleteIcon"
                onClick={(e: React.MouseEvent) =>
                  handleDeleteConfirm(e, item.id!)
                }
              >
                <span className="material-icons">delete</span>
              </CustomButton>
            </div>
          ),
        };
      });
    return (
      <div>
        {pisosTabList.length > 0 ? (
          <TablesParameters
            columns={columnsPisos}
            data={pisosData}
            multiHeader={multiHeaderPisos}
          />
        ) : (
          <p>No hay datos</p>
        )}
      </div>
    );
  };


  // ===================== RENDER PESTAÑAS STEP4 ======================
  const renderStep4Tabs = () => {
    if (!showTabsInStep4) return null;

    const tabs = [
      { key: "muros", label: "Muros" },
      { key: "techumbre", label: "Techumbre" },
      { key: "pisos", label: "Pisos" },
      // { key: "ventanas", label: "Ventanas" },
      // { key: "puertas",  label: "Puertas"  },
    ] as { key: TabStep4; label: string }[];

    return (
      <div className="mt-4">
        {/* ──────────────────────────────────────────────────────────────
          Cabecera:  buscador  +  botón “Nuevo” (solo muros/techo/piso)
         ───────────────────────────────────────────────────────────── */}
        {(tabStep4 === "muros" ||
          tabStep4 === "techumbre" ||
          tabStep4 === "pisos") && (
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: "12px",
                marginBottom: "1rem",
                flexWrap: "wrap",
              }}
            >
              {/* Buscador */}
              <SearchParameters
                value={searchQuery}
                onChange={setSearchQuery}
                placeholder={`Buscar ${tabStep4}`}
                showNewButton={false} /* ← no queremos que duplique el +Nuevo */
                style={{ flex: 1, minWidth: "180px" }}
                onNew={() => { }} /* prop obligatoria pero sin uso aquí */
              />

              {/* Botón + Nuevo */}
              <NewHeaderButton
                tab={tabStep4 as "muros" | "techumbre" | "pisos"}
                onNewCreated={
                  tabStep4 === "muros"
                    ? fetchMurosDetails
                    : tabStep4 === "techumbre"
                      ? fetchTechumbreDetails
                      : fetchPisosDetails
                }
              />            </div>
          )}

        {/* Pestañas */}
        <HorizontalTabs
          tabs={tabs}
          currentTab={tabStep4}
          onTabChange={(tab) => setTabStep4(tab as TabStep4)}
        />
        {/* Contenido de cada tab */}
        <div
          style={{ height: "400px", position: "relative", marginTop: "1rem" }}
        >
          {tabStep4 === "muros" && renderMurosParameters()}
          {tabStep4 === "techumbre" && renderTechumbreParameters()}
          {tabStep4 === "pisos" && renderPisosParameters()}
        </div>
      </div>
    );
  };

  // ===================== RENDER RECINTO ======================
  const renderRecinto = () => {
    return (
      <div className="recinto-container">
        <div className="d-flex justify-content-between align-items-center mb-3 flex-wrap">
          <div></div>
        </div>
        <div className="table-responsive-wrapper">
          <TabRecintDataCreate />
        </div>

        <style jsx>{`
          .recinto-container {
            width: 100%;
            overflow-x: auto;
          }
          
          .table-responsive-wrapper {
            min-width: 100%;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            margin-bottom: 1rem;
            box-shadow: inset -5px 0 5px -5px rgba(0,0,0,0.1);
          }

          .table-responsive-wrapper::-webkit-scrollbar {
            height: 8px;
          }

          .table-responsive-wrapper::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 4px;
          }

          .table-responsive-wrapper::-webkit-scrollbar-thumb {
            background: var(--primary-color);
            border-radius: 4px;
          }

          @media (max-width: 768px) {
            .recinto-container {
              margin: 0 -15px;
              padding: 0 15px;
            }
          }
        `}</style>
      </div>
    );
  };

  // ===================== SIDEBAR & STEP CHANGE ======================
  const handleSidebarStepChange = (newStep: number) => {
    if (newStep === 1) {
      router.push(`/workflow-part1-edit?id=${projectId}&step=1`);
    } else if (newStep === 2) {
      router.push(`/workflow-part1-edit?id=${projectId}&step=2`);
    } else {
      setStep(newStep);
    }
  };



  // ===================== FUNCIONES PARA VENTANAS Y PUERTAS ======================
  const [deleteItem, setDeleteItem] = useState<{
    id: number;
    type: "window" | "door" | "detail";
  } | null>(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const handleConfirmVentanaEdit = async () => {
    if (!editingVentana || !projectId) return;
    const token = getToken();
    if (!token) return;
    const url = `${constantUrlApiEndpoint}/user/elements/${editingVentana.id}/update`;
    const headers = {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    };
    const payload = {
      name_element: editingVentana.name_element,
      type: "window",
      atributs: editingVentana.atributs,
      u_marco: editingVentana.u_marco,
      fm: editingVentana.fm,
    };
    try {
      await axios.put(url, payload, { headers });
      notify("Ventana actualizada con éxito.");
      fetchVentanasDetails();
      setEditingVentana(null);
    } catch (error: any) {
      console.error("Error al actualizar ventana:", error);
      if (
        error?.response?.data?.detail ===
        "El nombre del elemento ya existe dentro del tipo window"
      ) {
        notify("El Nombre de la Ventana ya existe");
      } else {
        notify("Error al actualizar la ventana");
      }
    }
  };

  const handleConfirmPuertaEdit = async () => {
    if (!editingPuerta || !projectId) return;
    const token = getToken();
    if (!token) return;
    const url = `${constantUrlApiEndpoint}/user/elements/${editingPuerta.id}/update`;
    const headers = {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    };
    const payload = {
      name_element: editingPuerta.name_element,
      type: "door",
      atributs: editingPuerta.atributs,
      u_marco: editingPuerta.u_marco,
      fm: editingPuerta.fm,
    };
    try {
      await axios.put(url, payload, { headers });
      notify("Puerta actualizada con éxito.");
      fetchPuertasDetails();
      setEditingPuerta(null);
    } catch (error: any) {
      if (
        error?.response?.data?.detail ===
        "El nombre del elemento ya existe dentro del tipo door"
      ) {
        notify("El Nombre de la Puerta ya existe");
      } else {
        notify("Error al actualizar la puerta");
      }
    }
  };

  // ===================== RENDER FINAL ======================
  return (
    <>
      <GooIcons />
      <div>
        <Card>
          <div>
            <Title text="Edición de Proyecto" />
            <div className="d-flex align-items-center" style={{ gap: "10px" }}>
              <ProjectInfoHeader projectName={projectName} region={region} project_id={projectId ?? ""} />
              <Breadcrumb
                items={[{ title: "Editar", href: "/", active: true }]}
              />
            </div>
          </div>
        </Card>
        <Card>
          <div className="row">
            <div className="col-12 col-lg-3">
              <AdminSidebar
                activeStep={step}
                onStepChange={handleSidebarStepChange}
                steps={steps}
              />
            </div>
            <div className="col-12 col-lg-9">
              <div className="w-100">
                {step === 3 && (
                  <>
                    {showTabsInStep4
                      ? renderStep4Tabs()
                      : renderInitialDetails()}
                  </>
                )}
                {step === 4 && renderRecinto()}
                {step === 6 && (
                  <div className="mt-3">
                    <ConfiguracionEnergiaTab />
                  </div>
                )}
                {step === 8 && (
                  <AguaCalienteSanitaria
                    onSaveSuccess={() => {
                      setProjectStatus("En proceso");
                    }}
                    actualizarStatus={async () => {
                      if (!projectId) return;
                      try {
                        const token = localStorage.getItem("token");
                        if (!token) return;
                        await axios.put(
                          `${constantUrlApiEndpoint}/project/${projectId}/status`,
                          { status: "En proceso" },
                          { headers: { Authorization: `Bearer ${token}` } }
                        );
                        notify("Estado del proyecto actualizado a 'En proceso'.");
                      } catch {
                        notify("No se pudo actualizar el estado del proyecto");
                      }
                    }}
                  />
                )}
              </div>
            </div>
          </div>
        </Card>

        {projectStatus && (
          <ProjectStatus
            status={projectStatus}
            projectId={String(projectId)}
          />
        )}
      </div>

      {/* Modal para crear un nuevo detalle con la lógica handleCreateNewDetail */}
      <ModalCreate
        detail={null}
        isOpen={showNewDetailRow}
        title="Crear capas (de Interior a Exterior)"
        onClose={() => {
          setShowNewDetailRow(false);
          setNewDetailForm({
            scantilon_location: "",
            name_detail: "",
            material_id: 0,
            layer_thickness: null,
          });
        }}
        onSave={handleCreateNewDetail}
      >
        <form>
          <div className="form-group">
            <label>Ubicación del Detalle</label>
            <select
              className="form-control"
              value={newDetailForm.scantilon_location}
              onChange={(e) =>
                setNewDetailForm((prev) => ({
                  ...prev,
                  scantilon_location: e.target.value,
                }))
              }
            >
              <option value="">Seleccione</option>
              <option value="Muro">Muro</option>
              <option value="Techo">Techo</option>
              <option value="Piso">Piso</option>
            </select>
          </div>
          <div className="form-group">
            <label>Nombre de muro</label>
            <input
              type="text"
              className="form-control"
              placeholder="Nombre Detalle"
              value={newDetailForm.name_detail}
              onChange={(e) => {
                const value = e.target.value;
                if (value.includes("-")) {
                  return;
                }
                setNewDetailForm((prev) => ({ ...prev, name_detail: value }));
              }}
            />
          </div>
          <div className="form-group">
            <label>Material</label>
            <select
              className="form-control"
              value={newDetailForm.material_id}
              onChange={(e) =>
                setNewDetailForm((prev) => ({
                  ...prev,
                  material_id: parseInt(e.target.value, 10),
                }))
              }
            >
              <option value={0}>Seleccione un Material</option>
              {materials.map((mat) => (
                <option key={mat.id} value={mat.id}>
                  {mat.name}
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Espesor de capa (cm)</label>
            <input
              type="number"
              min="0"
              className="form-control"
              placeholder="Espesor (cm)"
              value={newDetailForm.layer_thickness ?? ""}
              onKeyDown={(e) => {
                if (e.key === "-") {
                  e.preventDefault();
                }
              }}
              onChange={(e) => {
                const value = e.target.value;
                if (value.includes("-")) {
                  return;
                }
                setNewDetailForm((prev) => ({
                  ...prev,
                  layer_thickness: parseFloat(value),
                }));
              }}
            />
          </div>
        </form>
      </ModalCreate>

      {/* Modal para mostrar los detalles generales de un registro */}
      <DetailModal
        detail={selectedDetail}
        show={showDetailModal}
        onClose={() => setShowDetailModal(false)}
      />

      {/* Modal para mostrar la tabla de Detalles Generales */}
      <ModalCreate
        detail={null}
        isOpen={showDetallesModal}
        title={`Detalles ${selectedItem?.name_detail || ""}`}
        onClose={() => setShowDetallesModal(false)}
        onSave={() => { }}
        showCancelButton={false}
        showSaveButton={false}
        modalStyle={{ maxWidth: "70%", width: "70%", padding: "32px" }}
      >
        {renderDetallesModalContent()}
      </ModalCreate>

      {/* Modal para editar un Detalle */}
      {editingDetail && (
        <ModalCreate
          isOpen={true}
          title={`Editar Detalle: ${editingDetail.name_detail}`}
          detail={editingDetail}
          onClose={() => setEditingDetail(null)}
          onSave={handleConfirmEditDetail}
        >
          <form>
            <div className="form-group">
              <label>Ubicación</label>
              <input
                type="text"
                className="form-control"
                value={editingDetail.scantilon_location}
                readOnly
              />
            </div>
            <div className="form-group">
              <label>Nombre</label>
              <input
                type="text"
                className="form-control"
                value={editingDetail.name_detail}
                onChange={(e) =>
                  setEditingDetail((prev) =>
                    prev ? { ...prev, name_detail: e.target.value } : prev
                  )
                }
              />
            </div>
            <div className="form-group">
              <label>Material</label>
              <select
                className="form-control"
                value={editingDetail.id_material}
                onChange={(e) =>
                  setEditingDetail((prev) =>
                    prev
                      ? { ...prev, id_material: parseInt(e.target.value, 10) }
                      : prev
                  )
                }
              >
                <option value="">Seleccione Material</option>
                {materials.map((mat: Material) => (
                  <option key={mat.id} value={mat.id}>
                    {mat.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Espesor de capa (cm)</label>
              <input
                type="number"
                min="0"
                className="form-control"
                value={editingDetail.layer_thickness}
                onChange={(e) =>
                  setEditingDetail((prev) =>
                    prev
                      ? { ...prev, layer_thickness: parseFloat(e.target.value) }
                      : prev
                  )
                }
              />
            </div>
          </form>
        </ModalCreate>
      )}

      {/* Modal para editar Ventana */}
      {editingVentana && (
        <ModalCreate
          isOpen={true}
          title="Editar Ventana"
          detail={editingVentana}
          onClose={() => setEditingVentana(null)}
          onSave={handleConfirmVentanaEdit}
        >
          <form>
            <div className="form-group">
              <label>Nombre Elemento</label>
              <input
                type="text"
                className="form-control"
                value={editingVentana.name_element}
                onChange={(e) =>
                  setEditingVentana((prev) =>
                    prev ? { ...prev, name_element: e.target.value } : prev
                  )
                }
              />
            </div>
            <div className="form-group">
              <label>U Vidrio [W/m²K]</label>
              <input
                type="number"
                className="form-control"
                value={editingVentana.atributs?.u_vidrio || ""}
                min="0"
                onKeyDown={(e) => {
                  if (e.key === "-") {
                    e.preventDefault();
                  }
                }}
                onChange={(e) =>
                  setEditingVentana((prev) =>
                    prev
                      ? {
                        ...prev,
                        atributs: {
                          ...prev.atributs,
                          u_vidrio: parseFloat(e.target.value),
                        },
                      }
                      : prev
                  )
                }
              />
            </div>
            <div className="form-group">
              <label>FS Vidrio</label>
              <input
                type="number"
                className="form-control"
                value={editingVentana.atributs?.fs_vidrio || ""}
                min="0"
                onKeyDown={(e) => {
                  if (e.key === "-") {
                    e.preventDefault();
                  }
                }}
                onChange={(e) =>
                  setEditingVentana((prev) =>
                    prev
                      ? {
                        ...prev,
                        atributs: {
                          ...prev.atributs,
                          fs_vidrio: parseFloat(e.target.value),
                        },
                      }
                      : prev
                  )
                }
              />
            </div>
            <div className="form-group">
              <label>Tipo Marco</label>
              <input
                type="text"
                className="form-control"
                value={editingVentana.atributs?.frame_type || ""}
                min="0"
                onKeyDown={(e) => {
                  if (e.key === "-") {
                    e.preventDefault();
                  }
                }}
                onChange={(e) =>
                  setEditingVentana((prev) =>
                    prev
                      ? {
                        ...prev,
                        atributs: {
                          ...prev.atributs,
                          frame_type: e.target.value,
                        },
                      }
                      : prev
                  )
                }
              />
            </div>
            <div className="form-group">
              <label>Tipo Cierre</label>
              <input
                type="text"
                className="form-control"
                value={editingVentana.atributs?.clousure_type || ""}
                onChange={(e) =>
                  setEditingVentana((prev) =>
                    prev
                      ? {
                        ...prev,
                        atributs: {
                          ...prev.atributs,
                          clousure_type: e.target.value,
                        },
                      }
                      : prev
                  )
                }
              />
            </div>
            <div className="form-group">
              <label>U Marco [W/m²K]</label>
              <input
                type="number"
                className="form-control"
                value={editingVentana.u_marco || ""}
                min="0"
                onKeyDown={(e) => {
                  if (e.key === "-") {
                    e.preventDefault();
                  }
                }}
                onChange={(e) =>
                  setEditingVentana((prev) =>
                    prev
                      ? { ...prev, u_marco: parseFloat(e.target.value) }
                      : prev
                  )
                }
              />
            </div>
            <div className="form-group">
              <label>FV [%]</label>
              <input
                type="number"
                className="form-control"
                value={
                  editingVentana.fm !== undefined
                    ? Math.round(editingVentana.fm * 100)
                    : ""
                }
                min="0"
                onKeyDown={(e) => {
                  if (e.key === "-") {
                    e.preventDefault();
                  }
                }}
                onChange={(e) => {
                  const rawValue = e.target.value;
                  if (rawValue === "") {
                    setEditingVentana((prev) =>
                      prev ? { ...prev, fm: 0 } : prev
                    );
                    return;
                  }
                  const val = parseInt(rawValue, 10);
                  if (isNaN(val)) return;
                  const clampedValue = Math.min(100, Math.max(0, val));
                  setEditingVentana((prev) =>
                    prev ? { ...prev, fm: clampedValue / 100 } : prev
                  );
                }}
              />
            </div>
          </form>
        </ModalCreate>
      )}

      {/* Modal para editar Puerta */}
      {editingPuerta && (
        <ModalCreate
          isOpen={true}
          title="Editar Puerta"
          detail={editingPuerta}
          onClose={() => setEditingPuerta(null)}
          onSave={handleConfirmPuertaEdit}
        >
          <form>
            <div className="form-group">
              <label>Nombre Elemento</label>
              <input
                type="text"
                className="form-control"
                value={editingPuerta.name_element}
                onChange={(e) =>
                  setEditingPuerta((prev) =>
                    prev ? { ...prev, name_element: e.target.value } : prev
                  )
                }
              />
            </div>
            <div className="form-group">
              <label>U puerta opaca [W/m²K]</label>
              <input
                type="number"
                className="form-control"
                value={editingPuerta.atributs?.u_puerta_opaca || ""}
                onChange={(e) =>
                  setEditingPuerta((prev) =>
                    prev
                      ? {
                        ...prev,
                        atributs: {
                          ...prev.atributs,
                          u_puerta_opaca: parseFloat(e.target.value),
                        },
                      }
                      : prev
                  )
                }
              />
            </div>
            <div className="form-group">
              <label>Nombre Ventana</label>
              <input
                type="text"
                className="form-control"
                value={editingPuerta.atributs?.name_ventana || ""}
                onChange={(e) =>
                  setEditingPuerta((prev) =>
                    prev
                      ? {
                        ...prev,
                        atributs: {
                          ...prev.atributs,
                          name_ventana: e.target.value,
                        },
                      }
                      : prev
                  )
                }
              />
            </div>
            <div className="form-group">
              <label>% Vidrio</label>
              <input
                type="number"
                className="form-control"
                value={
                  editingPuerta.atributs?.porcentaje_vidrio !== undefined
                    ? Math.round(editingPuerta.atributs.porcentaje_vidrio * 100)
                    : ""
                }
                onChange={(e) => {
                  const rawValue = e.target.value;
                  if (rawValue === "") {
                    setEditingPuerta((prev) =>
                      prev
                        ? {
                          ...prev,
                          atributs: {
                            ...prev.atributs,
                            porcentaje_vidrio: 0,
                          },
                        }
                        : prev
                    );
                    return;
                  }
                  const val = parseInt(rawValue, 10);
                  if (isNaN(val)) return;
                  const clampedValue = Math.min(100, Math.max(0, val));
                  setEditingPuerta((prev) =>
                    prev
                      ? {
                        ...prev,
                        atributs: {
                          ...prev.atributs,
                          porcentaje_vidrio: clampedValue / 100,
                        },
                      }
                      : prev
                  );
                }}
              />
            </div>
            <div className="form-group">
              <label>U Marco [W/m²K]</label>
              <input
                type="number"
                className="form-control"
                value={editingPuerta.u_marco || ""}
                onChange={(e) =>
                  setEditingPuerta((prev) =>
                    prev
                      ? { ...prev, u_marco: parseFloat(e.target.value) }
                      : prev
                  )
                }
              />
            </div>
            <div className="form-group">
              <label>FM [%]</label>
              <input
                type="number"
                className="form-control"
                value={
                  editingPuerta.fm !== undefined
                    ? Math.round(editingPuerta.fm * 100)
                    : ""
                }
                onChange={(e) => {
                  const rawValue = e.target.value;
                  if (rawValue === "") {
                    setEditingPuerta((prev) =>
                      prev ? { ...prev, fm: 0 } : prev
                    );
                    return;
                  }
                  const val = parseInt(rawValue, 10);
                  if (isNaN(val)) return;
                  const clampedValue = Math.min(100, Math.max(0, val));
                  setEditingPuerta((prev) =>
                    prev ? { ...prev, fm: clampedValue / 100 } : prev
                  );
                }}
              />
            </div>
          </form>
        </ModalCreate>
      )}

      {/* Modal de confirmación original para Ventanas / Puertas (no se quita) */}
      {showDeleteModal && deleteItem && (
        <ModalCreate
          isOpen={showDeleteModal}
          title="Confirmar Eliminación"
          onClose={() => setShowDeleteModal(false)}
          onSave={confirmDelete}
          detail={null}
          hideFooter={false}
          modalStyle={{ maxWidth: "500px", width: "500px", padding: "24px" }}
          saveLabel="Confirmar"
        >
          <p>
            {deleteItem.type === "detail"
              ? "¿Estás seguro de que deseas eliminar este detalle?"
              : deleteItem.type === "window"
                ? "¿Estás seguro de que deseas eliminar esta ventana?"
                : "¿Estás seguro de que deseas eliminar esta puerta?"}
          </p>
        </ModalCreate>
      )}

      {/* PISO NUEVO MODAL para /user/detail-create/{detail_part_id} 
          (Se abre al hacer clic en "+ Nuevo" dentro de renderDetallesModalContent) */}
      <ModalCreate
        isOpen={showCreateDetailModal}
        onClose={() => setShowCreateDetailModal(false)}
        onSave={handleCreateDetail}
        title="Crear capas (de Interior a Exterior)"
        saveLabel="Crear Capa"
      >
        <form>
          <div className="form-group">
            <label>Nombre </label>
            <input
              type="text"
              className="form-control"
              value={newDetailData.name_detail}
              readOnly
            />
          </div>
          <div className="form-group">
            <label>Material</label>
            <select
              className="form-control"
              value={newDetailData.material_id}
              onChange={(e) =>
                setNewDetailData({
                  ...newDetailData,
                  material_id: parseInt(e.target.value, 10),
                })
              }
            >
              <option value={0}>Seleccione un material</option>
              {materials.map((mat) => (
                <option key={mat.id} value={mat.id}>
                  {mat.name}
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Espesor de capa (cm)</label>
            <input
              type="number"
              min="0"
              className="form-control"
              placeholder="cm"
              value={
                newDetailData.layer_thickness > 0
                  ? newDetailData.layer_thickness
                  : ""
              }
              onKeyDown={(e) => {
                if (e.key === "-") e.preventDefault();
              }}
              onChange={(e) =>
                setNewDetailData({
                  ...newDetailData,
                  layer_thickness: parseFloat(e.target.value || "0"),
                })
              }
            />
          </div>
        </form>
      </ModalCreate>

      {/* NUEVO Modal de confirmación para eliminar Muro/Techo/Piso con /detail-general/{detail_id}/true */}
      {showDeleteLayerModal && selectedDeleteDetailId && (
        <ModalCreate
          isOpen={showDeleteLayerModal}
          saveLabel="Confirmar"
          onClose={() => setShowDeleteLayerModal(false)}
          onSave={handleDeleteLayer}
          title="Confirmar Eliminación"
        >
          <p>¿Estás seguro que deseas eliminar este detalle?</p>
        </ModalCreate>
      )}
    </>
  );
};

export default WorkFlowpar2editPage;