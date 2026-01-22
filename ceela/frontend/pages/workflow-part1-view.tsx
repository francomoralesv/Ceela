import ProjectInfoHeader from "@/components/common/ProjectInfoHeader";
import axios from "axios";
import "bootstrap/dist/css/bootstrap.min.css";
import "leaflet/dist/leaflet.css";
import dynamic from "next/dynamic";
import { useRouter } from "next/router";
import React, { useEffect, useState } from "react";
import GooIcons from "../public/GoogleIcons";
import Title from "../src/components/Title";
import { AdminSidebar } from "../src/components/administration/AdminSidebar";
import Breadcrumb from "../src/components/common/Breadcrumb";
import Card from "../src/components/common/Card";
import useAuth from "../src/hooks/useAuth";
import { constantUrlApiEndpoint } from "../src/utils/constant-url-endpoint";
import ProjectStatus from "../src/components/projects/ProjectStatus";

// Cargamos el mapa sin SSR
const NoSSRInteractiveMap = dynamic(
  () => import("../src/components/InteractiveMap"),
  {
    ssr: false,
  }
);
const NoSSRInteractiveMap2 = dynamic(
  () => import("../src/components/InteractiveMap2"),
  {
    ssr: false,
  }
);

type Country = "" | "Perú" | "Chile";

interface FormData {
  name_project: string;
  owner_name: string;
  owner_lastname: string;
  country: Country;
  department: string;
  province: string;
  district: string;
  building_type: string;
  main_use_type: string;
  number_levels: number;
  number_homes_per_level: number;
  built_surface: number;
  latitude: number;
  longitude: number;
  address: string;
  residential_type: string;
  building_name?: string; // New field for building name
}

const initialFormData: FormData = {
  name_project: "",
  owner_name: "",
  owner_lastname: "",
  country: "",
  department: "",
  province: "",
  district: "",
  building_type: "",
  main_use_type: "",
  number_levels: 0,
  number_homes_per_level: 0,
  built_surface: 0,
  latitude: -33.4589314398474,
  longitude: -70.6703553846175,
  address: "",
  residential_type: "",
  building_name: "", // New field for building name
};

const ProjectWorkflowPart1: React.FC = () => {
  useAuth();
  const router = useRouter();
  const isViewOnly = true; // Forzar el modo de vista

  const [, setPrimaryColor] = useState("#3ca7b7");
  const [step, setStep] = useState<number>(1);
  const [locationSearch, setLocationSearch] = useState("");
  const [formData, setFormData] = useState<FormData>(initialFormData);
  // Estado para almacenar project_metadata (ahora solo se extrae la zona)
  const [projectMetadata, setProjectMetadata] = useState("");
  const [projectStatus, setProjectStatus] = useState<string | null>(null);

  // Estado para almacenar datos del header del proyecto
  const [projectHeaderData, setProjectHeaderData] = useState({
    projectName: "",
    region: "",
  });

  useEffect(() => {
    const pColor =
      getComputedStyle(document.documentElement)
        .getPropertyValue("--primary-color")
        .trim() || "#3ca7b7";
    setPrimaryColor(pColor);
  }, []);

  // Actualizamos el header del proyecto cuando cambien los datos relevantes
  useEffect(() => {
    setProjectHeaderData({
      projectName: localStorage.getItem("project_name_view") || "",
      region: localStorage.getItem("project_department_view") || "", // o cualquier otra propiedad que defina la región
    });
  }, [formData.name_project, formData.department]);

  // Obtener datos del localStorage para el header del proyecto
  useEffect(() => {
    if (typeof window !== "undefined") {
      const storedLatitude = localStorage.getItem("project_latitude");
      const storedLongitude = localStorage.getItem("project_longitude");
      const currentLatitude = formData.latitude.toString();
      const currentLongitude = formData.longitude.toString();

      if (
        storedLatitude === currentLatitude &&
        storedLongitude === currentLongitude
      ) {
        const storedAddress = localStorage.getItem("project_address");
        if (storedAddress) {
          setFormData((prev) => ({ ...prev, address: storedAddress }));
        }
      }
    }
  }, [formData.latitude, formData.longitude]);

  // Cargar dirección almacenada en localStorage, si existe
  useEffect(() => {
    if (typeof window !== "undefined") {
      const storedAddress = localStorage.getItem("project_address");
      if (storedAddress) {
        setFormData((prev) => ({ ...prev, address: storedAddress }));
      }
    }
  }, []);

  // Actualiza el step en modo vista si se pasa como query
  useEffect(() => {
    if (router.isReady && isViewOnly) {
      const stepQuery = router.query.step;
      if (stepQuery) {
        const stepNumber = parseInt(stepQuery as string, 10);
        if (!isNaN(stepNumber)) {
          setStep(stepNumber);
        }
      }
    }
  }, [router.isReady, router.query.step, isViewOnly]);

  // Carga de datos del proyecto si se está visualizando
  useEffect(() => {
    if (!router.isReady) return;
    if (!router.query.id) {
      setFormData(initialFormData);
      return;
    }
    const projectIdParam = router.query.id;
    const projectIdStr = Array.isArray(projectIdParam)
      ? projectIdParam[0]
      : projectIdParam;
    const fetchProjectData = async () => {
      try {
        const token = localStorage.getItem("token");
        if (!token) return;
        // Utilizar la ruta de admin para obtener project_metadata
        const { data: projectData } = await axios.get(
          `${constantUrlApiEndpoint}/projects/${projectIdStr}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        setFormData({
          name_project: projectData.name_project || "",
          owner_name: projectData.owner_name || "",
          owner_lastname: projectData.owner_lastname || "",
          country: projectData.country || "",
          department: projectData.divisions?.department || "",
          province: projectData.divisions?.province || "",
          district: projectData.divisions?.district || "",
          building_type: projectData.building_type || "",
          main_use_type: projectData.main_use_type || "",
          number_levels: projectData.number_levels || 0,
          number_homes_per_level: projectData.number_homes_per_level || 0,
          built_surface: projectData.built_surface || 0,
          latitude: projectData.latitude || -33.4589314398474,
          longitude: projectData.longitude || -70.6703553846175,
          address: projectData.divisions?.address || "",
          residential_type: projectData.residential_type || "",
          building_name: projectData.building_name || "",
        });
        // Extraer la zona desde project_metadata, asumiendo que la propiedad se llama "zone"
        setProjectMetadata(projectData.project_metadata?.zone || "");
      } catch (error: unknown) {
        console.error("Error fetching project data", error);
      }
    };
    fetchProjectData();
  }, [router.isReady, router.query.id]);

  // Efecto para obtener el estado del proyecto
  useEffect(() => {
    if (!router.isReady || !router.query.id) return;
    
    const projectIdParam = router.query.id;
    const projectIdStr = Array.isArray(projectIdParam) ? projectIdParam[0] : projectIdParam;
    
    const fetchProjectStatus = async () => {
      try {
        const token = localStorage.getItem("token");
        if (!token) {
          console.warn("Token no encontrado");
          return;
        }
        
        const { data: projectData } = await axios.get(
          `${constantUrlApiEndpoint}/projects/${projectIdStr}`,
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
  }, [router.isReady, router.query.id]);

  // Efecto para realizar geocodificación inversa a través del proxy cada vez que cambian las coordenadas.
  useEffect(() => {
    if (formData.latitude && formData.longitude) {
      axios
        .get(`/api/geocode-reverse`, {
          params: {
            lat: formData.latitude,
            lon: formData.longitude,
          },
        })
        .then((response) => {
          const { display_name } = response.data;
          // Actualizamos la dirección si es diferente de la ya almacenada.
          if (display_name && display_name !== formData.address) {
            setFormData((prev) => {
              const updatedData = { ...prev, address: display_name };
              localStorage.setItem("project_address", display_name);
              return updatedData;
            });
          }
        })
        .catch((error) => {
          console.error("Error en la geocodificación inversa:", error);
        });
    }
  }, [formData.latitude, formData.longitude]);

  // Función para obtener el id del proyecto desde localStorage
  const getProjectId = () => localStorage.getItem("project_id") || "";

  // Definición de los pasos para la sidebar (modo vista)
  const steps = [
    {
      stepNumber: 1,
      iconName: "assignment_ind",
      title:
        "1. Agregar detalles de propietario / proyecto y clasificación de edificaciones",
    },
    {
      stepNumber: 2,
      iconName: "location_on",
      title: "2. Ubicación del proyecto",
    },
    {
      stepNumber: 6,
      iconName: "build",
      title: "3. Detalles constructivos",
    },
    {
      stepNumber: 7,
      iconName: "design_services",
      title: "4. Recinto",
    },
    {
      stepNumber: 8,
      iconName: "water_drop",
      title: "5. Agua Caliente Sanitaria",
    },
  ];

  // Función para manejar el cambio de paso en la sidebar
  const handleSidebarStepChange = (newStep: number) => {
    const projectId = getProjectId();
    if (newStep === 1 || newStep === 2) {
      router.push(`/workflow-part1-view?id=${projectId}&step=${newStep}`);
    } else if (newStep === 6) {
      router.push(`/workflow-part2-view?id=${projectId}&step=4`);
    } else if (newStep === 7) {
      router.push(`/workflow-part2-view?id=${projectId}&step=7`);
    } else if (newStep === 8) {
      router.push(`/workflow-part2-view?id=${projectId}&step=8`);
    }
  };

  // Render del encabezado principal
  const renderMainHeader = () => {
    return (
      <Card className="header-card">
        <div className="d-flex flex-column w-100">
          <Title text="Vista de Proyecto" />
          <div className="d-flex justify-content-between align-items-center w-100">
            <div style={{ pointerEvents: "none" }}>
              <ProjectInfoHeader
                projectName={projectHeaderData.projectName}
                region={projectHeaderData.region}
              />
            </div>
            <Breadcrumb
              items={[
                {
                  title: "Vista de Proyecto",
                  href: "/",
                  active: true,
                },
              ]}
            />
          </div>
        </div>
      </Card>
    );
  };

  return (
    <>
      <GooIcons />
      <div>
        <div>{renderMainHeader()}</div>
        <Card>
          <div
            className="d-flex flex-wrap"
            style={{ alignItems: "stretch", gap: 0 }}
          >
            {/* Sidebar para cambiar de step */}
            <AdminSidebar
              activeStep={step}
              onStepChange={handleSidebarStepChange}
              steps={steps}
            />
            <div className="content p-4" style={{ flex: 1 }}>
              {step === 1 && (
                <>
                  {/* Paso 1: Datos generales */}
                  <div className="row mb-3">
                    <div className="col-12 col-md-6">
                      <label className="form-label">Nombre del proyecto</label>
                      <input
                        type="text"
                        className="form-control"
                        value={formData.name_project}
                        disabled
                      />
                    </div>
                    <div className="col-12 col-md-6">
                      <label className="form-label">
                        Nombre del propietario
                      </label>
                      <input
                        type="text"
                        className="form-control"
                        value={formData.owner_name}
                        disabled
                      />
                    </div>
                  </div>
                  <div className="row mb-3">
                    <div className="col-12 col-md-6">
                      <label className="form-label">
                        Apellido del propietario
                      </label>
                      <input
                        type="text"
                        className="form-control"
                        value={formData.owner_lastname}
                        disabled
                      />
                    </div>
                    {/* <div className="col-12 col-md-6">
                      <label className="form-label">País</label>
                      <select
                        className="form-control"
                        value={formData.country}
                        disabled
                      >
                        <option value="">Seleccione un país</option>
                        {Object.keys(locationData).map((country) => (
                          <option key={country} value={country}>
                            {country}
                          </option>
                        ))}
                      </select>
                    </div> */}
                    <div className="col-12 col-md-6">
                      <label className="form-label">Distrito/Municipio</label>
                      <input
                        type="text"
                        className="form-control"
                        value={formData.district}
                        disabled
                      />
                    </div>
                  </div>
                  <div className="row mb-3">
                    {/* <div className="col-12 col-md-6">
                      <label className="form-label">Región</label>
                      <select
                        className="form-control"
                        value={formData.department}
                        disabled
                      >
                        <option value="">Seleccione un departamento</option>
                        {formData.country &&
                          Object.keys(
                            locationData[formData.country]?.departments || {}
                          ).map((dept) => (
                            <option key={dept} value={dept}>
                              {dept}
                            </option>
                          ))}
                      </select>
                    </div> */}
                    {/* <div className="col-12 col-md-6">
                      <label className="form-label">Ciudad</label>
                      <select
                        className="form-control"
                        value={formData.province}
                        disabled
                      >
                        <option value="">Seleccione una provincia</option>
                        {formData.country &&
                          formData.department &&
                          (
                            locationData[formData.country]?.departments?.[
                              formData.department
                            ] || []
                          ).map((prov) => (
                            <option key={prov} value={prov}>
                              {prov}
                            </option>
                          ))}
                      </select>
                    </div> */}
                    <div className="col-12 col-md-6">
                      <label className="form-label">Tipo de edificación</label>
                      <input
                        type="text"
                        className="form-control"
                        value={formData.building_type}
                        disabled
                      />
                    </div>
                    <div className="col-12 col-md-6">
                      <label className="form-label">Tipo de residencial</label>
                      <input
                        type="text"
                        className="form-control"
                        value={formData.residential_type}
                        disabled
                      />
                    </div>
                  </div>
                  {/* Se elimina la sección de "Tipo de uso principal" y se reestructura la información */}
                  <div className="row mb-3">
                    <div className="col-12 col-md-6">
                      <label className="form-label">Número de niveles</label>
                      <input
                        type="number"
                        min="0"
                        className="form-control"
                        value={formData.number_levels}
                        disabled
                      />
                    </div>
                    <div className="col-12 col-md-6">
                      <label className="form-label">
                        Superficie construida (m²)
                      </label>
                      <input
                        type="number"
                        min="0"
                        className="form-control"
                        value={formData.built_surface}
                        disabled
                      />
                    </div>
                  </div>                  <div className="row mb-3">
                    <div className="col-12 col-md-6">
                      <label className="form-label">Número de viviendas</label>
                      <input
                        type="number"
                        min="0"
                        className="form-control"
                        value={formData.number_homes_per_level}
                        disabled
                      />
                    </div>
                    <div className="col-12 col-md-6">
                      <label className="form-label">Número de edificio</label>
                      <input
                        type="text"
                        className="form-control"
                        value={formData.building_name}
                        disabled
                      />
                    </div>
                  </div>
                </>
              )}
              {step === 2 && (
                <>
                  {/* Paso 2: Ubicación */}
                  <div
                    style={{
                      border: "1px solid #ccc",
                      borderRadius: "8px",
                      padding: "30px",
                      marginBottom: "20px",
                    }}
                  >
                    {/* Fila para el input de búsqueda */}
                    <div className="row mb-3">
                      <div className="col-12">
                        <div style={{ position: "relative" }}>
                          <input
                            type="text"
                            className="form-control"
                            value={locationSearch}
                            onChange={(e) => setLocationSearch(e.target.value)}
                            style={{ paddingLeft: "40px" }}
                            disabled
                          />
                          <span
                            className="material-icons"
                            style={{
                              position: "absolute",
                              left: "10px",
                              top: "50%",
                              transform: "translateY(-50%)",
                              color: "#ccc",
                            }}
                          >
                            search
                          </span>
                        </div>
                      </div>
                    </div>
                    {/* Fila con dos columnas: mapa y detalles */}
                    <div className="row">
                      <div className="col-12 col-md-8 mb-3">
                        <div style={{ pointerEvents: "none" }}>
                          {/* <NoSSRInteractiveMap
                            onLocationSelect={() => {}}
                            initialLat={formData.latitude}
                            initialLng={formData.longitude}
                          /> */}
                          <NoSSRInteractiveMap2
                            initialLat={formData.latitude}
                            initialLng={formData.longitude}
                          ></NoSSRInteractiveMap2>
                        </div>
                      </div>
                      <div className="col-12 col-md-4">
                        <div className="mb-3">
                          <label
                            className="form-label"
                            style={{ width: "100%", height: "20px" }}
                          >
                            Datos de ubicaciones encontradas
                          </label>
                          <textarea
                            className="form-control"
                            rows={5}
                            value={`Latitud: ${formData.latitude}, Longitud: ${formData.longitude}`}
                            readOnly
                            style={{ width: "100%", height: "100px" }}
                          />
                        </div>
                        <div className="mb-3">
                          <label
                            className="form-label"
                            style={{ width: "100%", height: "20px" }}
                          >
                            Detalles de la ubicación
                          </label>
                          <textarea
                            className="form-control"
                            rows={5}
                            value={`Dirección: ${formData.address}`}
                            readOnly
                            style={{ width: "100%", height: "100px" }}
                          />
                        </div>
                        <div className="mb-3">
                          <label
                            className="form-label"
                            style={{ width: "100%", height: "20px" }}
                          >
                            Zona
                          </label>
                          <textarea
                            className="form-control"
                            rows={5}
                            value={projectMetadata}
                            readOnly
                            style={{ width: "100%", height: "100px" }}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        </Card>
        {projectStatus && router.query.id && (
          <ProjectStatus
            status={projectStatus}
            projectId={Array.isArray(router.query.id) ? router.query.id[0] : router.query.id}
          />
        )}
      </div>
      <style jsx>{`
        .container {
          font-family: var(--font-family-base);
          font-weight: normal;
        }
      `}</style>
    </>
  );
};

export default ProjectWorkflowPart1;
