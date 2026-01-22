import ActionButtonsConfirm from "@/components/common/ActionButtonsConfirm";
import Breadcrumb from "@/components/common/Breadcrumb";
import DeleteDetailButton from "@/components/common/DeleteDetailButton";
import HorizontalTabs from "@/components/common/HorizontalTabs";
import ProjectInfoHeader from "@/components/common/ProjectInfoHeader";
import SearchParameters from "@/components/inputs/SearchParameters";
import TabRecintDataCreate from "@/components/tab_recint_data/TabRecintDataCreate";
import TablesParameters from "@/components/tables/TablesParameters";
import Title from "@/components/Title";
import VerticalDivider from "@/components/ui/HorizontalDivider";
import { notify } from "@/utils/notify";
import axios from "axios";
import "bootstrap/dist/css/bootstrap.min.css";
import { useRouter } from "next/router";
import React, { useCallback, useEffect, useState } from "react";
import GooIcons from "../public/GoogleIcons";
import { AdminSidebar } from "../src/components/administration/AdminSidebar";
import Card from "../src/components/common/Card";
import CustomButton from "../src/components/common/CustomButton";
import ModalCreate from "../src/components/common/ModalCreate";
import useAuth from "../src/hooks/useAuth";
import { constantUrlApiEndpoint } from "../src/utils/constant-url-endpoint";

// Importamos ProjectStatus para el estado y cálculo
import AddDetailOnLayer from "@/components/projects/AddDetailOnLayer";
import ProjectStatus from "@/components/projects/ProjectStatus";
import AguaCalienteSanitaria from "@/components/projects/tabs/AguaCalienteSanitaria";
import { useApi } from "@/hooks/useApi";
import ConfiguracionEnergiaTab from "@/components/projects/tabs/ConfiguracionEnergiaTab";

interface Detail {
  id_detail: number;
  scantilon_location: string;
  name_detail: string;
  material_id: number;
  material: string;
  layer_thickness: number;
  id?: string;
  created_status: string; // "default" | "created" | "global"
}

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
  id?: number;
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

function getCssVarValue(varName: string, fallback: string) {
  if (typeof window === "undefined") return fallback;
  const value = getComputedStyle(document.documentElement)
    .getPropertyValue(varName)
    .trim();
  return value || fallback;
}

const WorkFlowpar2createPage: React.FC = () => {
  useAuth();
  const router = useRouter();
  const api = useApi();

  const [isAdmin, setIsAdmin] = useState(false);
  useEffect(() => {
    const roleId = localStorage.getItem("role_id");
    setIsAdmin(roleId === "1");
  }, []);

  const [projectStatus, setProjectStatus] = useState("En proceso");
  const [projectId, setProjectId] = useState<number | null>(null);
  const [hasLoaded, setHasLoaded] = useState(false);
  const [step, setStep] = useState<number>(4)
  const [primaryColor, setPrimaryColor] = useState("#3ca7b7");
  const [searchQuery, setSearchQuery] = useState("");

  const [fetchedDetails, setFetchedDetails] = useState<Detail[]>([]);
  const [showTabsInStep4, setShowTabsInStep4] = useState(true);
  const [tabStep4, setTabStep4] = useState<TabStep4>("muros");

  interface ExtendedTabItem extends TabItem {
    created_status?: string;
  }

  const [murosTabList, setMurosTabList] = useState<ExtendedTabItem[]>([]);
  const [techumbreTabList, setTechumbreTabList] = useState<ExtendedTabItem[]>(
    []
  );
  const [pisosTabList, setPisosTabList] = useState<ExtendedTabItem[]>([]);
  const [ventanasTabList, setVentanasTabList] = useState<Ventana[]>([]);
  const [puertasTabList, setPuertasTabList] = useState<Puerta[]>([]);
  const [materials, setMaterials] = useState<Material[]>([]);

  const [selectedItem, SetSelectedItem] = useState<any>(null);
  const [editingRowId, setEditingRowId] = useState<number | null>(null);
  // Nuevo estado para editar el nombre abreviado (name_detail) en Muros
  const [editingNombreAbreviado, setEditingNombreAbreviado] =
    useState<string>("");
  // Estados para editar nombre abreviado en Techumbre y Pisos
  const [editingNombreAbreviadoTech, setEditingNombreAbreviadoTech] =
    useState<string>("");
  const [editingNombreAbreviadoPiso, setEditingNombreAbreviadoPiso] =
    useState<string>("");

  // Edición de colores en muros:
  const [editingColors, setEditingColors] = useState<{
    interior: string;
    exterior: string;
  }>({
    interior: "Intermedio",
    exterior: "Intermedio",
  });

  // Edición en techumbre:
  const [editingTechRowId, setEditingTechRowId] = useState<number | null>(null);
  const [editingTechColors, setEditingTechColors] = useState<{
    interior: string;
    exterior: string;
  }>({
    interior: "Intermedio",
    exterior: "Intermedio",
  });

  // Edición en pisos:
  const [editingPisoRowId, setEditingPisoRowId] = useState<number | null>(null);
  const [editingPisoForm, setEditingPisoForm] = useState({
    vertical: { lambda: "", e_aisl: "", d: "" },
    horizontal: { lambda: "", e_aisl: "", d: "" },
  });

  // Edición de ventanas/puertas:
  const [editingVentanaForm, setEditingVentanaForm] = useState<Ventana | null>(
    null
  );
  const [editingPuertaForm, setEditingPuertaForm] = useState<Puerta | null>(
    null
  );
  const [ventanaFmInput, setVentanaFmInput] = useState<string>("");
  const [puertaPorcentajeInput, setPuertaPorcentajeInput] =
    useState<string>("");

  // Edición de un detalle (Modal no-inline)
  const [editingDetail, setEditingDetail] = useState<Detail | null>(null);

  // Edición inline en el modal de Detalles
  const [editingDetailId, setEditingDetailId] = useState<number | null>(null);
  const [editingDetailData, setEditingDetailData] = useState<{
    material_id: number;
    layer_thickness: number;
  }>({
    material_id: 0,
    layer_thickness: 0,
  });

  // Confirmación de borrado:
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [deleteAction, setDeleteAction] = useState<(() => void) | null>(null);

  // Estado del modal que muestra la tabla de detalles:
  const [showDetallesModal, setShowDetallesModal] = useState(false);

  // Info del proyecto
  const [projectName, setProjectName] = useState("");
  const [projectDepartment, setProjectDepartment] = useState("");

  // Modal de "Crear detalle" cuando estás en la Tab (muros/techumbre/pisos)
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newDetalle, setNewDetalle] = useState({
    name_detail: "",
    colorExterior: "Intermedio",
    colorInterior: "Intermedio",
    ref_aisl_vertical: {
      lambda: "",
      e_aisl: "",
      d: "",
    },
    ref_aisl_horizontal: {
      lambda: "",
      e_aisl: "",
      d: "",
    },
  });

  // ----------------------------------------------------
  // Estados y funciones para el NUEVO DETALLE en el modal
  // "Detalles"
  // ----------------------------------------------------
  const [showNewDetailModal, setShowNewDetailModal] = useState(false);
  const [newDetailData, setNewDetailData] = useState({
    scantilon_location: "",
    name_detail: "",
    material_id: 0,
    layer_thickness: 0,
  });

  const [detailsList, SetDetailsList] = useState<Detail[]>([]);

  // Mapping para la ubicación
  const titleMapping: { [key in TabStep4]?: string } = {
    muros: "Muro",
    techumbre: "Techo",
    pisos: "Piso",
  };

  // Mapping para POST /user/[Muro|Techo|Piso]/detail-part-create
  const detailTypeMapping: { [key in TabStep4]?: string } = {
    muros: "Muro",
    techumbre: "Techo",
    pisos: "Piso",
  };

  // ------------------------------------
  // getToken y fetch de datos del proyecto
  // ------------------------------------
  const getToken = () => {
    const token = localStorage.getItem("token");
    if (!token) {
      notify("Token no encontrado", "Inicia sesión.");
    }
    return token;
  };

  const fetchProjectData = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) return;
      if (!projectId) return;
      console.log("projectId", projectId);
      const { data: projectData } = await axios.get(
        `${constantUrlApiEndpoint}/projects/${projectId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setProjectStatus(projectData?.status || "En proceso");
    } catch (error) {
      console.error("Error al obtener el estado del proyecto:", error);
    }
  };

  // --------------------------------
  // Cargar materiales (para selects)
  // --------------------------------
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
    } catch (error) {
      console.error("Error al obtener materiales:", error);
      notify("Error al obtener Materiales.");
    }
  };

  // -------------------------
  // useEffects de inicialización
  // -------------------------
  useEffect(() => {
    const storedProjectId = localStorage.getItem("last_created_project");
    if (storedProjectId) {
      setProjectId(Number(storedProjectId));
    }
    const storedProjectName =
      localStorage.getItem("project_name") || "Nombre no definido";
    const storedProjectDepartment =
      localStorage.getItem("project_department") || "Región no definida";
    setProjectName(storedProjectName);
    setProjectDepartment(storedProjectDepartment);
    setHasLoaded(true);
  }, []);

  useEffect(() => {
    if (hasLoaded && projectId === null) {
      notify(
        "Ningún proyecto está seleccionado",
        "Serás redirigido a la creación de proyecto"
      );
      router.push("/workflow-part1-create");
    }
  }, [hasLoaded, projectId, router]);

  useEffect(() => {
    if (router.query.step) {
      const queryStep = parseInt(router.query.step as string, 10);
      if (!isNaN(queryStep)) {
        setStep(queryStep);
      }
    }
  }, [router.query.step]);

  useEffect(() => {
    const pColor = getCssVarValue("--primary-color", "#3ca7b7");
    setPrimaryColor(pColor);
  }, []);

  useEffect(() => {
    if (projectId) {
      fetchProjectData();
    }
  }, [projectId]);

  // --------------------------------------------------
  // Hooks para recargar materiales en edición/creación
  // --------------------------------------------------
  useEffect(() => {
    if (showCreateModal || editingDetail) {
      fetchMaterials();
    }
  }, [showCreateModal, editingDetail]);

  // ----------------------------------------------------------------
  // useEffects para inputs de Ventanas/Puertas (edición) – fm y % vidrio
  // ----------------------------------------------------------------
  useEffect(() => {
    if (editingVentanaForm) {
      setVentanaFmInput(
        editingVentanaForm.fm !== undefined
          ? String(Math.round(editingVentanaForm.fm * 100))
          : ""
      );
    }
  }, [editingVentanaForm]);

  useEffect(() => {
    if (editingPuertaForm && editingPuertaForm.atributs) {
      setPuertaPorcentajeInput(
        editingPuertaForm.atributs.porcentaje_vidrio !== undefined
          ? String(
            Math.round(editingPuertaForm.atributs.porcentaje_vidrio * 100)
          )
          : ""
      );
    }
  }, [editingPuertaForm]);

  // ---------------------------------
  // Fetches usando useCallback
  // ---------------------------------
  const fetchData = useCallback(
    async <T,>(endpoint: string, setter: (data: T) => void) => {
      if (!projectId) return;
      const token = getToken();
      if (!token) return;

      try {
        const headers = { Authorization: `Bearer ${token}` };
        const response = await axios.get(endpoint, { headers });
        setter(response.data);
      } catch (error) {
        console.error(`Error al obtener datos desde ${endpoint}:`, error);
      }
    },
    [projectId]
  );

  const fetchFetchedDetails = useCallback(async () => {
    const token = getToken();
    if (!token || !projectId) return;

    try {
      const url = `${constantUrlApiEndpoint}/user/details/?project_id=${projectId}`;
      const headers = { Authorization: `Bearer ${token}` };
      const response = await axios.get(url, { headers });
      setFetchedDetails(response.data || []);
    } catch (error) {
      console.error("Error al obtener detalles:", error);
      notify("Error al obtener detalles. Ver consola.");
    }
  }, [projectId]);

  const fetchMurosDetails = useCallback(() => {
    fetchData<TabItem[]>(
      `${constantUrlApiEndpoint}/project/${projectId}/details/Muro`,
      (data) => {
        if (data && data.length > 0) setMurosTabList(data);
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
        notify("Error al obtener datos de ventanas. Ver consola.");
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
        notify("Error al obtener datos de puertas. Ver consola.");
      });
  }, []);

  // -----------------------------------------------
  // Efectos de refresco cuando step=4, o cambia tab
  // -----------------------------------------------
  useEffect(() => {
    if (step === 4 && projectId) {
      fetchFetchedDetails();
    }
  }, [step, fetchFetchedDetails, projectId]);

  useEffect(() => {
    if (showTabsInStep4) {
      setTabStep4("muros");
    }
  }, [showTabsInStep4]);

  useEffect(() => {
    if (showTabsInStep4) {
      switch (tabStep4) {
        case "muros":
          fetchMurosDetails();
          break;
        case "techumbre":
          fetchTechumbreDetails();
          break;
        case "pisos":
          fetchPisosDetails();
          break;
        case "ventanas":
          fetchVentanasDetails();
          break;
        case "puertas":
          fetchPuertasDetails();
          break;
      }
    }
  }, [
    showTabsInStep4,
    tabStep4,
    fetchMurosDetails,
    fetchTechumbreDetails,
    fetchPisosDetails,
    fetchVentanasDetails,
    fetchPuertasDetails,
  ]);

  // -----------------------------------------
  // Funciones para ver el modal de detalles
  // -----------------------------------------
  const fetchDetailModal = (detail_id: any) => {
    // Consulta "detail-part/{detail_id}" y setea "detailsList"
    api.get(`detail-part/${detail_id}`).then((data) => {
      SetDetailsList(data);
    });
  };

  const OnDetailOpened = (detalle: any) => {
    SetSelectedItem(detalle);
    setShowDetallesModal(true);
    fetchDetailModal(detalle?.id);
  };

  // ---------------------------------------------
  // Botón "Nuevo" en las tabs (muros/techumbre...)
  // ---------------------------------------------
  const handleNewButtonClick = () => {
    setShowCreateModal(true);
    setShowDetallesModal(false);
  };

  // -------------------------------
  // Manejo de creación de Detalles
  // -------------------------------
  // "handleSaveDetalle" = crea un Detalle constructivo (Muro, Techo o Piso)
  // con su color exterior/interior
  const handleSaveDetalle = async () => {
    if (
      !newDetalle.name_detail ||
      (tabStep4 !== "pisos" &&
        (!newDetalle.colorInterior || !newDetalle.colorExterior))
    ) {
      notify("Por favor, complete todos los campos del Detalle Constructivo.");
      return;
    }

    const token = getToken();
    const projectId = localStorage.getItem("project_id");
    if (!token || !projectId) return;

    const type = detailTypeMapping[tabStep4] || "Muro";
    let payload;

    if (type === "Piso") {
      // Pide info de ref_aisl_vertical/horizontal:
      payload = {
        name_detail: newDetalle.name_detail,
        info: {
          ref_aisl_vertical: {
            d: Number(newDetalle.ref_aisl_vertical.d),
            e_aisl: Number(newDetalle.ref_aisl_vertical.e_aisl),
            lambda: Number(newDetalle.ref_aisl_vertical.lambda),
          },
          ref_aisl_horizontal: {
            d: Number(newDetalle.ref_aisl_horizontal.d),
            e_aisl: Number(newDetalle.ref_aisl_horizontal.e_aisl),
            lambda: Number(newDetalle.ref_aisl_horizontal.lambda),
          },
        },
      };
    } else {
      // Muro / Techo
      payload = {
        name_detail: newDetalle.name_detail,
        info: {
          surface_color: {
            interior: { name: newDetalle.colorInterior },
            exterior: { name: newDetalle.colorExterior },
          },
        },
      };
    }

    try {
      const url = `${constantUrlApiEndpoint}/user/${type}/detail-part-create?project_id=${projectId}`;
      const headers = {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      };
      await axios.post(url, payload, { headers });

      notify("Detalle creado exitosamente.");

      if (type === "Muro") fetchMurosDetails();
      if (type === "Techo") fetchTechumbreDetails();
      if (type === "Piso") fetchPisosDetails();

      // Cierra el modal + refresca la lista general
      setShowCreateModal(false);
      setNewDetalle({
        name_detail: "",
        colorExterior: "Intermedio",
        colorInterior: "Intermedio",
        ref_aisl_vertical: {
          lambda: "",
          e_aisl: "",
          d: "",
        },
        ref_aisl_horizontal: {
          lambda: "",
          e_aisl: "",
          d: "",
        },
      });
      fetchFetchedDetails();
    } catch (error) {
      console.error("Error al crear detalle constructivo:", error);
      notify("Ya existe un detalle con el nombre ingresado.");
    }
  };

  // "handleSaveNewDetail" = crea un detalle nuevo con:
  // POST /user/detail-create/{detail_part_id}
  // Este se usa cuando estás dentro del modal "Detalles"
  // y das clic en "+ Nuevo"
  const handleSaveNewDetail = async () => {
    if (
      !newDetailData.scantilon_location.trim() ||
      !newDetailData.name_detail.trim() ||
      newDetailData.material_id <= 0 ||
      newDetailData.layer_thickness <= 0
    ) {
      notify("Por favor, completa todos los campos correctamente.");
      return;
    }

    const token = getToken();
    if (!token || !selectedItem?.id) return;

    try {
      const url = `${constantUrlApiEndpoint}/user/detail-create/${selectedItem.id}`;
      const headers = {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      };

      await axios.post(url, newDetailData, { headers });
      notify("Detalle creado con éxito.");

      // Recarga la tabla del modal
      fetchDetailModal(selectedItem.id);

      // Recargar las tablas principales para actualizar el valor U
      if (tabStep4 === "muros") await fetchMurosDetails();
      if (tabStep4 === "techumbre") await fetchTechumbreDetails();
      if (tabStep4 === "pisos") await fetchPisosDetails();

      // Cierra el modal y resetea los campos
      setShowNewDetailModal(false);
      setNewDetailData({
        scantilon_location: "",
        name_detail: "",
        material_id: 0,
        layer_thickness: 0,
      });
    } catch (error) {
      console.error("Error al crear detalle:", error);
      notify("Error al crear el Detalle.");
    }
  };

  // ------------------------------------
  // Editar un Detalle (Modal no-inline)
  // ------------------------------------
  const handleEditDetail = (detail: Detail) => {
    setShowDetallesModal(false);
    setEditingDetail(detail);
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

      // Recargar data
      fetchFetchedDetails();
      fetchMurosDetails();
      fetchTechumbreDetails();
      fetchPisosDetails();

      setEditingDetail(null);
      setShowDetallesModal(true);
    } catch (error) {
      console.error("Error al actualizar el detalle:", error);
      notify("Error al actualizar el Detalle.");
    }
  };

  // ------------------------------------------------
  // Edición inline en el Modal "Detalles"
  // ------------------------------------------------
  const handleInlineEdit = (detail: Detail) => {
    const uniqueId = detail.id_detail || Number(detail.id);
    setEditingDetailId(uniqueId);
    setEditingDetailData({
      material_id: detail.material_id,
      layer_thickness: detail.layer_thickness,
    });
  };

  const handleConfirmInlineEdit = async (detail: Detail) => {
    const uniqueId = detail.id_detail || Number(detail.id);
    if (editingDetailData.material_id <= 0) {
      notify("Por favor, seleccione un material válido.");
      return;
    }
    if (editingDetailData.layer_thickness <= 0) {
      notify("El 'Espesor de capa' debe ser un valor mayor a 0.");
      return;
    }

    const token = getToken();
    if (!token || !uniqueId) return;

    try {
      const url = `${constantUrlApiEndpoint}/user/detail-update/${uniqueId}`;
      const headers = {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      };

      const payload = {
        scantilon_location: detail.scantilon_location,
        name_detail: detail.name_detail,
        material_id: editingDetailData.material_id,
        layer_thickness: editingDetailData.layer_thickness,
      };

      await axios.patch(url, payload, { headers });
      notify("Detalle actualizado exitosamente");

      // Recarga
      fetchDetailModal(selectedItem?.id);
      fetchFetchedDetails();

      // Recargar las tablas principales para actualizar el valor U
      if (tabStep4 === "muros") await fetchMurosDetails();
      if (tabStep4 === "techumbre") await fetchTechumbreDetails();
      if (tabStep4 === "pisos") await fetchPisosDetails();
    } catch (error) {
      console.error("Error al actualizar el detalle:", error);
      notify("Error al actualizar el detalle.");
    }
    setEditingDetailId(null);
  };

  const handleCancelInlineEdit = () => {
    setEditingDetailId(null);
  };

  // ---------------------------
  // Eliminar un Detalle
  // ---------------------------
  const handleDeleteDetail = async (detailId: number) => {
    const token = getToken();
    if (!token || !projectId) return;

    try {
      const url = `${constantUrlApiEndpoint}/user/${detailId}/details/delete?project_id=${projectId}`;
      await axios.delete(url, {
        headers: { Authorization: `Bearer ${token}` },
      });
      notify("Detalle eliminado exitosamente.");

      // *** Aquí refrescas las tablas ***
      await fetchFetchedDetails();
      await fetchMurosDetails();
      await fetchTechumbreDetails();
      await fetchPisosDetails();
      // Si tenías abierto el modal de capas:
      if (selectedItem?.id) await fetchDetailModal(selectedItem.id);
    } catch (error) {
      console.error(error);
      notify("Error al eliminar el detalle.");
    }
  };

  const confirmDeleteDetail = (detailId: number) => {
    setShowDetallesModal(false);
    setDeleteAction(() => () => handleDeleteDetail(detailId));
    setShowConfirmModal(true);
  };

  // ---------------------------
  // Eliminar una Ventana/Puerta
  // ---------------------------
  const handleDeleteElement = async (elementId: number, type: string) => {
    const token = getToken();
    if (!token || !projectId) return;

    try {
      const url = `${constantUrlApiEndpoint}/user/elements/${elementId}/delete?type=${type}`;
      const headers = { Authorization: `Bearer ${token}` };
      await axios.delete(url, { headers });

      notify("Elemento eliminado exitosamente.");

      if (type === "window") {
        fetchVentanasDetails();
      } else if (type === "door") {
        fetchPuertasDetails();
      }
    } catch (error) {
      console.error("Error al eliminar el elemento:", error);
      notify("Error al eliminar el elemento.");
    }
  };

  const confirmDeleteElement = (elementId: number, type: string) => {
    setShowDetallesModal(false);
    setDeleteAction(() => () => handleDeleteElement(elementId, type));
    setShowConfirmModal(true);
  };

  // --------------------------------------------------
  // Edición inline de Muros (color, name_detail)
  // --------------------------------------------------
  const handleEditClick = (detail: TabItem) => {
    setEditingRowId(detail.id || null);
    setEditingColors({
      interior: detail.info?.surface_color?.interior?.name || "Intermedio",
      exterior: detail.info?.surface_color?.exterior?.name || "Intermedio",
    });
    setEditingNombreAbreviado(detail.name_detail);
  };

  const handleCancelEdit = (detail: TabItem) => {
    setEditingRowId(null);
    setEditingColors({
      interior: detail.info?.surface_color?.interior?.name || "Intermedio",
      exterior: detail.info?.surface_color?.exterior?.name || "Intermedio",
    });
  };

  const handleConfirmEdit = async (detail: TabItem) => {
    if (!projectId) return;
    const token = getToken();
    if (!token) return;

    try {
      const url = `${constantUrlApiEndpoint}/project/${projectId}/update_details/Muro/${detail.id}`;
      const headers = {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      };

      const payload = {
        name_detail: editingNombreAbreviado,
        info: {
          surface_color: {
            interior: { name: editingColors.interior },
            exterior: { name: editingColors.exterior },
          },
        },
      };

      await axios.put(url, payload, { headers });
      notify("Detalle tipo Muro actualizado con éxito.");
      fetchMurosDetails();
      setEditingRowId(null);
    } catch (error) {
      console.error("Error al actualizar detalle:", error);
      notify("Ya existe un detalle con el nombre asignado.");
    }
  };

  // --------------------------------------------------
  // Edición inline de Techumbre (color, name_detail)
  // --------------------------------------------------
  const handleEditTechClick = (detail: TabItem) => {
    setEditingTechRowId(detail.id || null);
    setEditingTechColors({
      interior: detail.info?.surface_color?.interior?.name || "Intermedio",
      exterior: detail.info?.surface_color?.exterior?.name || "Intermedio",
    });
    setEditingNombreAbreviadoTech(detail.name_detail);
  };

  const handleCancelTechEdit = (detail: TabItem) => {
    setEditingTechRowId(null);
    setEditingTechColors({
      interior: detail.info?.surface_color?.interior?.name || "Intermedio",
      exterior: detail.info?.surface_color?.exterior?.name || "Intermedio",
    });
  };

  const handleConfirmTechEdit = async (detail: TabItem) => {
    if (!projectId) return;
    const token = getToken();
    if (!token) return;

    try {
      const url = `${constantUrlApiEndpoint}/project/${projectId}/update_details/Techo/${detail.id}`;
      const headers = {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      };
      const payload = {
        name_detail: editingNombreAbreviadoTech,
        info: {
          surface_color: {
            interior: { name: editingTechColors.interior },
            exterior: { name: editingTechColors.exterior },
          },
        },
      };
      await axios.put(url, payload, { headers });
      notify("Detalle tipo Techo actualizado con éxito.");
      fetchTechumbreDetails();
      setEditingTechRowId(null);
    } catch (error) {
      console.error("Error al actualizar detalle:", error);
      notify("Ya existe un detalle con el nombre asignado.");
    }
  };

  // -----------------------------------------------------------
  // Edición inline de Pisos (name_detail + aisl. vertical/horiz)
  // -----------------------------------------------------------
  const handleEditPisoClick = (detail: TabItem) => {
    setEditingPisoRowId(detail.id || null);

    setEditingPisoForm({
      vertical: {
        lambda: detail.info?.ref_aisl_vertical?.lambda?.toString() || "",
        e_aisl: detail.info?.ref_aisl_vertical?.e_aisl?.toString() || "",
        d: detail.info?.ref_aisl_vertical?.d?.toString() || "",
      },
      horizontal: {
        lambda: detail.info?.ref_aisl_horizontal?.lambda?.toString() || "",
        e_aisl: detail.info?.ref_aisl_horizontal?.e_aisl?.toString() || "",
        d: detail.info?.ref_aisl_horizontal?.d?.toString() || "",
      },
    });
    setEditingNombreAbreviadoPiso(detail.name_detail);
  };

  const handleCancelPisoEdit = () => {
    setEditingPisoRowId(null);
  };

  const handleConfirmPisoEdit = async (detail: TabItem) => {
    if (!projectId) return;
    const token = getToken();
    if (!token) return;

    try {
      const url = `${constantUrlApiEndpoint}/project/${projectId}/update_details/Piso/${detail.id}`;
      const headers = {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      };
      const payload = {
        name_detail: editingNombreAbreviadoPiso,
        info: {
          ref_aisl_vertical: {
            d: Number(editingPisoForm.vertical.d),
            e_aisl: Number(editingPisoForm.vertical.e_aisl),
            lambda: Number(editingPisoForm.vertical.lambda),
          },
          ref_aisl_horizontal: {
            d: Number(editingPisoForm.horizontal.d),
            e_aisl: Number(editingPisoForm.horizontal.e_aisl),
            lambda: Number(editingPisoForm.horizontal.lambda),
          },
        },
      };

      await axios.put(url, payload, { headers });
      notify("Detalle tipo Piso actualizado con éxito");
      fetchPisosDetails();
      setEditingPisoRowId(null);
    } catch (error) {
      console.error("Error al actualizar detalle de Piso:", error);
      notify("Ya existe un detalle con el nombre asignado.");
    }
  };

  // -----------------------------
  // Edición de Ventanas y Puertas
  // -----------------------------
  const handleConfirmVentanaEdit = async (ventana: Ventana) => {
    if (!projectId) return;
    const token = getToken();
    if (!token) return;

    try {
      const url = `${constantUrlApiEndpoint}/user/elements/${ventana.id}/update`;
      const headers = {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      };
      const payload = {
        name_element: ventana.name_element,
        type: "window",
        atributs: ventana.atributs,
        u_marco: ventana.u_marco,
        fm: ventana.fm,
      };
      await axios.put(url, payload, { headers });
      notify("Detalle tipo Ventana actualizado con éxito.");
      fetchVentanasDetails();
      setEditingVentanaForm(null);
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

  const handleConfirmPuertaEdit = async (puerta: Puerta) => {
    if (!projectId) return;
    const token = getToken();
    if (!token) return;

    try {
      const url = `${constantUrlApiEndpoint}/user/elements/${puerta.id}/update`;
      const headers = {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      };
      const payload = {
        name_element: puerta.name_element,
        type: "door",
        atributs: puerta.atributs,
        u_marco: puerta.u_marco,
        fm: puerta.fm,
      };
      await axios.put(url, payload, { headers });
      notify("Detalle tipo Puerta actualizado con éxito.");
      fetchPuertasDetails();
      setEditingPuertaForm(null);
    } catch (error: any) {
      console.error("Error al actualizar puerta:", error);
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

  // ---------------------------------
  // Render de encabezado principal
  // ---------------------------------
  const renderMainHeader = () => <Title text="Desarrollo de proyecto" />;

  // ---------------------------------
  // Render de la tabla de DETALLES
  // dentro del modal "Detalles"
  // ---------------------------------
  const renderDetallesModalContent = () => {
    const columnsDetails = [
      { headerName: "Ubicación Detalle", field: "scantilon_location" },
      { headerName: "Nombre Detalle", field: "name_detail" },
      { headerName: "Material", field: "material" },
      { headerName: "Espesor capa (cm)", field: "layer_thickness" },
      { headerName: "Acción", field: "accion" },
    ];

    const data = detailsList.map((det: any) => {
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
            <DeleteDetailButton
              disabled={
                det.created_status === "default" ||
                det.created_status === "global"
              }
              detailId={det.id}
              onDelete={() => {
                // Tras borrado, refresca
                fetchFetchedDetails();
                fetchMurosDetails();
                fetchTechumbreDetails();
                fetchPisosDetails();
                fetchDetailModal(selectedItem?.id);
              }}
            />
          </>
        ),
      };
    });

    return (
      <>
        {/* Botón que abre el modal de "Crear Detalle" con POST /detail-create/{detail_part_id} */}
        <div
          style={{
            display: "flex",
            justifyContent: "flex-end",
            marginBottom: "1rem",
          }}
        >
          <CustomButton
            disabled={
              selectedItem?.created_status === "default" ||
              selectedItem?.created_status === "global"
            }
            variant="save"
            onClick={() => {
              // PRELLENAR CAMPOS segun la pestaña:
              const locationFromTab =
                tabStep4 === "muros"
                  ? "Muro"
                  : tabStep4 === "techumbre"
                    ? "Techo"
                    : tabStep4 === "pisos"
                      ? "Piso"
                      : "";

              setNewDetailData((prev) => ({
                ...prev,
                scantilon_location: locationFromTab,
                name_detail: selectedItem?.name_detail || "",
              }));

              setShowNewDetailModal(true);
              fetchMaterials();
            }}
          >
            + Nuevo
          </CustomButton>
        </div>

        <TablesParameters columns={columnsDetails} data={data} />
      </>
    );
  };

  // -------------------------------------
  // Render de la tabla "Inicial" de detalles
  // -------------------------------------
  const renderInitialDetails = () => {
    return (
      <>
        <SearchParameters
          value={searchQuery}
          onChange={setSearchQuery}
          placeholder="Buscar..."
          onNew={handleNewButtonClick}
          newButtonText="Nuevo"
          style={{ marginBottom: "1rem" }}
        />
        <div style={{ height: "400px", overflowY: "auto", overflowX: "auto" }}>
          <TablesParameters
            columns={[
              { headerName: "Ubicación Detalle", field: "scantilon_location" },
              { headerName: "Nombre Detalle", field: "name_detail" },
              { headerName: "Material", field: "material" },
              { headerName: "Espesor capa (cm)", field: "layer_thickness" },
              { headerName: "Acción", field: "accion" },
            ]}
            data={fetchedDetails
              .filter((det) => {
                const searchLower = searchQuery.toLowerCase();
                return (
                  det.scantilon_location.toLowerCase().includes(searchLower) ||
                  det.name_detail.toLowerCase().includes(searchLower) ||
                  det.material.toLowerCase().includes(searchLower) ||
                  det.layer_thickness.toString().includes(searchLower)
                );
              })
              .map((det) => {
                const textStyle =
                  det.created_status === "created"
                    ? { color: "var(--primary-color)", fontWeight: "bold" }
                    : {};
                return {
                  scantilon_location: (
                    <span style={textStyle}>{det.scantilon_location}</span>
                  ),
                  name_detail: <span style={textStyle}>{det.name_detail}</span>,
                  material: (
                    <span style={textStyle}>
                      {det.material &&
                        det.material !== "0" &&
                        det.material.toUpperCase() !== "N/A"
                        ? det.material
                        : "-"}
                    </span>
                  ),
                  layer_thickness: (
                    <span style={textStyle}>
                      {det.layer_thickness && det.layer_thickness > 0
                        ? det.layer_thickness
                        : "-"}
                    </span>
                  ),
                  accion: (
                    <>
                      <CustomButton
                        variant="editIcon"
                        onClick={() => handleEditDetail(det)}
                      >
                        Editar
                      </CustomButton>
                      <CustomButton
                        variant="deleteIcon"
                        onClick={() => confirmDeleteDetail(det.id_detail)}
                      >
                        <span className="material-icons">delete</span>
                      </CustomButton>
                    </>
                  ),
                };
              })}
          />
        </div>
      </>
    );
  };

  // ------------------------------------------
  // Render de la tabla de Muros (inline edit)
  // ------------------------------------------
  const renderMurosTable = () => {
    const columnsMuros = [
      { headerName: "Nombre Abreviado", field: "nombreAbreviado" },
      { headerName: "Valor U (W/m²K)", field: "valorU" },
      { headerName: "Color Exterior", field: "colorExterior" },
      { headerName: "Color Interior", field: "colorInterior" },
      { headerName: "Acciones", field: "acciones", sortable: false },
    ];

    const murosData = murosTabList
      .filter((m) =>
        m.name_detail.toLowerCase().includes(searchQuery.toLowerCase())
      )
      .map((item) => {
        const isEditing = editingRowId === item.id;
        const textStyle =
          item.created_status === "created"
            ? { color: "var(--primary-color)", fontWeight: "bold" }
            : {};
        return {
          code_ifc: <span style={textStyle}>{item.code_ifc || "-"}</span>,
          nombreAbreviado: isEditing ? (
            item.created_status === "default" ||
              item.created_status === "global" ? (
              <input
                type="text"
                className="form-control"
                value={editingNombreAbreviado}
                readOnly
              />
            ) : (
              <input
                type="text"
                className="form-control"
                value={editingNombreAbreviado}
                onChange={(e) => {
                  setEditingNombreAbreviado(e.target.value);
                }}
              />
            )
          ) : (
            <span style={textStyle}>{item.name_detail}</span>
          ),
          valorU: (
            <span style={textStyle}>{item.value_u?.toFixed(2) ?? "--"}</span>
          ),
          colorExterior: isEditing ? (
            <select
              value={editingColors.exterior}
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
            <span style={textStyle}>
              {item.info?.surface_color?.exterior?.name || "Desconocido"}
            </span>
          ),
          colorInterior: isEditing ? (
            <select
              value={editingColors.interior}
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
            <span style={textStyle}>
              {item.info?.surface_color?.interior?.name || "Desconocido"}
            </span>
          ),
          acciones: isEditing ? (
            <div onClick={(e) => e.stopPropagation()}>
              <ActionButtonsConfirm
                onAccept={() => handleConfirmEdit(item)}
                onCancel={() => handleCancelEdit(item)}
              />
            </div>
          ) : (
            <div>
              <AddDetailOnLayer item={item} OnDetailOpened={OnDetailOpened} />
              <CustomButton
                disabled={
                  item.created_status === "default" ||
                  item.created_status === "global"
                }
                className="btn-table"
                variant="editIcon"
                onClick={(e) => {
                  e.stopPropagation();
                  handleEditClick(item);
                }}
              >
                Editar
              </CustomButton>
              <CustomButton
                variant="deleteIcon"
                onClick={(e: React.MouseEvent) => {
                  e.stopPropagation();
                  const detailId = item.id_detail || item.id;
                  if (detailId) {
                    confirmDeleteDetail(detailId);
                  }
                }}
                disabled={
                  item.created_status === "default" ||
                  item.created_status === "global"
                }
              >
                <span className="material-icons">delete</span>
              </CustomButton>
            </div>
          ),
        };
      });

    return (
      <div style={{ overflowX: "auto" }}>
        {murosTabList.length > 0 ? (
          <TablesParameters columns={columnsMuros} data={murosData} />
        ) : (
          <p>No hay datos</p>
        )}
      </div>
    );
  };

  // ------------------------------------------
  // Render de la tabla de Techumbre (inline edit)
  // ------------------------------------------
  const renderTechumbreTable = () => {
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
      .filter((t) =>
        t.name_detail.toLowerCase().includes(searchQuery.toLowerCase())
      )
      .map((item) => {
        const isEditing = editingTechRowId === item.id;
        const textStyle =
          item.created_status === "created"
            ? { color: "var(--primary-color)", fontWeight: "bold" }
            : {};
        return {
          code_ifc: <span style={textStyle}>{item.code_ifc || "-"}</span>,
          nombreAbreviado: isEditing ? (
            item.created_status === "default" ||
              item.created_status === "global" ? (
              <input
                type="text"
                className="form-control"
                value={editingNombreAbreviadoTech}
                readOnly
              />
            ) : (
              <input
                type="text"
                className="form-control"
                value={editingNombreAbreviadoTech}
                onChange={(e) => setEditingNombreAbreviadoTech(e.target.value)}
              />
            )
          ) : (
            <span style={textStyle}>{item.name_detail}</span>
          ),
          valorU: (
            <span style={textStyle}>{item.value_u?.toFixed(2) ?? "--"}</span>
          ),
          colorExterior: isEditing ? (
            <select
              value={editingTechColors.exterior}
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
            <span style={textStyle}>
              {item.info?.surface_color?.exterior?.name || "Desconocido"}
            </span>
          ),
          colorInterior: isEditing ? (
            <select
              value={editingTechColors.interior}
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
            <span style={textStyle}>
              {item.info?.surface_color?.interior?.name || "Desconocido"}
            </span>
          ),
          acciones: isEditing ? (
            <div onClick={(e) => e.stopPropagation()}>
              <ActionButtonsConfirm
                onAccept={() => handleConfirmTechEdit(item)}
                onCancel={() => handleCancelTechEdit(item)}
              />
            </div>
          ) : (
            <div>
              <AddDetailOnLayer item={item} OnDetailOpened={OnDetailOpened} />
              <CustomButton
                disabled={
                  item.created_status === "default" ||
                  item.created_status === "global"
                }
                variant="editIcon"
                className="btn-table"
                onClick={(e) => {
                  e.stopPropagation();
                  handleEditTechClick(item);
                }}
              >
                Editar
              </CustomButton>
              <CustomButton
                variant="deleteIcon"
                onClick={(e: React.MouseEvent) => {
                  e.stopPropagation();
                  const detailId = item.id_detail || item.id;
                  if (detailId) {
                    confirmDeleteDetail(detailId);
                  }
                }}
                disabled={
                  item.created_status === "default" ||
                  item.created_status === "global"
                }
              >
                <span className="material-icons">delete</span>
              </CustomButton>
            </div>
          ),
        };
      });

    return (
      <div style={{ minWidth: "600px", overflowX: "auto" }}>
        {techumbreTabList.length > 0 ? (
          <TablesParameters columns={columnsTech} data={techData} />
        ) : (
          <p>No hay datos</p>
        )}
      </div>
    );
  };

  // ---------------------------------
  // Render de la tabla de Pisos
  // ---------------------------------
  const multiHeaderPisos = {
    rows: [
      // Fila 1: IFC, Nombre, U y grupos, Acciones
      [
        { label: "Código IFC", field: "code_ifc", rowSpan: 2, sortable: true },
        { label: "Nombre", field: "nombre", rowSpan: 2, sortable: true },
        { label: "U [W/m²K]", field: "uValue", rowSpan: 2, sortable: true },
        { label: "Aislamiento bajo piso", colSpan: 2 },
        { label: "Ref Aisl Vert.", colSpan: 3 },
        { label: "Ref Aisl Horiz.", colSpan: 3 },
        { label: "Acciones", field: "acciones", rowSpan: 2, sortable: false },
      ],
      // Fila 2: subcolumnas ordenables
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


  const formatNumber = (
    num: number | string | undefined,
    decimals = 2
  ): string => {
    const parsedNum = Number(num);
    return !isNaN(parsedNum) && parsedNum !== 0
      ? parsedNum.toFixed(decimals)
      : "-";
  };

  const renderPisosTable = () => {
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
      { headerName: "Acciones", field: "acciones", colSpan: 4 },
    ];

    const pisosData = pisosTabList
      .filter((p) =>
        p.name_detail.toLowerCase().includes(searchQuery.toLowerCase())
      )
      .map((item) => {
        const bajoPiso = item.info?.aislacion_bajo_piso || {};
        const vert = item.info?.ref_aisl_vertical || {};
        const horiz = item.info?.ref_aisl_horizontal || {};
        const isEditing = editingPisoRowId === item.id;
        const textStyle =
          item.created_status === "created"
            ? { color: "var(--primary-color)", fontWeight: "bold" }
            : {};

        return {
          code_ifc: <span style={textStyle}>{item.code_ifc || "-"}</span>,
          nombre: isEditing ? (
            item.created_status === "default" ||
              item.created_status === "global" ? (
              <input
                type="text"
                className="form-control"
                value={editingNombreAbreviadoPiso}
                readOnly
              />
            ) : (
              <input
                type="text"
                className="form-control"
                value={editingNombreAbreviadoPiso}
                onChange={(e) => setEditingNombreAbreviadoPiso(e.target.value)}
              />
            )
          ) : (
            <span style={textStyle}>{item.name_detail}</span>
          ),
          uValue: <span style={textStyle}>{formatNumber(item.value_u, 2)}</span>,
          bajoPisoLambda: (
            <span style={textStyle}>
              {bajoPiso.lambda != null && bajoPiso.lambda !== 0
                ? Number(bajoPiso.lambda).toFixed(2)
                : "-"}
            </span>
          ),
          bajoPisoEAisl: (
            <span style={textStyle}>
              {bajoPiso.e_aisl != null && bajoPiso.e_aisl !== 0
                ? Number(bajoPiso.e_aisl).toFixed(2)
                : "-"}
            </span>
          ),

          vertLambda: isEditing ? (
            <input
              type="number"
              min="0"
              step="any"
              className="form-control form-control-sm"
              value={editingPisoForm.vertical.lambda}
              onKeyDown={(e) => {
                if (e.key === "-") e.preventDefault();
              }}
              onChange={(e) =>
                setEditingPisoForm((prev) => ({
                  ...prev,
                  vertical: { ...prev.vertical, lambda: e.target.value },
                }))
              }
            />
          ) : (
            <span style={textStyle}>
              {vert.lambda && vert.lambda > 0
                ? Number(vert.lambda).toFixed(2)
                : "-"}
            </span>
          ),

          vertEAisl: isEditing ? (
            <input
              type="number"
              min="0"
              step="any"
              className="form-control form-control-sm"
              value={editingPisoForm.vertical.e_aisl}
              onKeyDown={(e) => {
                if (e.key === "-") e.preventDefault();
              }}
              onChange={(e) =>
                setEditingPisoForm((prev) => ({
                  ...prev,
                  vertical: { ...prev.vertical, e_aisl: e.target.value },
                }))
              }
            />
          ) : (
            <span style={textStyle}>
              {vert.e_aisl && vert.e_aisl > 0
                ? Number(vert.e_aisl).toFixed(2)
                : "-"}
            </span>
          ),

          vertD: isEditing ? (
            <input
              type="number"
              min="0"
              step="any"
              className="form-control form-control-sm"
              value={editingPisoForm.vertical.d}
              onKeyDown={(e) => {
                if (e.key === "-") e.preventDefault();
              }}
              onChange={(e) =>
                setEditingPisoForm((prev) => ({
                  ...prev,
                  vertical: { ...prev.vertical, d: e.target.value },
                }))
              }
            />
          ) : (
            <span style={textStyle}>
              {vert.d && vert.d > 0
                ? Number(vert.d).toFixed(2)
                : "-"}
            </span>
          ),

          horizLambda: isEditing ? (
            <input
              type="number"
              min="0"
              step="any"
              className="form-control form-control-sm"
              value={editingPisoForm.horizontal.lambda}
              onKeyDown={(e) => {
                if (e.key === "-") e.preventDefault();
              }}
              onChange={(e) =>
                setEditingPisoForm((prev) => ({
                  ...prev,
                  horizontal: { ...prev.horizontal, lambda: e.target.value },
                }))
              }
            />
          ) : (
            <span style={textStyle}>
              {horiz.lambda && horiz.lambda > 0
                ? Number(horiz.lambda).toFixed(2)
                : "-"}
            </span>
          ),

          horizEAisl: isEditing ? (
            <input
              type="number"
              min="0"
              step="any"
              className="form-control form-control-sm"
              value={editingPisoForm.horizontal.e_aisl}
              onKeyDown={(e) => {
                if (e.key === "-") e.preventDefault();
              }}
              onChange={(e) =>
                setEditingPisoForm((prev) => ({
                  ...prev,
                  horizontal: { ...prev.horizontal, e_aisl: e.target.value },
                }))
              }
            />
          ) : (
            <span style={textStyle}>
              {horiz.e_aisl && horiz.e_aisl > 0
                ? Number(horiz.e_aisl).toFixed(2)
                : "-"}
            </span>
          ),

          horizD: isEditing ? (
            <input
              type="number"
              min="0"
              step="any"
              className="form-control form-control-sm"
              value={editingPisoForm.horizontal.d}
              onKeyDown={(e) => {
                if (e.key === "-") e.preventDefault();
              }}
              onChange={(e) =>
                setEditingPisoForm((prev) => ({
                  ...prev,
                  horizontal: { ...prev.horizontal, d: e.target.value },
                }))
              }
            />
          ) : (
            <span style={textStyle}>
              {horiz.d && horiz.d > 0
                ? Number(horiz.d).toFixed(2)
                : "-"}
            </span>
          ),

          acciones: isEditing ? (
            <div
              style={{ width: "160px" }}
              onClick={(e) => e.stopPropagation()}
            >
              <ActionButtonsConfirm
                onAccept={() => handleConfirmPisoEdit(item)}
                onCancel={() => handleCancelPisoEdit()}
              />
            </div>
          ) : (
            <div style={{ width: "160px" }}>
              <AddDetailOnLayer item={item} OnDetailOpened={OnDetailOpened} />
              <CustomButton
                disabled={
                  item.created_status === "default" ||
                  item.created_status === "global"
                }
                className="btn-table"
                variant="editIcon"
                onClick={(e) => {
                  e.stopPropagation();
                  handleEditPisoClick(item);
                }}
              >
                Editar
              </CustomButton>
              <CustomButton
                variant="deleteIcon"
                onClick={(e: React.MouseEvent) => {
                  e.stopPropagation();
                  const detailId = item.id_detail || item.id;
                  if (detailId) {
                    confirmDeleteDetail(detailId);
                  }
                }}
                disabled={
                  item.created_status === "default" ||
                  item.created_status === "global"
                }
              >
                <span className="material-icons">delete</span>
              </CustomButton>
            </div>
          ),
        };
      });

    return (
      <div style={{ minWidth: "600px", overflowX: "auto" }}>
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


  // --------------------------------
  // Render de Tabs en el Step=4
  // --------------------------------
  const renderStep4Tabs = () => {
    if (!showTabsInStep4) return null;
    const tabs = [
      { key: "muros", label: "Muros" },
      { key: "techumbre", label: "Techumbre" },
      { key: "pisos", label: "Pisos" },
      // Pestañas de ventanas y puertas comentadas temporalmente
      /*
      { key: "ventanas", label: "Ventanas" },
      { key: "puertas", label: "Puertas" },
      */
    ] as { key: TabStep4; label: string }[];

    return (
      <div>
        {/* barra de búsqueda */}
        <div className="mb-4">
          <SearchParameters
            value={searchQuery}
            onChange={setSearchQuery}
            placeholder={`Buscar ${tabStep4}`}
            onNew={handleNewButtonClick}
          />
        </div>

        {/* Si NO es ventanas o puertas, mostramos el + Nuevo arriba a la derecha */}
        {tabStep4 !== "ventanas" && tabStep4 !== "puertas" && (
          <div
            style={{
              display: "flex",
              justifyContent: "flex-end",
              marginBottom: "1rem",
            }}
          ></div>)}

        <HorizontalTabs
          tabs={tabs}
          currentTab={tabStep4}
          onTabChange={(tab) => setTabStep4(tab as TabStep4)}
        />

        <div style={{ height: "400px", position: "relative" }}>
          {tabStep4 === "muros" && renderMurosTable()}
          {tabStep4 === "techumbre" && renderTechumbreTable()}
          {tabStep4 === "pisos" && renderPisosTable()}
          {/* Renderizado de tablas de ventanas y puertas comentado temporalmente
          {tabStep4 === "ventanas" && renderVentanasTable()}
          {tabStep4 === "puertas" && renderPuertasTable()}
          */}
        </div>
      </div>
    );
  };

  // -----------------------------------
  // Render de la sección Recinto (step=7)
  // -----------------------------------
  const renderRecinto = () => {
    return (
      <>
        <div className="d-flex justify-content-between align-items-center mb-3">
          <div></div>
        </div>
        <div className="table-responsive">
          <div style={{ minWidth: '800px' }}>
            <TabRecintDataCreate />
          </div>
        </div>
      </>
    );
  };

  // -----------------------------------
  // Pasos del Sidebar
  // -----------------------------------
  const sidebarSteps = [
    { stepNumber: 4, iconName: "build", title: "3. Detalles constructivos" },
    { stepNumber: 7, iconName: "design_services", title: "4. Recinto" },
    { stepNumber: 8, iconName: "water_drop", title: "5. Agua Caliente Sanitaria" },
    { stepNumber: 6, iconName: "settings", title: "6. Sistemas Activos (equipos)" },
  ];

  // -----------------------------------
  // Componente principal
  // -----------------------------------
  return (
    <>
      <GooIcons />
      <Card>
        <div
          className="d-flex align-items-center w-100"
          style={{ marginBottom: "2rem" }}
        >
          {renderMainHeader()}
        </div>
        <div className="d-flex align-items-center gap-4">
          <ProjectInfoHeader
            projectName={projectName}
            region={projectDepartment}
            project_id={projectId ?? ""}
          />
          <div className="ms-auto" style={{ display: "flex" }}>
            <Breadcrumb
              items={[{ title: "Proyecto Nuevo", href: "/", active: true }]}
            />
          </div>
        </div>
      </Card>

      <Card>
        <div className="row">
          <div className="col-lg-3 col-12 order-lg-first order-first">
            <div className="mb-3 mb-lg-0">
              <AdminSidebar
                activeStep={step}
                onStepChange={setStep}
                steps={sidebarSteps}
              />
            </div>
            <VerticalDivider />
          </div>

          <div className="col-lg-9 col-12 order-last">
            <div style={{ padding: "20px" }}>
              {step === 4 && (
                <>
                  {showTabsInStep4 ? renderStep4Tabs() : renderInitialDetails()}
                </>
              )}
              {step === 8 && (
                <AguaCalienteSanitaria
                  onlyView={isAdmin}
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
              {step === 6 && (
                <div className="mt-3">
                  <React.Suspense fallback={<div>Cargando configuración...</div>}>
                    <ConfiguracionEnergiaTab />
                  </React.Suspense>
                </div>
              )}
              {step === 7 && renderRecinto()}
            </div>
          </div>
        </div>
      </Card>

      {projectId && (
        <ProjectStatus status={projectStatus} projectId={String(projectId)} />
      )}

      {/* 
          MODAL: Edición de Detalle (no-inline).
          Se muestra cuando se hace "Editar" en la tabla de Detalles principal 
      */}
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
              <label>Ubicación Detalle</label>
              <input
                type="text"
                className="form-control"
                value={editingDetail.scantilon_location}
                readOnly
              />
            </div>
            <div className="form-group">
              <label>Nombre Detalle</label>
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
                value={editingDetail.material_id || 0}
                onChange={(e) =>
                  setEditingDetail((prev) =>
                    prev
                      ? { ...prev, material_id: Number(e.target.value) }
                      : prev
                  )
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
                      ? { ...prev, layer_thickness: Number(e.target.value) }
                      : prev
                  )
                }
              />
            </div>
          </form>
        </ModalCreate>
      )}

      {/* 
          MODAL: Edición de Ventana 
      */}
      {editingVentanaForm && (
        <ModalCreate
          isOpen={true}
          title="Editar Ventana"
          detail={editingVentanaForm}
          onClose={() => setEditingVentanaForm(null)}
          onSave={() => handleConfirmVentanaEdit(editingVentanaForm)}
        >
          <form>
            <div className="form-group">
              <label>Nombre Elemento</label>
              <input
                type="text"
                className="form-control"
                value={editingVentanaForm.name_element}
                onChange={(e) =>
                  setEditingVentanaForm((prev) =>
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
                value={editingVentanaForm.atributs?.u_vidrio || ""}
                min="0"
                onKeyDown={(e) => {
                  if (e.key === "-") e.preventDefault();
                }}
                onChange={(e) =>
                  setEditingVentanaForm((prev) =>
                    prev
                      ? {
                        ...prev,
                        atributs: {
                          ...prev.atributs,
                          u_vidrio: Number(e.target.value),
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
                value={editingVentanaForm.atributs?.fs_vidrio || ""}
                min="0"
                onKeyDown={(e) => {
                  if (e.key === "-") e.preventDefault();
                }}
                onChange={(e) =>
                  setEditingVentanaForm((prev) =>
                    prev
                      ? {
                        ...prev,
                        atributs: {
                          ...prev.atributs,
                          fs_vidrio: Number(e.target.value),
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
                value={editingVentanaForm.atributs?.frame_type || ""}
                onChange={(e) =>
                  setEditingVentanaForm((prev) =>
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
                value={editingVentanaForm.atributs?.clousure_type || ""}
                onChange={(e) =>
                  setEditingVentanaForm((prev) =>
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
                value={editingVentanaForm.u_marco || ""}
                min="0"
                onKeyDown={(e) => {
                  if (e.key === "-") e.preventDefault();
                }}
                onChange={(e) =>
                  setEditingVentanaForm((prev) =>
                    prev ? { ...prev, u_marco: Number(e.target.value) } : prev
                  )
                }
              />
            </div>
            <div className="form-group">
              <label>FM [%]</label>
              <input
                type="number"
                min="0"
                max="100"
                step="any"
                className="form-control"
                value={ventanaFmInput}
                onKeyDown={(e) => {
                  if (e.key === "-") e.preventDefault();
                }}
                onChange={(e) => {
                  let val = Number(e.target.value);
                  if (isNaN(val)) {
                    setVentanaFmInput("");
                    return;
                  }
                  if (val > 100) val = 100;
                  if (val < 0) val = 0;
                  setVentanaFmInput(String(val));
                  setEditingVentanaForm((prev) =>
                    prev ? { ...prev, fm: Math.round(val) / 100 } : prev
                  );
                }}
              />
            </div>
          </form>
        </ModalCreate>
      )}

      {/* 
          MODAL: Edición de Puerta 
      */}
      {editingPuertaForm && (
        <ModalCreate
          isOpen={true}
          title="Editar Puerta"
          detail={editingPuertaForm}
          onClose={() => setEditingPuertaForm(null)}
          onSave={() => handleConfirmPuertaEdit(editingPuertaForm)}
        >
          <form>
            <div className="form-group">
              <label>Nombre Elemento</label>
              <input
                type="text"
                className="form-control"
                value={editingPuertaForm.name_element}
                onChange={(e) =>
                  setEditingPuertaForm((prev) =>
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
                value={editingPuertaForm.atributs?.u_puerta_opaca || ""}
                min="0"
                onKeyDown={(e) => {
                  if (e.key === "-") e.preventDefault();
                }}
                onChange={(e) =>
                  setEditingPuertaForm((prev) =>
                    prev
                      ? {
                        ...prev,
                        atributs: {
                          ...prev.atributs,
                          u_puerta_opaca: Number(e.target.value),
                        },
                      }
                      : prev
                  )
                }
              />
            </div>
            <div className="form-group">
              <label>Ventana Asociada</label>
              <input
                type="text"
                className="form-control"
                value={editingPuertaForm.atributs?.name_ventana || ""}
                onChange={(e) =>
                  setEditingPuertaForm((prev) =>
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
                min="0"
                max="100"
                step="any"
                className="form-control"
                value={puertaPorcentajeInput}
                onKeyDown={(e) => {
                  if (e.key === "-") e.preventDefault();
                }}
                onChange={(e) => {
                  let val = Number(e.target.value);
                  if (isNaN(val)) {
                    setPuertaPorcentajeInput("");
                    return;
                  }
                  if (val > 100) val = 100;
                  if (val < 0) val = 0;
                  setPuertaPorcentajeInput(String(val));
                  setEditingPuertaForm((prev) =>
                    prev && prev.atributs
                      ? {
                        ...prev,
                        atributs: {
                          ...prev.atributs,
                          porcentaje_vidrio: Math.round(val) / 100,
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
                value={editingPuertaForm.u_marco || ""}
                min="0"
                onKeyDown={(e) => {
                  if (e.key === "-") e.preventDefault();
                }}
                onChange={(e) =>
                  setEditingPuertaForm((prev) =>
                    prev ? { ...prev, u_marco: Number(e.target.value) } : prev
                  )
                }
              />
            </div>
            <div className="form-group">
              <label>FM [%]</label>
              <input
                type="number"
                min="0"
                max="100"
                step="any"
                className="form-control"
                value={
                  editingPuertaForm.fm
                    ? Math.round(editingPuertaForm.fm * 100)
                    : ""
                }
                onKeyDown={(e) => {
                  if (e.key === "-") e.preventDefault();
                }}
                onChange={(e) => {
                  let val = Number(e.target.value);
                  if (isNaN(val)) {
                    setPuertaPorcentajeInput("");
                    return;
                  }
                  if (val > 100) val = 100;
                  if (val < 0) val = 0;
                  setEditingPuertaForm((prev) =>
                    prev ? { ...prev, fm: Math.round(val) / 100 } : prev
                  );
                }}
              />
            </div>
          </form>
        </ModalCreate>
      )}

      {/* 
          MODAL: Detalles 
          Se abre al dar clic al + en Muros/Techo/Piso (botón "Ver Detalles" AddDetailOnLayer)
      */}
      {showDetallesModal && (
        <ModalCreate
          onSave={() => { }}
          isOpen={true}
          title={`Detalles ${selectedItem?.name_detail || ""}`}
          onClose={() => setShowDetallesModal(false)}
          modalStyle={{ maxWidth: "70%", width: "70%", padding: "32px" }}
          showSaveButton={false}
        >
          {renderDetallesModalContent()}
        </ModalCreate>
      )}

      {/* 
          MODAL: Confirmar borrado 
      */}
      {showConfirmModal && (
        <ModalCreate
          isOpen={true}
          saveLabel="Confirmar"
          title="Confirmar eliminación"
          onClose={() => {
            setShowConfirmModal(false);
            setDeleteAction(null);
          }}
          onSave={() => {
            if (deleteAction) {
              deleteAction();
            }
            setShowConfirmModal(false);
            setDeleteAction(null);
          }}
        >
          <p>¿Está seguro que desea eliminar este elemento?</p>
        </ModalCreate>
      )}

      {/* 
          MODAL: Crear Detalle (cuando le das + Nuevo arriba en la Tab de muros/techumbre/pisos)
          POST /user/[Muro|Techo|Piso]/detail-part-create
      */}
      {showCreateModal && (
        <ModalCreate
          isOpen={true}
          title={`Crear Nuevo ${titleMapping[tabStep4] || "Detalle"}`}
          onClose={() => {
            setShowCreateModal(false);
            setNewDetalle({
              name_detail: "",
              colorExterior: "Intermedio",
              colorInterior: "Intermedio",
              ref_aisl_vertical: {
                lambda: "",
                e_aisl: "",
                d: "",
              },
              ref_aisl_horizontal: {
                lambda: "",
                e_aisl: "",
                d: "",
              },
            });
          }}
          onSave={handleSaveDetalle}
          saveLabel={`Crear ${titleMapping[tabStep4] || "Detalle"}`}
        >
          <form>
            <div className="form-group">
              <label>Nombre <span style={{ color: "red" }}>*</span></label>
              <input
                type="text"
                className="form-control"
                value={newDetalle.name_detail}
                onChange={(e) =>
                  setNewDetalle((prev) => ({
                    ...prev,
                    name_detail: e.target.value,
                  }))
                }
              />
            </div>

            {/* 
                Para pisos pedimos aislamiento vertical/horizontal 
            */}
            {tabStep4 === "pisos" ? (
              <>
                <div className="form-group mt-4">
                  <h6>Aislamiento Vertical</h6>
                  <div className="row">
                    <div className="col-md-4">
                      <label>λ [W/mK]</label>
                      <input
                        type="number"
                        min="0"
                        step="any"
                        className="form-control"
                        value={newDetalle.ref_aisl_vertical.lambda}
                        onKeyDown={(e) => {
                          if (e.key === "-") e.preventDefault();
                        }}
                        onChange={(e) =>
                          setNewDetalle((prev) => ({
                            ...prev,
                            ref_aisl_vertical: {
                              ...prev.ref_aisl_vertical,
                              lambda: e.target.value,
                            },
                          }))
                        }
                      />
                    </div>
                    <div className="col-md-4">
                      <label>e Aisl [cm]</label>
                      <input
                        type="number"
                        min="0"
                        step="any"
                        className="form-control"
                        value={newDetalle.ref_aisl_vertical.e_aisl}
                        onKeyDown={(e) => {
                          if (e.key === "-") e.preventDefault();
                        }}
                        onChange={(e) =>
                          setNewDetalle((prev) => ({
                            ...prev,
                            ref_aisl_vertical: {
                              ...prev.ref_aisl_vertical,
                              e_aisl: e.target.value,
                            },
                          }))
                        }
                      />
                    </div>
                    <div className="col-md-4">
                      <label>D [cm]</label>
                      <input
                        type="number"
                        min="0"
                        step="any"
                        className="form-control"
                        value={newDetalle.ref_aisl_vertical.d}
                        onKeyDown={(e) => {
                          if (e.key === "-") e.preventDefault();
                        }}
                        onChange={(e) =>
                          setNewDetalle((prev) => ({
                            ...prev,
                            ref_aisl_vertical: {
                              ...prev.ref_aisl_vertical,
                              d: e.target.value,
                            },
                          }))
                        }
                      />
                    </div>
                  </div>
                </div>

                <div className="form-group mt-4">
                  <h6>Aislamiento Horizontal</h6>
                  <div className="row">
                    <div className="col-md-4">
                      <label>λ [W/mK]</label>
                      <input
                        type="number"
                        min="0"
                        step="any"
                        className="form-control"
                        value={newDetalle.ref_aisl_horizontal.lambda}
                        onKeyDown={(e) => {
                          if (e.key === "-") e.preventDefault();
                        }}
                        onChange={(e) =>
                          setNewDetalle((prev) => ({
                            ...prev,
                            ref_aisl_horizontal: {
                              ...prev.ref_aisl_horizontal,
                              lambda: e.target.value,
                            },
                          }))
                        }
                      />
                    </div>
                    <div className="col-md-4">
                      <label>e Aisl [cm]</label>
                      <input
                        type="number"
                        min="0"
                        step="any"
                        className="form-control"
                        value={newDetalle.ref_aisl_horizontal.e_aisl}
                        onKeyDown={(e) => {
                          if (e.key === "-") e.preventDefault();
                        }}
                        onChange={(e) =>
                          setNewDetalle((prev) => ({
                            ...prev,
                            ref_aisl_horizontal: {
                              ...prev.ref_aisl_horizontal,
                              e_aisl: e.target.value,
                            },
                          }))
                        }
                      />
                    </div>
                    <div className="col-md-4">
                      <label>D [cm]</label>
                      <input
                        type="number"
                        min="0"
                        step="any"
                        className="form-control"
                        value={newDetalle.ref_aisl_horizontal.d}
                        onKeyDown={(e) => {
                          if (e.key === "-") e.preventDefault();
                        }}
                        onChange={(e) =>
                          setNewDetalle((prev) => ({
                            ...prev,
                            ref_aisl_horizontal: {
                              ...prev.ref_aisl_horizontal,
                              d: e.target.value,
                            },
                          }))
                        }
                      />
                    </div>
                  </div>
                </div>
                {/* Texto de datos obligatorios */}
                <div className="row">
                  <div className="col-12" style={{ textAlign: "left" }}>
                    <p style={{ color: "red", margin: 0 }}>(*) Datos obligatorios</p>
                  </div>
                </div>
              </>
            ) : (
              // Para muros/techumbre pedimos color exterior/interior
              <>
                <div className="form-group">
                  <label>Color Exterior</label>
                  <select
                    className="form-control"
                    value={newDetalle.colorExterior}
                    onChange={(e) =>
                      setNewDetalle((prev) => ({
                        ...prev,
                        colorExterior: e.target.value,
                      }))
                    }
                  >
                    <option value="Claro">Claro</option>
                    <option value="Oscuro">Oscuro</option>
                    <option value="Intermedio">Intermedio</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Color Interior</label>
                  <select
                    className="form-control"
                    value={newDetalle.colorInterior}
                    onChange={(e) =>
                      setNewDetalle((prev) => ({
                        ...prev,
                        colorInterior: e.target.value,
                      }))
                    }
                  >
                    <option value="Claro">Claro</option>
                    <option value="Oscuro">Oscuro</option>
                    <option value="Intermedio">Intermedio</option>
                  </select>
                </div>
              </>
            )}
          </form>
        </ModalCreate>
      )}

      {/* 
          MODAL: Crear Detalle dentro del modal "Detalles" 
          POST /user/detail-create/{detail_part_id}
      */}
      {showNewDetailModal && (
        <ModalCreate
          isOpen={true}
          title="Crear capas  (de Interior a Exterior)"
          saveLabel="Crear Capa"
          onClose={() => setShowNewDetailModal(false)}
          onSave={handleSaveNewDetail}
        >
          <form>
            <div className="form-group">
              <label>Ubicación del Detalle</label>
              <input
                type="text"
                className="form-control"
                value={newDetailData.scantilon_location}
                readOnly
              />
            </div>

            <div className="form-group">
              <label>Nombre de muro</label>
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
                  setNewDetailData((prev) => ({
                    ...prev,
                    material_id: Number(e.target.value),
                  }))
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
                className="form-control"
                placeholder="cm"
                value={
                  newDetailData.layer_thickness > 0
                    ? newDetailData.layer_thickness
                    : ""
                }
                min="0"
                step="any"
                onKeyDown={(e) => {
                  if (e.key === "-") e.preventDefault();
                }}
                onChange={(e) =>
                  setNewDetailData((prev) => ({
                    ...prev,
                    layer_thickness: Number(e.target.value),
                  }))
                }
              />
            </div>
          </form>
        </ModalCreate>
      )}
    </>
  );
};

export default WorkFlowpar2createPage;

