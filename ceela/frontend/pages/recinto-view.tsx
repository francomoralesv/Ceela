import React, { useEffect, useState } from "react";
import TablesParameters from "@/components/tables/TablesParameters";
import Card from "../src/components/common/Card";
import { constantUrlApiEndpoint } from "@/utils/constant-url-endpoint";
import Breadcrumb from "@/components/common/Breadcrumb";
import Title from "../src/components/Title";
import ProjectInfoHeader from "@/components/common/ProjectInfoHeader";

interface Muro {
  id: number;
  name: string;
  area: number;
  orientation: string;
  angulo_azimut: string;
  characteristics: string;
  u?: number;
}

interface Ventana {
  alojado_en: string;
  id: number;
  window_name: string;
  position: string;
  orientation: string;
  angulo_azimut: string;
  characteristics?: string;
  housed_in?: number | string;
  clousure_type?: string;
  with_no_return?: string;
  high?: number | string;
  broad?: number | string;
  frame?: string;
  fav1_D?: any;
  fav1_L?: any;
  fav2izq_P?: any;
  fav2izq_S?: any;
  fav2der_P?: any;
  fav2der_S?: any;
  fav3_E?: any;
  fav3_T?: any;
  fav3_beta?: any;
  fav3_alpha?: any;
  acciones?: string;
  acciones_fav?: string;
}

interface Puerta {
  id: number;
  orientation: string;
  anguloAzimut: string;
}

interface FloorData {
  id: number;
  index: number;
  pisos: string;
  floor_id: number;
  caracteristicas: string;
  area: number;
  uValue: number;
  perimetroSuelo: number;
  pisoVentilado: string;
  ptP06L: number;
}

type Techumbre = any[];

interface RoofData {
  id: number;
  techos: string;
  caracteristicas: string;
  area: number;
  u: number;
}

interface PuenteTermico {
  id: number;
  enclosure_id: number;
  wall_id: number;
  po1_length: number;
  po2_length: number;
  po3_length: number;
  po4_length: number;
  po1_id_element: number;
  po2_id_element: number;
  po3_id_element: number;
  po4_id_element: number;
  po4_e_aislacion: number;
  po1_element_name: string | null;
  po2_element_name: string | null;
  po3_element_name: string | null;
  po4_element_name: string | null;
}

interface DoorData {
  id: number;
  door_id: number;
  tipoPuente: string;
  characteristics: string;
  anguloAzimut: string;
  orientacion: string;
  high: number;
  broad: number;
  fav1D: number;
  fav1L: number;
  fav2izqP: number;
  fav2izqS: number;
  fav2DerP: number;
  fav2DerS: number;
  fav3E: number;
  fav3T: number;
  fav3Beta: number;
  fav3Alpha: number;
  fav_id: number | null;
}

// Actualización de la interfaz para obstrucciones
interface ObstructionsData {
  id: number;
  division_id: number | null;
  index: number;
  división: string;
  floor_id: number;
  b: number;
  a: number;
  d: number;
  anguloAzimut: string;
  orientación: any;
  obstrucción: number;
  mainRow: boolean;
}

const HeaderVistaDesarrollo: React.FC = () => {
  const [projectName, setProjectName] = useState("");
  const [projectDepartment, setProjectDepartment] = useState("");

  useEffect(() => {
    const name = localStorage.getItem("project_name_view") || "";
    const department = localStorage.getItem("project_department_view") || "";
    setProjectName(name);
    setProjectDepartment(department);
  }, []);

  return (
    <Card>
      <div style={{ marginTop: "10px" }}>
        <h3>
          <Title text="Vista de Desarrollo de proyecto" />
        </h3>
      </div>
      <div
        style={{
          width: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <ProjectInfoHeader projectName={projectName} region={projectDepartment} />
        <Breadcrumb
          items={[
            {
              title: "Vista recintos",
              href: "/",
              active: true,
            },
          ]}
        />
      </div>
    </Card>
  );
};

const RecintoView: React.FC = () => {
  const [walls, setWalls] = useState<Muro[]>([]);
  const [windows, setWindows] = useState<Ventana[]>([]);
  const [doorTableData, setDoorTableData] = useState<DoorData[]>([]);
  const [roofData, setRoofData] = useState<RoofData[]>([]);
  const [thermalBridges, setThermalBridges] = useState<PuenteTermico[]>([]);
  const [angleOptions, setAngleOptions] = useState<string[]>([]);
  const [doorOptions, setDoorOptions] = useState<any[]>([]);
  const [activeWallTab, setActiveWallTab] = useState<"muros" | "puentes">("muros");
  const [floorTableData, setFloorTableData] = useState<FloorData[]>([]);
  
  // Nuevas variables para la tabla de obstrucciones
  const [obstructionsData, setObstructionsData] = useState<ObstructionsData[]>([]);
  const [obstructionsLoading, setObstructionsLoading] = useState<boolean>(false);

  // Definición de columnas para la tabla de muros
  const murosColumns = [
    { headerName: "Muros", field: "name" },
    { headerName: "Caracteristicas", field: "characteristics" },
    { headerName: "Orientación", field: "orientation" },
    {
      headerName: "Área [m²]",
      field: "area",
      renderCell: (row: any) => formatCellValue(row.area, 2),
    },
    {
      headerName: "U [W/m²K]",
      field: "u",
      renderCell: (row: any) => formatCellValue(row.u, 2),
    },
  ];

  const puentesColumns = [
    {
      headerName: "L[m]",
      field: "po1_length",
      renderCell: (row: any) => formatCellValue(row.po1_length, 2),
    },
    {
      headerName: "Elemento",
      field: "po1_element_name",
      renderCell: (row: any) => formatCellValue(row.po1_element_name),
    },
    {
      headerName: "L[m]",
      field: "po2_length",
      renderCell: (row: any) => formatCellValue(row.po2_length, 2),
    },
    {
      headerName: "Elemento",
      field: "po2_element_name",
      renderCell: (row: any) => formatCellValue(row.po2_element_name, 2),
    },
    {
      headerName: "L[m]",
      field: "po3_length",
      renderCell: (row: any) => formatCellValue(row.po3_length, 2),
    },
    {
      headerName: "Elemento",
      field: "po3_element_name",
      renderCell: (row: any) => formatCellValue(row.po3_element_name, 2),
    },
    {
      headerName: "L[m]",
      field: "po4_length",
      renderCell: (row: any) => formatCellValue(row.po4_length, 2),
    },
    {
      headerName: "e Aislación [cm]",
      field: "po4_e_aislacion",
      renderCell: (row: any) => formatCellValue(row.po4_e_aislacion, 2),
    },
    {
      headerName: "Elemento",
      field: "po4_element_name",
      renderCell: (row: any) => formatCellValue(row.po4_element_name, 2),
    },
  ];

  const mergedColumns = [...murosColumns, ...puentesColumns];

  const mergedMultiHeader = {
    rows: [
      [
        ...[
          { label: "Muros" },
          { label: "Características espacio contiguo al elemento" },
          { label: "Orientación" },
          { label: "Área[m²]" },
          { label: "U [W/m²K]" },
        ],
        ...[
          { label: (<><span>P01</span><br /><span>L[m]</span></>) },
          { label: (<><span>P01</span><br /><span>Elemento</span></>) },
          { label: (<><span>P02</span><br /><span>L[m]</span></>) },
          { label: (<><span>P02</span><br /><span>Elemento</span></>) },
          { label: (<><span>P03</span><br /><span>L[m]</span></>) },
          { label: (<><span>P03</span><br /><span>Elemento</span></>) },
          { label: (<><span>P04</span><br /><span>L[m]</span></>) },
          { label: (<><span>P04</span><br /><span>e Aislación [cm]</span></>) },
          { label: (<><span>P04</span><br /><span>Elemento</span></>) },
        ],
      ],
    ],
  };

  // Definición de columnas para la tabla de ventanas
  const ventanaColumns = [
    { headerName: "Tipo de vano Acristalado (incluye marco)", field: "tipoVano" },
    { headerName: "Características espacio contiguo al elemento", field: "caracteristicas" },
    { headerName: "Orientación", field: "orientacion" },
    { headerName: "Alojado en", field: "alojadoEn" },
    { headerName: "Tipo de Cierre", field: "tipoCierre" },
    { headerName: "Posición Ventanal", field: "posicionVentanal" },
    { headerName: "Aislación Con/sin retorno", field: "aislacion" },
    {
      headerName: "Alto (H) [m]",
      field: "alto",
      renderCell: (row: any) => formatCellValue(row.alto, 2),
    },
    {
      headerName: "Ancho (W) [m]",
      field: "ancho",
      renderCell: (row: any) => formatCellValue(row.ancho, 2),
    },
    {
      headerName: "Marco",
      field: "marco",
      renderCell: (row: any) => formatCellValue(row.marco, 2),
    },
    {
      headerName: "FAV 1 - D [m]",
      field: "fav1_D",
      renderCell: (row: any) => formatCellValue(row.fav1_D, 2),
    },
    {
      headerName: "FAV 1 - L [m]",
      field: "fav1_L",
      renderCell: (row: any) => formatCellValue(row.fav1_L, 2),
    },
    {
      headerName: "FAV 2 izq - P [m]",
      field: "fav2izq_P",
      renderCell: (row: any) => formatCellValue(row.fav2izq_P, 2),
    },
    {
      headerName: "FAV 2 izq - S [m]",
      field: "fav2izq_S",
      renderCell: (row: any) => formatCellValue(row.fav2izq_S, 2),
    },
    {
      headerName: "FAV 2 Der - P [m]",
      field: "fav2der_P",
      renderCell: (row: any) => formatCellValue(row.fav2der_P, 2),
    },
    {
      headerName: "FAV 2 Der - S [m]",
      field: "fav2der_S",
      renderCell: (row: any) => formatCellValue(row.fav2der_S, 2),
    },
    {
      headerName: "FAV 3 - E [m]",
      field: "fav3_E",
      renderCell: (row: any) => formatCellValue(row.fav3_E, 2),
    },
    {
      headerName: "FAV 3 - T [m]",
      field: "fav3_T",
      renderCell: (row: any) => formatCellValue(row.fav3_T, 2),
    },
    {
      headerName: "FAV 3 - β [°]",
      field: "fav3_beta",
      renderCell: (row: any) => formatCellValue(row.fav3_beta, 2),
    },
    {
      headerName: "FAV 3 - α [°]",
      field: "fav3_alpha",
      renderCell: (row: any) => formatCellValue(row.fav3_alpha, 2),
    },
  ];

  const ventanaMultiHeader = {
    rows: [
      [
        { label: "Tipo de vano Acristalado (incluye marco)", rowSpan: 2 },
        { label: "Características espacio contiguo al elemento", rowSpan: 2 },
        { label: "Orientación", rowSpan: 2 },
        { label: "Alojado en", rowSpan: 2 },
        { label: "Tipo de Cierre", rowSpan: 2 },
        { label: "Posición Ventanal", rowSpan: 2 },
        { label: "Aislación Con/sin retorno", rowSpan: 2 },
        { label: "Alto (H) [m]", rowSpan: 2 },
        { label: "Ancho (W) [m]", rowSpan: 2 },
        { label: "Marco", rowSpan: 2 },
        { label: "FAV 1", colSpan: 2 },
        { label: "FAV 2 izq", colSpan: 2 },
        { label: "FAV 2 Der", colSpan: 2 },
        { label: "FAV 3", colSpan: 4 },
      ],
      [
        { label: "D [m]" },
        { label: "L [m]" },
        { label: "P [m]" },
        { label: "S [m]" },
        { label: "P [m]" },
        { label: "S [m]" },
        { label: "E [m]" },
        { label: "T [m]" },
        { label: "β [°]" },
        { label: "α [°]" },
      ],
    ],
  };

  // Definición de columnas para la tabla de puertas
  const doorColumnsNew = [
    { headerName: "Tipo Puerta", field: "tipoPuente" },
    { headerName: "Características", field: "characteristics" },
    { headerName: "Orientación", field: "orientacion" },
    {
      headerName: "Alto [m]",
      field: "high",
      renderCell: (row: any) => formatCellValue(row.high, 2),
    },
    {
      headerName: "Ancho [m]",
      field: "broad",
      renderCell: (row: any) => formatCellValue(row.broad, 2),
    },
    {
      headerName: "D [m]",
      field: "fav1D",
      renderCell: (row: any) => formatCellValue(row.fav1D, 2),
    },
    {
      headerName: "L [m]",
      field: "fav1L",
      renderCell: (row: any) => formatCellValue(row.fav1L, 2),
    },
    {
      headerName: "P [m]",
      field: "fav2izqP",
      renderCell: (row: any) => formatCellValue(row.fav2izqP, 2),
    },
    {
      headerName: "S [m]",
      field: "fav2izqS",
      renderCell: (row: any) => formatCellValue(row.fav2izqS, 2),
    },
    {
      headerName: "P [m]",
      field: "fav2DerP",
      renderCell: (row: any) => formatCellValue(row.fav2DerP, 2),
    },
    {
      headerName: "S [m]",
      field: "fav2DerS",
      renderCell: (row: any) => formatCellValue(row.fav2DerS, 2),
    },
    {
      headerName: "E [m]",
      field: "fav3E",
      renderCell: (row: any) => formatCellValue(row.fav3E, 2),
    },
    {
      headerName: "T [m]",
      field: "fav3T",
      renderCell: (row: any) => formatCellValue(row.fav3T, 2),
    },
    {
      headerName: "β [°]",
      field: "fav3Beta",
      renderCell: (row: any) => formatCellValue(row.fav3Beta, 2),
    },
    {
      headerName: "α [°]",
      field: "fav3Alpha",
      renderCell: (row: any) => formatCellValue(row.fav3Alpha, 2),
    },
  ];

  const doorMultiHeader = {
    rows: [
      [
        { label: "Tipo de Puerta", rowSpan: 2 },
        { label: "Características espacio contiguo al elemento", rowSpan: 2 },
        { label: "Orientación", rowSpan: 2 },
        { label: "Alto [m]", rowSpan: 2 },
        { label: "Ancho [m]", rowSpan: 2 },
        { label: "FAV 1", colSpan: 2 },
        { label: "FAV 2 izq", colSpan: 2 },
        { label: "FAV 2 Der", colSpan: 2 },
        { label: "FAV 3", colSpan: 4 },
      ],
      [
        { label: "D [m]" },
        { label: "L [m]" },
        { label: "P [m]" },
        { label: "S [m]" },
        { label: "P [m]" },
        { label: "S [m]" },
        { label: "E [m]" },
        { label: "T [m]" },
        { label: "β [°]" },
        { label: "α [°]" },
      ],
    ],
  };

  // Definición de columnas para la tabla de techumbre
  const roofColumns = [
    { headerName: "Techos", field: "techos" },
    { headerName: "Características espacio contiguo al elemento", field: "caracteristicas" },
    {
      headerName: "Área [m²]",
      field: "area",
      renderCell: (row: any) => formatCellValue(row.area, 2),
    },
    {
      headerName: "U [W/m²K]",
      field: "u",
      renderCell: (row: any) => formatCellValue(row.u, 2),
    },
  ];

  // Definición de columnas para la tabla de pisos
  const floorColumns = [
    {
      headerName: "Pisos",
      field: "pisos",
      renderCell: (row: FloorData) => formatCellValue(row.pisos),
    },
    {
      headerName: "Características espacio contiguo al elemento",
      field: "caracteristicas",
      renderCell: (row: FloorData) => formatCellValue(row.caracteristicas),
    },
    {
      headerName: "Área [m²]",
      field: "area",
      renderCell: (row: FloorData) => formatCellValue(row.area, 2),
    },
    {
      headerName: "U [W/m²K]",
      field: "uValue",
      renderCell: (row: FloorData) =>
        row.uValue === 0 ? "-" : formatCellValue(row.uValue, 2),
    },
    {
      headerName: "Perímetro Suelo [m]",
      field: "perimetroSuelo",
      renderCell: (row: FloorData) => formatCellValue(row.perimetroSuelo, 2),
    },
    {
      headerName: "Piso ventilado",
      field: "pisoVentilado",
      renderCell: (row: FloorData) => formatCellValue(row.pisoVentilado),
    },
    {
      headerName: "PT P06 L [m]",
      field: "ptP06L",
      renderCell: (row: FloorData) => formatCellValue(row.ptP06L, 2),
    },
  ];

  // NUEVA definición de columnas para la tabla de obstrucciones (versión simplificada)
  const obstructionColumns = [
    {
      headerName: "Ángulo Azimut",
      field: "anguloAzimut",
      renderCell: (row: ObstructionsData) => row.mainRow ? row.anguloAzimut : "",
    },
    {
      headerName: "Orientación",
      field: "orientación",
      renderCell: (row: ObstructionsData) => row.mainRow ? (row.orientación || "-") : "",
    },
    {
      headerName: "Obstrucción",
      field: "obstrucción",
      renderCell: (row: ObstructionsData) => row.obstrucción === 0 ? "-" : row.obstrucción,
    },
    {
      headerName: "División",
      field: "división",
      renderCell: (row: ObstructionsData) => row.división,
    },
    {
      headerName: "A [m]",
      field: "a",
      renderCell: (row: ObstructionsData) => row.a === 0 ? "-" : row.a,
    },
    {
      headerName: "B [m]",
      field: "b",
      renderCell: (row: ObstructionsData) => row.b === 0 ? "-" : row.b,
    },
    {
      headerName: "D [m]",
      field: "d",
      renderCell: (row: ObstructionsData) => row.d === 0 ? "-" : row.d,
    },
  ];

  // Función de formateo: reemplaza el valor 0 por guion y en otros casos formatea con dos decimales
  const formatCellValue = (value: any, decimalPlaces?: number): string => {
    if (value === 0) {
      return "-";
    }
    if (value === undefined || value === null) {
      return "";
    }
    if (decimalPlaces !== undefined && typeof value === "number") {
      return value.toFixed(decimalPlaces);
    }
    return value.toString();
  };

  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const enclosure_id = typeof window !== "undefined" ? localStorage.getItem("enclosure_id") : null;

  useEffect(() => {
    if (!token || !enclosure_id) return;
    const headers = {
      accept: "application/json",
      Authorization: `Bearer ${token}`,
    };

    // Obtener muros
    fetch(`${constantUrlApiEndpoint}/wall-enclosures/${enclosure_id}`, { headers })
      .then((res) => res.json())
      .then((data: Muro[]) => setWalls(data))
      .catch((err) => console.error("Error al obtener muros:", err));

    // Obtener ventanas y fusionar datos FAV
    const fetchWindowsData = async () => {
      try {
        const windowsResponse = await fetch(
          `${constantUrlApiEndpoint}/window-enclosures/${enclosure_id}`,
          { headers }
        );
        if (!windowsResponse.ok) {
          throw new Error("Error al obtener ventanas");
        }
        const windowsData = await windowsResponse.json();
        console.log("Ventanas:", windowsData);

        const favResponse = await fetch(
          `${constantUrlApiEndpoint}/window/fav-enclosures/${enclosure_id}/`,
          { headers }
        );
        if (!favResponse.ok) {
          throw new Error("Error al obtener los favs de ventana");
        }
        const favsData = await favResponse.json();
        console.log("Datos FAV de ventanas:", favsData);

        const mergedData = windowsData.map((win: any) => {
          const fav = favsData.find((f: any) => f.item_id === win.id);
          if (fav) {
            return {
              ...win,
              fav1_D: fav.fav1?.d ?? "",
              fav1_L: fav.fav1?.l ?? "",
              fav2izq_P: fav.fav2_izq?.p ?? "",
              fav2izq_S: fav.fav2_izq?.s ?? "",
              fav2der_P: fav.fav2_der?.p ?? "",
              fav2der_S: fav.fav2_der?.s ?? "",
              fav3_E: fav.fav3?.e ?? "",
              fav3_T: fav.fav3?.t ?? "",
              fav3_beta: fav.fav3?.beta ?? "",
              fav3_alpha: fav.fav3?.alfa ?? "",
            };
          }
          return {
            ...win,
            fav1_D: "",
            fav1_L: "",
            fav2izq_P: "",
            fav2izq_S: "",
            fav2der_P: "",
            fav2der_S: "",
            fav3_E: "",
            fav3_T: "",
            fav3_beta: "",
            fav3_alpha: "",
          };
        });

        console.log("Ventanas fusionadas:", mergedData);
        setWindows(mergedData);
      } catch (error) {
        console.error("Error fetching windows data:", error);
      }
    };

    fetchWindowsData();

    // Obtener techumbre y formatear datos para la tabla simplificada
    fetch(`${constantUrlApiEndpoint}/roof-enclosures/${enclosure_id}`, { headers })
      .then((res) => res.json())
      .then((enclosureData: any[]) => {
        const formattedData = enclosureData.map((item) => ({
          id: item.id,
          techos: item.name,
          caracteristicas: item.characteristic,
          area: item.area,
          u: item.u,
        }));
        setRoofData(formattedData);
      })
      .catch((err) => console.error("Error al obtener techumbre:", err));

    // Obtener pisos y formatearlos para la nueva tabla
    fetch(`${constantUrlApiEndpoint}/floor-enclosures/${enclosure_id}`, { headers })
      .then((res) => res.json())
      .then((data: any[]) => {
        const formattedData: FloorData[] = data.map((item, index) => ({
          id: item.id,
          index: index,
          pisos: item.name,
          floor_id: item.floor_id,
          caracteristicas: item.characteristic,
          area: item.area,
          uValue: item.value_u,
          perimetroSuelo: item.parameter,
          pisoVentilado: item.is_ventilated,
          ptP06L: item.po6_l,
        }));
        setFloorTableData(formattedData);
      })
      .catch((err) => console.error("Error al obtener pisos:", err));

    // Obtener puentes térmicos
    fetch(`${constantUrlApiEndpoint}/thermal-bridge/${enclosure_id}`, { headers })
      .then((res) => res.json())
      .then((data: PuenteTermico[]) => setThermalBridges(data))
      .catch((err) => console.error("Error al obtener puentes térmicos:", err));
  }, [token, enclosure_id]);

  useEffect(() => {
    if (!token || !enclosure_id) return;
    const fetchDoorData = async () => {
      try {
        const doorEnclosuresResponse = await fetch(
          `${constantUrlApiEndpoint}/door-enclosures/${enclosure_id}`,
          {
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
          }
        );
        if (!doorEnclosuresResponse.ok) {
          throw new Error("Error al obtener los datos de puertas");
        }
        const doorEnclosuresData = await doorEnclosuresResponse.json();
        const tableData: DoorData[] = doorEnclosuresData.map((item: any) => ({
          id: item.id,
          door_id: item.door_id,
          tipoPuente: `ID: ${item.door_id}`,
          characteristics: item.characteristics,
          anguloAzimut: item.angulo_azimut,
          orientacion: item.orientation,
          high: item.high,
          broad: item.broad,
          fav1D: 0,
          fav1L: 0,
          fav2izqP: 0,
          fav2izqS: 0,
          fav2DerP: 0,
          fav2DerS: 0,
          fav3E: 0,
          fav3T: 0,
          fav3Beta: 0,
          fav3Alpha: 0,
          fav_id: null,
        }));

        const favResponse = await fetch(
          `${constantUrlApiEndpoint}/door/fav-enclosures/${enclosure_id}/`,
          {
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
          }
        );
        if (!favResponse.ok) {
          throw new Error("Error al obtener los favs de puerta");
        }
        const favsData = await favResponse.json();
        const mergedData = tableData.map((row) => {
          const fav = favsData.find((f: any) => f.item_id === row.id);
          if (fav) {
            return {
              ...row,
              fav1D: fav.fav1.d,
              fav1L: fav.fav1.l,
              fav2izqP: fav.fav2_izq.p,
              fav2izqS: fav.fav2_izq.s,
              fav2DerP: fav.fav2_der.p,
              fav2DerS: fav.fav2_der.s,
              fav3E: fav.fav3.e,
              fav3T: fav.fav3.t,
              fav3Beta: fav.fav3.beta,
              fav3Alpha: fav.fav3.alfa,
              fav_id: fav.id,
            };
          }
          return row;
        });

        const angleResponse = await fetch(`${constantUrlApiEndpoint}/angle-azimut`, {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        });
        if (!angleResponse.ok) {
          throw new Error("Error al obtener las opciones de ángulo azimut");
        }
        const angleOpts: string[] = await angleResponse.json();
        setAngleOptions(angleOpts);

        const doorResponse = await fetch(
          `${constantUrlApiEndpoint}/user/elements/?type=door`,
          {
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
          }
        );
        if (!doorResponse.ok) {
          throw new Error("Error al obtener las opciones de puertas");
        }
        const doorData = await doorResponse.json();
        setDoorOptions(doorData);

        const updatedData = mergedData.map((row) => {
          const doorInfo = doorData.find((door: any) => door.id === row.door_id);
          if (doorInfo) {
            return { ...row, tipoPuente: doorInfo.name_element };
          }
          return row;
        });
        setDoorTableData(updatedData);
      } catch (error) {
        console.error("Error fetching door table data:", error);
      }
    };

    fetchDoorData();
  }, [token, enclosure_id]);

  useEffect(() => {
    const enclosureId = localStorage.getItem("enclosure_id");
    if (!token || !enclosureId) return;
    setObstructionsLoading(true);
    const headers = {
      accept: "application/json",
      Authorization: `Bearer ${token}`,
    };
    fetch(`${constantUrlApiEndpoint}/obstruction/${enclosureId}`, { headers })
      .then((res) => res.json())
      .then((data) => {
        const mappedData = data.orientations.map((orientation: any, index: number) => {
          const divisionData =
            orientation.divisions && orientation.divisions.length > 0
              ? orientation.divisions[0]
              : null;
          return {
            id: orientation.orientation_id,
            division_id: divisionData ? divisionData.division_id : null,
            index: index + 1,
            división: divisionData ? divisionData.division : "-",
            floor_id: orientation.enclosure_id,
            a: divisionData ? divisionData.a : 0,
            b: divisionData ? divisionData.b : 0,
            d: divisionData ? divisionData.d : 0,
            anguloAzimut: orientation.azimut,
            orientación: orientation.orientation,
            obstrucción: 0,
            mainRow: true,
          };
        });
        setObstructionsData(mappedData);
        setObstructionsLoading(false);
      })
      .catch((err) => {
        console.error("Error al cargar datos de obstrucciones", err);
        setObstructionsLoading(false);
      });
  }, [token]);

  return (
    <div>
      {/* Cabecera: Vista de Desarrollo de proyecto */}
      <HeaderVistaDesarrollo />

      {/* Muros y Puentes Térmicos */}
      <Card>
        <section>
          <div style={{ marginTop: "10px" }}>
            <Title text="Muros y Puentes Térmicos" variant="subtitle" />
          </div>
          {walls.length > 0 ? (
            <TablesParameters
              data={walls.map((wall) => {
                const thermal = thermalBridges.find((tb) => tb.wall_id === wall.id);
                return { ...wall, ...(thermal || {}) };
              })}
              columns={mergedColumns}
              multiHeader={mergedMultiHeader}
            />
          ) : (
            <p>No hay muros creados.</p>
          )}
        </section>
      </Card>

      {/* Ventanas */}
      <Card>
        <section>
          <div style={{ marginTop: "10px" }}>
            <Title text="Ventanas" variant="subtitle" />
          </div>
          {windows.length > 0 ? (
            <TablesParameters
              data={windows.map((win) => ({
                id: win.id,
                tipoVano: win.window_name,
                caracteristicas: win.characteristics || "",
                anguloAzimut: win.angulo_azimut,
                orientacion: win.orientation,
                alojadoEn: win.alojado_en,
                tipoCierre: win.clousure_type,
                posicionVentanal: win.position,
                aislacion: win.with_no_return,
                alto: win.high,
                ancho: win.broad,
                marco: win.frame,
                acciones: win.acciones || "",
                fav1_D: win.fav1_D,
                fav1_L: win.fav1_L,
                fav2izq_P: win.fav2izq_P,
                fav2izq_S: win.fav2izq_S,
                fav2der_P: win.fav2der_P,
                fav2der_S: win.fav2der_S,
                fav3_E: win.fav3_E,
                fav3_T: win.fav3_T,
                fav3_beta: win.fav3_beta,
                fav3_alpha: win.fav3_alpha,
                acciones_fav: win.acciones_fav || "",
              }))}
              columns={ventanaColumns}
              multiHeader={ventanaMultiHeader}
            />
          ) : (
            <p>No hay ventanas creadas.</p>
          )}
        </section>
      </Card>

      {/* Puertas */}
      <Card>
        <section>
          <div style={{ marginTop: "10px" }}>
            <Title text="Puertas" variant="subtitle" />
          </div>
          {doorTableData.length > 0 ? (
            <TablesParameters data={doorTableData} columns={doorColumnsNew} multiHeader={doorMultiHeader} />
          ) : (
            <p>No hay puertas creadas.</p>
          )}
        </section>
      </Card>

      {/* Techumbre - tabla simplificada */}
      <Card>
        <section>
          <div style={{ marginTop: "10px" }}>
            <Title text="Techumbre" variant="subtitle" />
          </div>
          {roofData.length > 0 ? (
            <TablesParameters data={roofData} columns={roofColumns} />
          ) : (
            <p>No hay techumbre creada.</p>
          )}
        </section>
      </Card>

      {/* Pisos */}
      <Card>
        <section>
          <div style={{ marginTop: "10px" }}>
            <Title text="Pisos" variant="subtitle" />
          </div>
          {floorTableData.length > 0 ? (
            <TablesParameters data={floorTableData} columns={floorColumns} />
          ) : (
            <p>No hay pisos creados.</p>
          )}
        </section>
      </Card>

      {/* Obstrucciones - tabla reemplazada con la versión simplificada inline */}
      <Card>
        <section>
          <div style={{ marginTop: "10px" }}>
            <Title text="Obstrucciones" variant="subtitle" />
          </div>
          {obstructionsLoading ? (
            <div className="text-center p-4">
              <p>Cargando datos de obstrucciones...</p>
            </div>
          ) : obstructionsData.length > 0 ? (
            <TablesParameters columns={obstructionColumns} data={obstructionsData} />
          ) : (
            <p>No hay obstrucciones creadas.</p>
          )}
        </section>
      </Card>
    </div>
  );
};

export default RecintoView;
