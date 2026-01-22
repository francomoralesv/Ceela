import Breadcrumb from "@/components/common/Breadcrumb";
import MapAutocompletion from "@/components/maps/MapAutocompletion";
import ConfiguracionEnergiaTab from "@/components/projects/tabs/ConfiguracionEnergiaTab";
import { useApi } from "@/hooks/useApi";
import { notify } from "@/utils/notify";
import axios from "axios";
import "bootstrap/dist/css/bootstrap.min.css";
import "leaflet/dist/leaflet.css";
import { useRouter } from "next/router";
import React, { useCallback, useEffect, useState } from "react";
import { Alert } from "react-bootstrap";
import { AdminSidebar } from "../src/components/administration/AdminSidebar";
import Card from "../src/components/common/Card";
import CustomButton from "../src/components/common/CustomButton";
import Title from "../src/components/Title";
import useAuth from "../src/hooks/useAuth";
import { constantUrlApiEndpoint } from "../src/utils/constant-url-endpoint";
import locationData from "public/locationData";

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
  zone?: string;
  residential_type?: string;
  region?: string; // Add this line
  building_name?: string; // New field for building name
}

interface Project {
  name_project: string;
}

const initialFormData: FormData = (() => {
    const baseFormData: FormData = {
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
        latitude: 0,
        longitude: 0,
        address: "",
        zone: "",
        residential_type: "",
        region: "",
        building_name: "",
    };

    if (typeof window !== 'undefined' && 'geolocation' in navigator) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                baseFormData.latitude = position.coords.latitude;
                baseFormData.longitude = position.coords.longitude;
            },
            (error) => {
                console.error("Error getting location:", error);
                baseFormData.latitude = -33.4589314398474;
                baseFormData.longitude = -70.6703553846175;
            },
            {
                enableHighAccuracy: true,
                timeout: 5000,
                maximumAge: 0
            }
        );
    }

    return baseFormData;
})();

const ProjectWorkflowPart1: React.FC = () => {
  useAuth();
  const router = useRouter();

  const [, setPrimaryColor] = useState("#3ca7b7");
  const [step, setStep] = useState<number>(1);
  const [isStep1Validated, setIsStep1Validated] = useState<boolean>(false);
  const [locationSearch, setLocationSearch] = useState("");
  const [errors, setErrors] = useState<Partial<Record<keyof FormData, string>>>(
    {}
  );
  const [submitted, setSubmitted] = useState(false);
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [loading, setLoading] = useState<boolean>(false);
  const [globalError, setGlobalError] = useState<string>("");
  const [zones, setZones] = useState<any[]>([]);

  const [disableButtonSave, setDisableButtonSave] = useState<boolean>(false);
  const [mapCountry, setMapCountry] = useState<string>("");

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
  ];

  useEffect(() => {
    const pColor =
      getComputedStyle(document.documentElement)
        .getPropertyValue("--primary-color")
        .trim() || "#3ca7b7";
    setPrimaryColor(pColor);
  }, []);

  // Efecto para obtener las zonas de forma dinámica cuando cambien latitud y longitud
  useEffect(() => {
    if (isStep1Validated && formData.latitude && formData.longitude) {
      axios
        .get(
          `${constantUrlApiEndpoint}/zones?latitude=${formData.latitude}&longitude=${formData.longitude}`
        )
        .then((response) => {
          setZones(response.data);
        })
        .catch((error) => {
          console.error("Error al obtener las zonas:", error);
        });
    }
  }, [formData.latitude, formData.longitude]);

  // Efecto para verificar si el país del formulario coincide con el del mapa
  useEffect(() => {
    console.log("Map country ", mapCountry)
    console.log("Form country ", formData.country)

    setDisableButtonSave(formData.country.toLowerCase() !== mapCountry.toLowerCase() || formData.country === "");
  }, [formData.country, mapCountry]);

  const isFieldEmpty = (field: keyof FormData): boolean => {
    const value = formData[field];
    if (typeof value === "string") {
      return !value.trim();
    } else if (typeof value === "number") {
      return value <= 0;
    }
    return true;
  };

  const handleFormInputChange = useCallback(
    (field: keyof FormData, value: string | number) => {
      if (
        field === "building_type" &&
        !value.toString().toLowerCase().startsWith("residencial")
      ) {
        // Reset residential_type when building_type is not "Residencial %"
        setFormData((prev) => ({ ...prev, residential_type: "" }));
        setFormData((prev) => ({ ...prev, number_homes_per_level: 0 }));
      }

      if (
        (field === "number_levels" ||
          field === "number_homes_per_level" ||
          field === "built_surface") &&
        typeof value === "number" &&
        value < 0
      ) {
        value = 0;
      }
      setFormData((prev) => ({ ...prev, [field]: value }));
      if (submitted && value !== "" && value !== 0) {
        setErrors((prev) => ({ ...prev, [field]: "" }));
      }
    },
    [submitted]
  );

  const handleCountryChange = useCallback(
    (country: Country) => {
      handleFormInputChange("country", country);
      handleFormInputChange("department", "");
      handleFormInputChange("province", "");
      setErrors((prev) => ({
        ...prev,
        country: "",
        department: "",
        province: "",
      }));
    },
    [handleFormInputChange]
  );

  const handleDepartmentChange = useCallback(
    (department: string) => {
      handleFormInputChange("department", department);
      handleFormInputChange("province", "");
      setErrors((prev) => ({ ...prev, department: "", province: "" }));
    },
    [handleFormInputChange]
  );

  const validateStep1Fields = (): Partial<Record<keyof FormData, string>> => {
    const newErrors: Partial<Record<keyof FormData, string>> = {};
    if (!formData.name_project.trim())
      newErrors.name_project = "El nombre del proyecto es obligatorio.";
    if (!formData.owner_name.trim())
      newErrors.owner_name = "El nombre del propietario es obligatorio.";
    if (!formData.owner_lastname.trim())
      newErrors.owner_lastname = "El apellido del propietario es obligatorio.";
    // if (!formData.country.trim())
    // newErrors.country = "Debe seleccionar un país.";
    // if (!formData.department.trim())
    // newErrors.department = "Debe seleccionar un departamento.";
    // if (!formData.province.trim())
    // newErrors.province = "Debe seleccionar una provincia.";
    if (!formData.district.trim())
      newErrors.district = "El distrito es obligatorio.";
    if (!formData.building_type.trim())
      newErrors.building_type = "Debe seleccionar un tipo de edificación.";
    if (
      !formData.residential_type?.trim() &&
      formData.building_type.toLowerCase().startsWith("residencial")
    )
      newErrors.residential_type = "Debe seleccionar un tipo de edificación.";
    if (formData.number_levels <= 0)
      newErrors.number_levels = "El número de niveles debe ser mayor a 0.";
    if (
      formData.number_homes_per_level <= 0 &&
      formData.building_type.toLowerCase().startsWith("residencial")
    )
      newErrors.number_homes_per_level =
        "El número de viviendas/oficinas por nivel debe ser mayor a 0.";
    if (formData.built_surface <= 0)
      newErrors.built_surface = "La superficie construida debe ser mayor a 0.";
    return newErrors;
  };

  const { post, get, put } = useApi();

  const checkProjectNameExists = async (): Promise<boolean> => {
    try {
      const token = localStorage.getItem("token");
      if (!token) return false;
      const response = await get(`/user/projects/?limit=999999&num_pag=1`);
      const projects: Project[] = response.projects || [];
      return projects.some(
        (project: Project) =>
          project.name_project.trim().toLowerCase() ===
          formData.name_project.trim().toLowerCase()
      );
    } catch (error) {
      console.error(
        "Error al verificar la unicidad del nombre del proyecto",
        error
      );
      return false;
    }
  };

  const [latitude, setLatitude] = useState<number>(0);
  const [longitude, setLongitude] = useState<number>(0);

  const handleGeolocation = () => {
    if (!navigator.geolocation) {
      console.error("La geolocalización no es soportada en este navegador.");
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        setLatitude(latitude);
        setLongitude(longitude);
        handleFormInputChange("latitude", latitude);
        handleFormInputChange("longitude", longitude);
        console.log(`Latitud: ${latitude}, Longitud: ${longitude}`);

        // Realizar solicitud de geocodificación inversa a través del proxy
        axios
          .get(`/api/geocode-reverse`, {
            params: {
              lat: latitude,
              lon: longitude,
            },
          })
          .then((response) => {
            const { display_name, address } = response.data;
            const country = address?.country || "";
            handleFormInputChange("address", display_name);
            setMapCountry(country);
            console.log("Dirección obtenida:", display_name);
            console.log("País detectado:", country);
          })
          .catch((error) => {
            console.error("Error en la geocodificación inversa:", error);
          });
      },
      () => {
        console.error("No se pudo obtener la ubicación actual.");
      }
    );
  };

  const enviarProyecto = async () => {
    setLoading(true);
    setGlobalError("");
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        setGlobalError("Por favor, inicie sesión para continuar.");
        setLoading(false);
        return;
      } const requestBody = {
        country: formData.country || "Perú",
        divisions: {
          department: formData.department,
          province: formData.province,
          district: formData.district,
          address: formData.address,
          region: formData.region, // Add the region to divisions
        },
        department: formData.department || "",
        province: formData.province || "",
        district: formData.district || "",
        name_project: formData.name_project,
        owner_name: formData.owner_name,
        owner_lastname: formData.owner_lastname,
        building_type: formData.building_type,
        main_use_type: formData.main_use_type,
        number_levels: formData.number_levels,
        number_homes_per_level: formData.number_homes_per_level,
        built_surface: formData.built_surface,
        latitude: formData.latitude,
        longitude: formData.longitude,
        project_metadata: {
          zone: formData.zone,
        },
        residential_type: formData.residential_type,
        building_name: formData.building_name, // Added building_name field
      };
      const data = await post(`/projects/create`, requestBody);
      const { project_id } = data;
      localStorage.setItem("last_created_project", project_id.toString());
      localStorage.setItem("project_id", project_id.toString());
      localStorage.setItem("project_department", formData.department);
      localStorage.setItem("project_name", formData.name_project);
      notify("Proyecto creado con éxito.");
      setFormData(initialFormData);
      router.push(`/workflow-part2-create?project_id=${project_id}`);
    } catch (error: unknown) {
      console.error("Error al enviar el proyecto:", error);
      let errorMessage: string | object = "Error desconocido";
      if (axios.isAxiosError(error)) {
        errorMessage = error.response?.data?.detail || error.message;
      } else if (error instanceof Error) {
        errorMessage = error.message;
      }
      if (typeof errorMessage !== "string") {
        errorMessage = JSON.stringify(errorMessage);
      }
      setGlobalError(errorMessage as string);
      notify("Ocurrió un error al enviar el proyecto.");
    }
    setLoading(false);
  };

  // Función que se encarga de la acción del botón Continuar en el paso 1
  const handleStep1Action = async () => {
    setSubmitted(true);
    const fieldErrors = validateStep1Fields();
    if (Object.keys(fieldErrors).length > 0) {
      setErrors(fieldErrors);
      notify("Por favor, complete correctamente todos los campos requeridos.");
      return;
    }
    // Verificar si el nombre del proyecto ya existe
    const nameExists = await checkProjectNameExists();
    if (nameExists) {
      setErrors((prev) => ({
        ...prev,
        name_project:
          "El nombre del proyecto ya existe. Por favor, elija otro nombre.",
      }));
      notify("El nombre del proyecto ya existe. Por favor, elija otro nombre.");
      return;
    }
    // Si todo es correcto, marcar que se validó el paso 1 y avanzar al siguiente paso
    setIsStep1Validated(true);
    setStep(2);
  };

  // Función para controlar el cambio de paso desde el sidebar
  const handleSidebarStepChange = (newStep: number) => {
    if (newStep > 1 && !isStep1Validated) {
      notify(
        "Por favor, complete y valide correctamente el Paso 1 antes de avanzar."
      );
      return;
    }
    setStep(newStep);
  };

  const renderMainHeader = () => {
    return <Title text="Proyecto nuevo" />;
  };

  const [completionList, setCompletionList] = useState<
    {
      Title: string;
      Position: [number, number];
    }[]
  >([]);



  useEffect(() => {
    if (!locationSearch.trim()) return;

    const delaySearch = setTimeout(() => {
      console.log("Buscando ubicación:", locationSearch);
      axios
        .get(`/api/map?q=${locationSearch}&lat=${latitude}&long=${longitude}`)
        .then((response) => {
          const { data } = response;
          console.log("Respuesta de ubicación", data.results.ResultItems);
          setCompletionList(data.results.ResultItems);
        })
        .catch((error) => {
          console.error("Error al buscar la ubicación:", error);
        });
    }, 500);

    return () => clearTimeout(delaySearch);
  }, [locationSearch, latitude, longitude]);

  return (
    <>
      <Card>
        <div className="d-flex align-items-center w-100">
          {renderMainHeader()}
          <Breadcrumb
            items={[
              { title: "Proyectos", href: "/project-list", active: false },
              { title: "Nuevo proyecto", active: true },
            ]}
          />
        </div>
      </Card>
      <Card>
        <div
          className="d-flex flex-wrap"
          style={{ alignItems: "stretch", gap: 0 }}
        >
          {/* Sidebar dinámico con el arreglo de pasos */}
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
                    <label className="form-label">
                      Nombre del proyecto{" "}
                      {isFieldEmpty("name_project") && (
                        <span style={{ color: "red" }}>*</span>
                      )}
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      value={formData.name_project}
                      onChange={(e) =>
                        handleFormInputChange("name_project", e.target.value)
                      }
                      style={
                        submitted && errors.name_project
                          ? { borderColor: "red" }
                          : undefined
                      }
                    />
                    {submitted && errors.name_project && (
                      <small className="text-danger">
                        {errors.name_project}
                      </small>
                    )}
                  </div>
                  <div className="col-12 col-md-6">
                    <label className="form-label">
                      Nombre del propietario{" "}
                      {isFieldEmpty("owner_name") && (
                        <span style={{ color: "red" }}>*</span>
                      )}
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      value={formData.owner_name}
                      onChange={(e) =>
                        handleFormInputChange("owner_name", e.target.value)
                      }
                    />
                    {submitted && errors.owner_name && (
                      <small className="text-danger">{errors.owner_name}</small>
                    )}
                  </div>
                </div>
                <div className="row mb-3">
                  <div className="col-12 col-md-6">
                    <label className="form-label">
                      Apellido del propietario{" "}
                      {isFieldEmpty("owner_lastname") && (
                        <span style={{ color: "red" }}>*</span>
                      )}
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      value={formData.owner_lastname}
                      onChange={(e) =>
                        handleFormInputChange("owner_lastname", e.target.value)
                      }
                    />
                    {submitted && errors.owner_lastname && (
                      <small className="text-danger">
                        {errors.owner_lastname}
                      </small>
                    )}
                  </div>

                </div>
                <div className="row">
                  <div className="col-6">
                    <label className="form-label">
                      País
                      {!router.query.id && (
                        <span style={{ color: "red" }}>*</span>
                      )}
                    </label>
                    <select
                      className="form-control"
                      value={formData.country}
                      onChange={(e) =>
                        handleCountryChange(e.target.value as Country)
                      }
                    >
                      <option value="">Seleccione un país</option>
                      {Object.keys(locationData).map((country) => (
                        <option key={country} value={country}>
                          {country}
                        </option>
                      ))}
                    </select>
                    {router.query.id && submitted && errors.country && (
                      <small className="text-danger">
                        {errors.country}
                      </small>
                    )}
                  </div>
                  <div className="col-6">
                    <label className="form-label">
                      Región{" "}
                      {!router.query.id && (
                        <span style={{ color: "red" }}>*</span>
                      )}
                    </label>
                    <select
                      className="form-control"
                      value={formData.department}
                      onChange={(e) =>
                        handleDepartmentChange(e.target.value)
                      }
                      disabled={!formData.country}
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
                    {router.query.id && submitted && errors.department && (
                      <small className="text-danger">
                        {errors.department}
                      </small>
                    )}
                  </div>
                </div><br />
                <div className="row">
                  <div className="col-6">
                    <label className="form-label">
                      Ciudad{" "}
                      {!router.query.id && (
                        <span style={{ color: "red" }}>*</span>
                      )}
                    </label>
                    <select
                      className="form-control"
                      value={formData.province}
                      onChange={(e) =>
                        handleFormInputChange("province", e.target.value)
                      }
                      disabled={!formData.department}
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
                    {router.query.id && submitted && errors.province && (
                      <small className="text-danger">
                        {errors.province}
                      </small>
                    )}
                  </div>
                  <div className="col-6">
                    <label className="form-label">
                      Distrito/Municipio
                      {!router.query.id && (
                        <span style={{ color: "red" }}>*</span>
                      )}
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      value={formData.district}
                      onChange={(e) =>
                        handleFormInputChange("district", e.target.value)
                      }
                    />
                    {router.query.id && submitted && errors.district && (
                      <small className="text-danger">
                        {errors.district}
                      </small>
                    )}
                  </div>
                </div>
                <br />
                <div className="row mb-3">
                  <div className="col-12 col-md-6">
                    <label className="form-label">
                      Tipo de edificación{" "}
                      {isFieldEmpty("building_type") && (
                        <span style={{ color: "red" }}>*</span>
                      )}
                    </label>
                    <select
                      className="form-control"
                      value={formData.building_type}
                      onChange={(e) =>
                        handleFormInputChange("building_type", e.target.value)
                      }
                    >
                      <option value="">
                        Seleccione un tipo de edificación
                      </option>
                      <option value="Residencial en altura">
                        Residencial en altura
                      </option>
                      <option value="Residencial en extensión">
                        Residencial en extensión
                      </option>
                      <option value="Educación">Educación</option>
                      <option value="Salud">Salud</option>
                      <option value="Comercio">Comercio</option>
                      <option value="Servicios (oficinas)">
                        Servicios (oficinas)
                      </option>
                    </select>
                    {submitted && errors.building_type && (
                      <small className="text-danger">
                        {errors.building_type}
                      </small>
                    )}
                  </div>
                  <div className="col-12 col-md-6">
                    <label className="form-label">Tipo de residencial</label>
                    <select
                      disabled={
                        !formData.building_type
                          .toLowerCase()
                          .startsWith("residencial")
                      }
                      className="form-control"
                      value={formData.residential_type}
                      onChange={(e) =>
                        handleFormInputChange(
                          "residential_type",
                          e.target.value
                        )
                      }
                    >
                      <option value="">
                        Seleccione un tipo de residencial
                      </option>
                      <option value="De interés social">
                        De interés social
                      </option>
                      <option value="De interés privada">
                        De interés privada
                      </option>
                    </select>
                    {submitted && errors.residential_type && (
                      <small className="text-danger">
                        {errors.residential_type}
                      </small>
                    )}
                  </div>
                </div>

                {/* Fila que contiene Número de niveles y Superficie construida (m²) */}
                <div className="row mb-3">
                  <div className="col-12 col-md-6">
                    <label className="form-label">
                      Número de niveles{" "}
                      {isFieldEmpty("number_levels") && (
                        <span style={{ color: "red" }}>*</span>
                      )}
                    </label>
                    <input
                      type="number"
                      min="0"
                      className="form-control"
                      value={formData.number_levels}
                      onChange={(e) =>
                        handleFormInputChange(
                          "number_levels",
                          parseInt(e.target.value) || 0
                        )
                      }
                    />
                    {submitted && errors.number_levels && (
                      <small className="text-danger">
                        {errors.number_levels}
                      </small>
                    )}
                  </div>
                  <div className="col-12 col-md-6">
                    <label className="form-label">
                      Superficie construida (m²){" "}
                      {isFieldEmpty("built_surface") && (
                        <span style={{ color: "red" }}>*</span>
                      )}
                    </label>
                    <input
                      type="number"
                      min="0"
                      className="form-control"
                      value={formData.built_surface}
                      onChange={(e) =>
                        handleFormInputChange(
                          "built_surface",
                          parseFloat(e.target.value) || 0
                        )
                      }
                    />
                    {submitted && errors.built_surface && (
                      <small className="text-danger">
                        {errors.built_surface}
                      </small>
                    )}
                  </div>
                </div>
                <div className="row mb-3">
                  <div className="col-12 col-md-6">
                    <label className="form-label">
                      Número de viviendas
                      {isFieldEmpty("number_homes_per_level") && (
                        <span style={{ color: "red" }}>*</span>
                      )}
                    </label>
                    <input
                      disabled={
                        !formData.building_type
                          .toLowerCase()
                          .startsWith("residencial")
                      }
                      type="number"
                      min="0"
                      className="form-control"
                      value={formData.number_homes_per_level}
                      onChange={(e) =>
                        handleFormInputChange(
                          "number_homes_per_level",
                          parseInt(e.target.value) || 0
                        )
                      }
                    />
                    {submitted && errors.number_homes_per_level && (
                      <small className="text-danger">
                        {errors.number_homes_per_level}
                      </small>
                    )}
                  </div>
                  <div className="col-12 col-md-6">
                    <label className="form-label">
                      Número de edificio
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      value={formData.building_name}
                      onChange={(e) =>
                        handleFormInputChange(
                          "building_name",
                          e.target.value
                        )
                      }
                    />
                  </div>
                </div>
                <div className="d-flex align-items-center mt-4">
                  (<span style={{ color: "red" }}>*</span>) Campos Obligatorios
                  <CustomButton
                    variant="save"
                    onClick={handleStep1Action}
                    disabled={loading}
                    className="ms-auto"
                    color='orange'
                  >
                    <span className="material-icons" style={{ marginRight: "5px" }}>
                      navigate_next
                    </span>
                    Continuar
                  </CustomButton>
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
                  <MapAutocompletion
                    formData={formData}
                    handleFormInputChange={handleFormInputChange}
                    onCountryDetected={setMapCountry}
                  />
                  <Alert variant="warning" className="mt-3">
                    Para cambiar ubicación mover el marcador en el mapa
                  </Alert>
                  <Alert variant="warning" className="mt-3">
                    Asegurarse que la Zona esté correctamente seleccionada para
                    que se procese correctamente lo datos del proyecto
                  </Alert>
                  <Alert variant="warning" className="mt-3">
                    El país seleccionado en el formulario debe coincidir con el país detectado en el mapa para poder guardar el proyecto.
                  </Alert>
                  <div className="d-flex justify-content-between align-items-center ">
                    <div className="d-flex">
                      <CustomButton variant="save" onClick={handleGeolocation}>
                        <span className="material-icons">location_on</span>
                        Ubicación actual
                      </CustomButton>
                    </div>
                    <div className="d-flex">
                      <CustomButton
                        variant={disableButtonSave ? "gray" : "save"}
                        color='orange'
                        onClick={enviarProyecto}
                        disabled={loading || disableButtonSave}
                        style={{
                          backgroundColor: disableButtonSave ? '#ccc' : undefined,
                          cursor: disableButtonSave ? 'not-allowed' : undefined
                        }}
                      >
                        <span
                          className="material-icons"
                          style={{ marginRight: "5px" }}
                        >
                          sd_card
                        </span>
                        Grabar Datos
                      </CustomButton>
                    </div>
                  </div>
                </div>
              </>
            )}
            {step === 6 && (
              <div className="mt-3">
                {/* Paso 6: Configuración */}
                <React.Suspense fallback={<div>Cargando configuración...</div>}>
                  <ConfiguracionEnergiaTab />
                </React.Suspense>
              </div>
            )}
          </div>
        </div>
      </Card>
    </>
  );
};

export default ProjectWorkflowPart1;
