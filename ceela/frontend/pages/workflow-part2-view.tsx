import Breadcrumb from "@/components/common/Breadcrumb";
import HorizontalTabs from "@/components/common/HorizontalTabs";
import AguaCalienteSanitaria from "@/components/projects/tabs/AguaCalienteSanitaria";
import TabRecintDataCreate from "@/components/tab_recint_data/TabRecintDataView";
import { notify } from "@/utils/notify";
import axios from "axios";
import "bootstrap/dist/css/bootstrap.min.css";
import { useRouter } from "next/router";
import React, { useCallback, useEffect, useState } from "react";
import Swal from "sweetalert2";
import GooIcons from "../public/GoogleIcons";
import Title from "../src/components/Title";
import { AdminSidebar } from "../src/components/administration/AdminSidebar";
import Card from "../src/components/common/Card";
import CustomButton from "../src/components/common/CustomButton";
import ModalCreate from "../src/components/common/ModalCreate";
import ProjectInfoHeader from "../src/components/common/ProjectInfoHeader";
import TablesParameters from "../src/components/tables/TablesParameters";
import useAuth from "../src/hooks/useAuth";
import { constantUrlApiEndpoint } from "../src/utils/constant-url-endpoint";
import ConfiguracionEnergiaTab from "@/components/projects/tabs/ConfiguracionEnergiaTab";
import ProjectStatus from "../src/components/projects/ProjectStatus";

/* ==================== TIPOS ==================== */
interface Detail {
  id_detail: number;
  scantilon_location: string;
  name_detail: string;
  id_material: number;
  material: string;
  layer_thickness: number;
  created_status?: string;
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
}

interface Ventana {
  code_ifc?: string;
  id?: number;
  name_element: string;
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
  code_ifc?: string;
  id?: number;
  name_element: string;
  atributs?: {
    u_puerta_opaca?: number;
    name_ventana?: string;
    porcentaje_vidrio?: number;
  };
  u_marco?: number;
  fm?: number;
}

/* Los tabs que corresponden a Step4 */
type TabStep4 =
  | "detalles"
  | "muros"
  | "techumbre"
  | "pisos"
  | "ventanas"
  | "puertas";

/* ==================== HELPERS ==================== */
function getCssVarValue(varName: string, fallback: string) {
  if (typeof window === "undefined") return fallback;
  const value = getComputedStyle(document.documentElement)
    .getPropertyValue(varName)
    .trim();
  return value || fallback;
}

/* ================================================= */
/* ==========  COMPONENTE PRINCIPAL  =============== */
/* ================================================= */
const WorkFlowpar2viewPage: React.FC = () => {
  useAuth();
  const router = useRouter();

  /* ==================== ESTADOS PRINCIPALES ==================== */
  const [projectId, setProjectId] = useState<number | null>(null);
  const [step, setStep] = useState<number>(4);
  const [hasLoaded, setHasLoaded] = useState(false);
  const [projectStatus, setProjectStatus] = useState<string | null>(null);

  /* Detalles generales del modal */
  const [fetchedDetails, setFetchedDetails] = useState<Detail[]>([]);
  const [searchQuery, setSearchQuery] = useState("");

  /* Vista por defecto: tabs (datos constructivos) */
  const [showTabsInStep4, setShowTabsInStep4] = useState(true);
  const [tabStep4, setTabStep4] = useState<TabStep4>("detalles");

  /* Listas para cada tab */
  const [murosTabList, setMurosTabList] = useState<TabItem[]>([]);
  const [techumbreTabList, setTechumbreTabList] = useState<TabItem[]>([]);
  const [pisosTabList, setPisosTabList] = useState<TabItem[]>([]);
  const [ventanasTabList, setVentanasTabList] = useState<Ventana[]>([]);
  const [puertasTabList, setPuertasTabList] = useState<Puerta[]>([]);

  /* Control de color en tabs */
  const primaryColor = getCssVarValue("--primary-color", "#3ca7b7");

  /* Estado para el modal y el id de detail-part seleccionado */
  const [showGeneralDetailsModal, setShowGeneralDetailsModal] = useState(false);
  const [selectedDetailId, setSelectedDetailId] = useState<number | null>(null);

  /* ==================== ESTADOS PARA CABECERA ==================== */
  const [projectName, setProjectName] = useState("");
  const [projectDepartment, setProjectDepartment] = useState("");

  /* Ejemplo de recintos (hardcodeado) */
  const recintos = [
    {
      id: 1,
      estado: "Activo",
      nombre: "Recinto Prueba",
      perfilOcup: "Sedentario",
      sensorCO2: "Si",
      alturaProm: 2.5,
      area: 50,
    },
  ];

  /* ==================== OBTENCIÓN DE projectId y paso ==================== */
  useEffect(() => {
    if (router.isReady) {
      if (router.query.id) {
        setProjectId(Number(router.query.id));
      } else {
        const storedProjectId = localStorage.getItem("project_id");
        if (storedProjectId) {
          setProjectId(Number(storedProjectId));
        }
      }
      if (router.query.step) {
        const stepQuery = parseInt(router.query.step as string, 10);
        if (!isNaN(stepQuery)) {
          setStep(stepQuery);
        }
      }
      setHasLoaded(true);
    }
  }, [router.isReady, router.query.id, router.query.step]);
  
  /* ==================== OBTENER ESTADO DEL PROYECTO ==================== */
  useEffect(() => {
    const fetchProjectStatus = async () => {
      if (!projectId) return;
      
      try {
        const token = localStorage.getItem("token");
        if (!token) {
          console.warn("Token no encontrado");
          return;
        }
        
        const { data: projectData } = await axios.get(
          `${constantUrlApiEndpoint}/projects/${projectId}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        
        if (projectData && projectData.status) {
          setProjectStatus(projectData.status);
        }
      } catch (error) {
        console.error("Error al obtener el estado del proyecto:", error);
      }
    };
    
    fetchProjectStatus();
  }, [projectId]);

  /* ==================== OBTENER DATOS DEL LOCAL STORAGE PARA CABECERA ==================== */
  useEffect(() => {
    const name = localStorage.getItem("project_name_view") || "";
    const department = localStorage.getItem("project_department_view") || "";
    setProjectName(name);
    setProjectDepartment(department);
  }, []);

  /* ==================== REDIRECCIÓN SI NO HAY projectId ==================== */
  useEffect(() => {
    if (hasLoaded && projectId === null) {
      Swal.fire(
        "Ningún proyecto está seleccionado",
        "Serás redirigido a la creación de proyecto",
        "warning"
      ).then(() => {
        router.push("/workflow-part1-view");
      });
    }
  }, [hasLoaded, projectId, router]);

  /* =============================================================== */
  /* ================  LLAMADAS A ENDPOINTS  ======================== */
  /* =============================================================== */

  /* ---------- Nuevo endpoint /detail-part/{detail_part_id} ---------- */
  const fetchDetailPart = async (detailPartId: number) => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        Swal.fire("Token no encontrado", "Inicia sesión.");
        return;
      }
      const url = `${constantUrlApiEndpoint}/detail-part/${detailPartId}`;
      const headers = { Authorization: `Bearer ${token}` };
      const response = await axios.get(url, { headers });
      /* La API devuelve un array según el ejemplo, así que guardamos tal cual */
      setFetchedDetails(response.data || []);
    } catch (error: unknown) {
      console.error("Error al obtener detalle-part:", error);
      if (axios.isAxiosError(error)) {
        console.error("Status:", error.response?.status);
        console.error("Response:", error.response?.data);
      }
      Swal.fire("Error", "Error al obtener detalles del elemento.");
    }
  };

  /* ---------------- Endpoints existentes para cada tab ---------------- */
  const fetchMurosDetails = useCallback(async () => {
    if (!projectId) return;
    const token = localStorage.getItem("token");
    if (!token) {
      Swal.fire("Token no encontrado", "Inicia sesión.");
      return;
    }
    try {
      const url = `${constantUrlApiEndpoint}/admin/project/${projectId}/details/Muro`;
      const headers = { Authorization: `Bearer ${token}` };
      const response = await axios.get(url, { headers });
      setMurosTabList(response.data);
    } catch (error) {
      console.error("Error al obtener datos de muros:", error);
    }
  }, [projectId]);

  const fetchTechumbreDetails = useCallback(async () => {
    if (!projectId) return;
    const token = localStorage.getItem("token");
    if (!token) {
      Swal.fire("Token no encontrado", "Inicia sesión.");
      return;
    }
    try {
      const url = `${constantUrlApiEndpoint}/admin/project/${projectId}/details/Techo`;
      const headers = { Authorization: `Bearer ${token}` };
      const response = await axios.get(url, { headers });
      setTechumbreTabList(response.data);
    } catch (error: unknown) {
      console.error("Error al obtener datos de techo:", error);
    }
  }, [projectId]);

  const fetchPisosDetails = useCallback(async () => {
    if (!projectId) return;
    const token = localStorage.getItem("token");
    if (!token) {
      Swal.fire("Token no encontrado", "Inicia sesión.");
      return;
    }
    try {
      const url = `${constantUrlApiEndpoint}/admin/project/${projectId}/details/Piso`;
      const headers = { Authorization: `Bearer ${token}` };
      const response = await axios.get(url, { headers });
      setPisosTabList(response.data);
    } catch (error: unknown) {
      console.error("Error al obtener datos de piso:", error);
    }
  }, [projectId]);

  const fetchVentanasDetails = useCallback(async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      Swal.fire("Token no encontrado", "Inicia sesión.");
      return;
    }
    try {
      const url = `${constantUrlApiEndpoint}/user/elements/?type=window`;
      const headers = { Authorization: `Bearer ${token}` };
      const response = await axios.get(url, { headers });
      setVentanasTabList(response.data);
    } catch (error: unknown) {
      console.error("Error al obtener datos de ventanas:", error);
      notify("Error al obtener datos de Ventanas. Ver consola.");
    }
  }, []);

  const fetchPuertasDetails = useCallback(async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      Swal.fire("Token no encontrado", "Inicia sesión.");
      return;
    }
    try {
      const url = `${constantUrlApiEndpoint}/user/elements/?type=door`;
      const headers = { Authorization: `Bearer ${token}` };
      const response = await axios.get(url, { headers });
      setPuertasTabList(response.data);
    } catch (error: unknown) {
      console.error("Error al obtener datos de puertas:", error);
      notify("Error al obtener datos de Puertas. Ver consola.");
    }
  }, []);

  /* ==================== EFECTO PARA DETAIL-PART ==================== */
  useEffect(() => {
    if (showGeneralDetailsModal && selectedDetailId !== null) {
      fetchDetailPart(selectedDetailId);
    }
  }, [showGeneralDetailsModal, selectedDetailId]);

  /* ==================== EFECTOS SEGÚN STEP ==================== */
  useEffect(() => {
    if (step === 4 && projectId !== null) {
      // Posible lógica al iniciar step 4
    }
  }, [step, projectId]);

  useEffect(() => {
    if (showTabsInStep4) {
      /* "muros" por defecto */
      setTabStep4("muros");
    }
  }, [showTabsInStep4]);

  useEffect(() => {
    if (showTabsInStep4) {
      if (tabStep4 === "muros") {
        fetchMurosDetails();
      } else if (tabStep4 === "techumbre") {
        fetchTechumbreDetails();
      } else if (tabStep4 === "pisos") {
        fetchPisosDetails();
      } else if (tabStep4 === "ventanas") {
        fetchVentanasDetails();
      } else if (tabStep4 === "puertas") {
        fetchPuertasDetails();
      }
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

  /* =============================================================== */
  /* ================    RENDER CABECERA      ====================== */
  /* =============================================================== */
  const renderMainHeader = () =>
    step >= 4 && <Title text="Vista de Desarrollo de proyecto" />;

  /* =============================================================== */
  /* =====      HELPERS PARA BOTÓN LAYERS (abrir modal)         ==== */
  /* =============================================================== */
  const handleOpenLayersModal = (detailId: number | undefined | null) => {
    if (!detailId) {
      Swal.fire("Error", "No se encontró el ID del detalle.");
      return;
    }
    setSelectedDetailId(detailId);
    setShowGeneralDetailsModal(true);
  };

  /* =============================================================== */
  /* ================  RENDER DE TABLAS (MUROS, ETC.) ============== */
  /* =============================================================== */

  const renderMurosTable = () => {
    const columnsMuros = [
      { headerName: "Nombre Abreviado", field: "name_detail" },
      { headerName: "Valor U (W/m²K)", field: "valorU" },
      { headerName: "Color Exterior", field: "colorExterior" },
      { headerName: "Color Interior", field: "colorInterior" },
      {
        headerName: "Acciones",
        field: "actions",
        renderCell: (row: any) => (
          <CustomButton
            variant="layersIcon"
            onClick={() => handleOpenLayersModal(row.id_detail ?? row.id)}
          />
        ),
      },
    ];

    const murosData = murosTabList.map((item) => ({
      code_ifc: item.code_ifc || "-",

      id_detail: item.id_detail ?? item.id, // necesario para obtener el id
      name_detail: item.name_detail,
      valorU: item.value_u?.toFixed(2) ?? "-",
      colorExterior: item.info?.surface_color?.exterior?.name || "Desconocido",
      colorInterior: item.info?.surface_color?.interior?.name || "Desconocido",
    }));

    return murosTabList.length > 0 ? (
      <TablesParameters columns={columnsMuros} data={murosData} />
    ) : (
      <p>No hay datos</p>
    );
  };

  const renderTechumbreTable = () => {
    const columnsTechumbre = [
      {
        headerName: "Código IFC",
        field: "code_ifc",
      },
      { headerName: "Nombre Abreviado", field: "name_detail" },
      { headerName: "Valor U (W/m²K)", field: "valorU" },
      { headerName: "Color Exterior", field: "colorExterior" },
      { headerName: "Color Interior", field: "colorInterior" },
      {
        headerName: "Acciones",
        field: "actions",
        renderCell: (row: any) => (
          <CustomButton
            variant="layersIcon"
            onClick={() => handleOpenLayersModal(row.id_detail ?? row.id)}
          />
        ),
      },
    ];

    const techData = techumbreTabList.map((item) => ({
      code_ifc: item.code_ifc || "-",

      id_detail: item.id_detail ?? item.id,
      name_detail: item.name_detail,
      valorU: item.value_u?.toFixed(2) ?? "-",
      colorExterior: item.info?.surface_color?.exterior?.name || "Desconocido",
      colorInterior: item.info?.surface_color?.interior?.name || "Desconocido",
    }));

    return techumbreTabList.length > 0 ? (
      <TablesParameters columns={columnsTechumbre} data={techData} />
    ) : (
      <p>No hay datos</p>
    );
  };

  const renderPisosTable = () => {
    /* Helper para formatear valores */
    const formatValue = (value: any, fixed?: number): string => {
      if (value === undefined || value === null || value === 0) {
        return "-";
      }
      if (typeof value === "number" && fixed !== undefined) {
        return value.toFixed(fixed);
      }
      return value.toString();
    };

    const columnsPisos = [
      {
        headerName: "Código IFC",
        field: "code_ifc",
      },
      { headerName: "Nombre", field: "nombre" },
      { headerName: "U [W/m²K]", field: "uValue" },
      { headerName: "I [W/mK] (bajo piso)", field: "bajoPisoLambda" },
      { headerName: "e Aisl [cm]", field: "bajoPisoEAisl" },
      { headerName: "I [W/mK] (vert)", field: "vertLambda" },
      { headerName: "e Aisl [cm]", field: "vertEAisl" },
      { headerName: "D [cm]", field: "vertD" },
      { headerName: "I [W/mK] (horiz)", field: "horizLambda" },
      { headerName: "e Aisl [cm]", field: "horizEAisl" },
      { headerName: "D [cm]", field: "horizD" },
      {
        headerName: "Acciones",
        field: "actions",
        renderCell: (row: any) => (
          <CustomButton
            variant="layersIcon"
            onClick={() => handleOpenLayersModal(row.id_detail ?? row.id)}
          />
        ),
      },
    ];

    const multiHeaderPisos = {
      rows: [
        [
          { label: "Código ICF", rowSpan: 2 },
          { label: "Nombre", rowSpan: 2 },
          { label: "U [W/m²K]", rowSpan: 2 },
          { label: "Aislamiento bajo piso", colSpan: 2 },
          { label: "Ref Aisl Vert.", colSpan: 3 },
          { label: "Ref Aisl Horiz.", colSpan: 3 },
        ],
        [
          { label: "I [W/mK]" },
          { label: "e Aisl [cm]" },
          { label: "I [W/mK]" },
          { label: "e Aisl [cm]" },
          { label: "D [cm]" },
          { label: "I [W/mK]" },
          { label: "e Aisl [cm]" },
          { label: "D [cm]" },
        ],
      ],
    };

    const pisosData = pisosTabList.map((item) => {
      const bajoPiso = item.info?.aislacion_bajo_piso || {};
      const vert = item.info?.ref_aisl_vertical || {};
      const horiz = item.info?.ref_aisl_horizontal || {};
      return {
        code_ifc: item.code_ifc || "-",
        id_detail: item.id_detail ?? item.id,
        nombre: item.name_detail,
        uValue: formatValue(item.value_u, 2),
        bajoPisoLambda: formatValue(bajoPiso.lambda, 2),
        bajoPisoEAisl: formatValue(bajoPiso.e_aisl),
        vertLambda: formatValue(vert.lambda, 2),
        vertEAisl: formatValue(vert.e_aisl),
        vertD: formatValue(vert.d),
        horizLambda: formatValue(horiz.lambda, 2),
        horizEAisl: formatValue(horiz.e_aisl),
        horizD: formatValue(horiz.d),
      };
    });

    return (
      <div style={{ minWidth: "600px" }}>
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

  /* Ventanas y puertas no usan modal, así que sin botón */
  const renderVentanasTable = () => {
    const columnsVentanas = [
      {
        headerName: "Código IFC",
        field: "code_ifc",
      },
      { headerName: "Nombre Elemento", field: "name_element" },
      { headerName: "U Vidrio [W/m²K]", field: "u_vidrio" },
      { headerName: "FS Vidrio []", field: "fs_vidrio" },
      { headerName: "Tipo Marco", field: "frame_type" },
      { headerName: "Tipo Cierre", field: "clousure_type" },
      { headerName: "U Marco [W/m²K]", field: "u_marco" },
      { headerName: "FV [%]", field: "fm" },
    ];

    const ventanasData = ventanasTabList.map((item) => {
      if ((item as any).created_status === "created") {
        return {
          code_ifc: item.code_ifc || "-",
          name_element: (
            <span style={{ color: "var(--primary-color)", fontWeight: "bold" }}>
              {item.name_element}
            </span>
          ),
          u_vidrio: item.atributs?.u_vidrio ? (
            <span style={{ color: "var(--primary-color)", fontWeight: "bold" }}>
              {item.atributs.u_vidrio.toFixed(2)}
            </span>
          ) : (
            "--"
          ),
          fs_vidrio: item.atributs?.fs_vidrio ? (
            <span style={{ color: "var(--primary-color)", fontWeight: "bold" }}>
              {Number(item.atributs.fs_vidrio).toFixed(2)}
            </span>
          ) : (
            "--"
          ),
          frame_type: item.atributs?.frame_type ? (
            <span style={{ color: "var(--primary-color)", fontWeight: "bold" }}>
              {item.atributs.frame_type}
            </span>
          ) : (
            "--"
          ),
          clousure_type: item.atributs?.clousure_type ? (
            <span style={{ color: "var(--primary-color)", fontWeight: "bold" }}>
              {item.atributs.clousure_type}
            </span>
          ) : (
            "--"
          ),
          u_marco: item.u_marco ? (
            <span style={{ color: "var(--primary-color)", fontWeight: "bold" }}>
              {item.u_marco.toFixed(2)}
            </span>
          ) : (
            "--"
          ),
          fm: item.fm ? (
            <span style={{ color: "var(--primary-color)", fontWeight: "bold" }}>
              {(item.fm * 100).toFixed(2)}
            </span>
          ) : (
            "--"
          ),
        };
      } else {
        return {
          code_ifc: item.code_ifc || "-",
          name_element: item.name_element,
          u_vidrio: item.atributs?.u_vidrio
            ? item.atributs.u_vidrio.toFixed(2)
            : "--",
          fs_vidrio: item.atributs?.fs_vidrio
            ? Number(item.atributs.fs_vidrio).toFixed(2)
            : "--",
          frame_type: item.atributs?.frame_type ?? "--",
          clousure_type: item.atributs?.clousure_type ?? "--",
          u_marco: item.u_marco ? item.u_marco.toFixed(2) : "--",
          fm: item.fm ? (item.fm * 100).toFixed(2) : "--",
        };
      }
    });

    return ventanasTabList.length > 0 ? (
      <TablesParameters columns={columnsVentanas} data={ventanasData} />
    ) : (
      <p>No hay datos</p>
    );
  };

  const renderPuertasTable = () => {
    const columnsPuertas = [
      {
        headerName: "Código IFC",
        field: "code_ifc",
      },
      { headerName: "Nombre Elemento", field: "name_element" },
      { headerName: "U puerta opaca [W/m²K]", field: "u_puerta" },
      { headerName: "Vidrio []", field: "name_ventana" },
      { headerName: "% vidrio", field: "porcentaje_vidrio" },
      { headerName: "U Marco [W/m²K]", field: "u_marco" },
      { headerName: "FM [%]", field: "fm" },
    ];

    const puertasData = puertasTabList.map((item) => {
      if ((item as any).created_status === "created") {
        return {
          code_ifc: item.code_ifc || "-",

          name_element: (
            <span style={{ color: "var(--primary-color)", fontWeight: "bold" }}>
              {item.name_element}
            </span>
          ),
          u_puerta: item.atributs?.u_puerta_opaca ? (
            <span style={{ color: "var(--primary-color)", fontWeight: "bold" }}>
              {item.atributs.u_puerta_opaca.toFixed(2)}
            </span>
          ) : (
            "--"
          ),
          name_ventana: item.atributs?.name_ventana ? (
            <span style={{ color: "var(--primary-color)", fontWeight: "bold" }}>
              {item.atributs.name_ventana}
            </span>
          ) : (
            "--"
          ),
          porcentaje_vidrio: item.atributs?.porcentaje_vidrio ? (
            <span style={{ color: "var(--primary-color)", fontWeight: "bold" }}>
              {(item.atributs.porcentaje_vidrio * 100).toFixed(2)}
            </span>
          ) : (
            "--"
          ),
          u_marco: item.u_marco ? (
            <span style={{ color: "var(--primary-color)", fontWeight: "bold" }}>
              {item.u_marco.toFixed(2)}
            </span>
          ) : (
            "--"
          ),
          fm: item.fm ? (
            <span style={{ color: "var(--primary-color)", fontWeight: "bold" }}>
              {(item.fm * 100).toFixed(2)}
            </span>
          ) : (
            "--"
          ),
        };
      } else {
        return {
          code_ifc: item.code_ifc || "-",
          name_element: item.name_element,
          u_puerta: item.atributs?.u_puerta_opaca
            ? item.atributs.u_puerta_opaca.toFixed(2)
            : "--",
          name_ventana: item.atributs?.name_ventana ?? "--",
          porcentaje_vidrio: item.atributs?.porcentaje_vidrio
            ? (item.atributs.porcentaje_vidrio * 100).toFixed(2)
            : "--",
          u_marco: item.u_marco ? item.u_marco.toFixed(2) : "--",
          fm: item.fm ? (item.fm * 100).toFixed(2) : "--",
        };
      }
    });

    return puertasTabList.length > 0 ? (
      <TablesParameters columns={columnsPuertas} data={puertasData} />
    ) : (
      <p>No hay datos</p>
    );
  };

  /* =============================================================== */
  /* ================  RENDER PESTAÑAS STEP 4 ====================== */
  /* =============================================================== */
  const renderStep4Tabs = () => {
    if (!showTabsInStep4) return null;
    const tabs = [
      { key: "muros", label: "Muros" },
      { key: "techumbre", label: "Techumbre" },
      { key: "pisos", label: "Pisos" },
      { key: "ventanas", label: "Ventanas" },
      { key: "puertas", label: "Puertas" },
    ] as { key: TabStep4; label: string }[]; return (
      <div className="mt-4">
        <HorizontalTabs
          tabs={tabs}
          currentTab={tabStep4}
          onTabChange={(tab) => setTabStep4(tab as TabStep4)}
        />

        <div
          style={{
            height:
              tabStep4 === "ventanas" || tabStep4 === "puertas"
                ? "auto"
                : "400px",
            overflowY:
              tabStep4 === "ventanas" || tabStep4 === "puertas"
                ? "hidden"
                : "auto",
            position: "relative",
            cursor:
              tabStep4 !== "puertas" && tabStep4 !== "ventanas"
                ? "pointer"
                : "default",
          }}
          onClick={
            tabStep4 !== "puertas" && tabStep4 !== "ventanas"
              ? undefined /* se abre con el botón ahora */
              : undefined
          }
        >
          {tabStep4 === "muros" && (
            <div style={{ overflowX: "auto" }}>{renderMurosTable()}</div>
          )}
          {tabStep4 === "techumbre" && (
            <div style={{ overflowX: "auto" }}>{renderTechumbreTable()}</div>
          )}
          {tabStep4 === "pisos" && (
            <div style={{ overflowX: "auto" }}>{renderPisosTable()}</div>
          )}
          {tabStep4 === "ventanas" && (
            <div style={{ overflowX: "auto" }}>{renderVentanasTable()}</div>
          )}
          {tabStep4 === "puertas" && (
            <div style={{ overflowX: "auto" }}>{renderPuertasTable()}</div>
          )}
        </div>
      </div>
    );
  };

  /* =============================================================== */
  /* =========   CONTENIDO DEL MODAL (Detalles Generales)   ========= */
  /* =============================================================== */
  const renderGeneralDetailsContent = () => {
    /* Filtra según la pestaña activa y búsqueda */
    const filteredDetails = fetchedDetails.filter((det) => {
      let typeMatch = false;
      const location = det.scantilon_location.toLowerCase();

      if (tabStep4 === "muros") {
        typeMatch = location === "muro";
      } else if (tabStep4 === "techumbre") {
        typeMatch = location === "techo" || location === "techumbre";
      } else if (tabStep4 === "pisos") {
        typeMatch = location === "piso";
      }

      const searchLower = searchQuery.toLowerCase();
      const searchMatch =
        det.scantilon_location.toLowerCase().includes(searchLower) ||
        det.name_detail.toLowerCase().includes(searchLower) ||
        det.material.toLowerCase().includes(searchLower) ||
        det.layer_thickness.toString().includes(searchLower);

      return typeMatch && searchMatch;
    });

    /* Mapeo para colorear filas creadas */
    const detailsData = filteredDetails.map((det) => {
      if (det.created_status === "created") {
        return {
          ...det,
          scantilon_location: (
            <span style={{ color: "var(--primary-color)", fontWeight: "bold" }}>
              {det.scantilon_location}
            </span>
          ),
          name_detail: (
            <span style={{ color: "var(--primary-color)", fontWeight: "bold" }}>
              {det.name_detail}
            </span>
          ),
          material: (
            <span style={{ color: "var(--primary-color)", fontWeight: "bold" }}>
              {det.material}
            </span>
          ),
          layer_thickness: (
            <span style={{ color: "var(--primary-color)", fontWeight: "bold" }}>
              {det.layer_thickness}
            </span>
          ),
        };
      } else {
        return det;
      }
    });

    return (
      <div className="mb-3">
        <div style={{ height: "400px", overflowY: "scroll" }}>
          <TablesParameters
            columns={[
              { headerName: "Nombre Detalle", field: "name_detail" },
              { headerName: "Material", field: "material" },
              { headerName: "Espesor capa (cm)", field: "layer_thickness" },
            ]}
            data={detailsData}
          />
        </div>
      </div>
    );
  };

  /* =============================================================== */
  /* ==================== RENDER RECINTO =========================== */
  /* =============================================================== */
  const renderRecinto = () => (
    <>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <div></div>
      </div>
      <TabRecintDataCreate />
    </>
  );

  /* =============================================================== */
  /* ==================== PASOS / SIDEBAR ========================== */
  /* =============================================================== */
  const sidebarSteps = [
    {
      stepNumber: 1,
      iconName: "assignment_ind",
      title:
        "1. Agregar detalles de propietario / proyecto y clasificación de edificaciones",
      route: `/workflow-part1-view?id=${projectId}&step=1`,
    },
    {
      stepNumber: 2,
      iconName: "location_on",
      title: "2. Ubicación del proyecto",
      route: `/workflow-part1-view?id=${projectId}&step=2`,
    },
    {
      stepNumber: 4,
      iconName: "build",
      title: "3. Detalles constructivos",
      route: `/workflow-part2-view?id=${projectId}&step=4`,
    },
    {
      stepNumber: 7,
      iconName: "design_services",
      title: "4. Recinto",
      route: `/workflow-part2-view?id=${projectId}&step=7`,
    },
    {
      stepNumber: 8,
      iconName: "water_drop",
      title: "5. Agua Caliente Sanitaria",
      route: `/workflow-part2-view?id=${projectId}&step=8`,
    },
    {
      stepNumber: 6,
      iconName: "settings",
      title: "6. Configuración",
      route: `/workflow-part2-view?id=${projectId}&step=6`,
    },
  ];

  /* =============================================================== */
  /* ========================  RETURN ============================== */
  /* =============================================================== */
  return (
    <>
      <GooIcons />
      <div>
        <Card>
          <h3>{renderMainHeader()}</h3>
          <div
            style={{
              width: "100%",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
            <div style={{ pointerEvents: 'none' }}>
              <ProjectInfoHeader
                projectName={projectName}
                region={projectDepartment}
              />
            </div>
            <Breadcrumb
              items={[
                {
                  title: "Vista De Proyecto",
                  href: "/",
                  active: true,
                },
              ]}
            />
          </div>
        </Card>

        <Card>
          <div className="row">
            <div className="col-12 col-md-3">
              <AdminSidebar
                activeStep={step}
                steps={sidebarSteps}
                onClickAction={(route: string) => router.push(route)}
                onStepChange={() => { }}
              />
            </div>

            <div className="col-12 col-md-9 p-4">
              {step === 4 && showTabsInStep4 && renderStep4Tabs()}
              {step === 7 && renderRecinto()}
              {step === 8 && <AguaCalienteSanitaria onlyView={true} />}
              {step === 6 && (
                <div className="mt-3">
                  <React.Suspense fallback={<div>Cargando configuración...</div>}>
                    <ConfiguracionEnergiaTab />
                  </React.Suspense>
                </div>
              )}
            </div>
          </div>
        </Card>
      </div>
      {projectStatus && (
        <ProjectStatus
          status={projectStatus}
          projectId={projectId?.toString() || ""}
        />
      )}

      {/* Modal para detalles generales */}
      <ModalCreate
        detail=""
        isOpen={showGeneralDetailsModal}
        onClose={() => setShowGeneralDetailsModal(false)}
        onSave={() => { }}
        title="Detalles Generales"
        hideFooter={true}
        modalStyle={{
          maxWidth: "70%",
          width: "70%",
          padding: "32px",
        }}
      >
        {renderGeneralDetailsContent()}
      </ModalCreate>
    </>
  );
};

export default WorkFlowpar2viewPage;
