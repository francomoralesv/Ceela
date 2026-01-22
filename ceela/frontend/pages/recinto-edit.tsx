import RecintoCaractersComponent from "@/components/RecintoCaractersComponentEdit";
import ProjectInfoHeader from "@/components/common/ProjectInfoHeader";
import Breadcrumb from "@/components/common/Breadcrumb";
import { notify } from "@/utils/notify";
import React, { useEffect, useState } from "react";
import Title from "../src/components/Title";
import Card from "../src/components/common/Card";
import CustomButton from "../src/components/common/CustomButton";
import { constantUrlApiEndpoint } from "../src/utils/constant-url-endpoint";
import "bootstrap-icons/font/bootstrap-icons.css"; // Import Bootstrap icons
import { ArrowLeft, Save, Plus } from 'lucide-react';
import { useRouter } from "next/router";

// Styles for the collapsible section
const styles = {
  collapsibleHeader: {
    cursor: 'pointer',
    userSelect: 'none' as const,
  },
  smallerForm: {
    fontSize: '0.9rem',
    transition: 'all 0.3s ease',
  }
};

export interface IFormData {
  nombreRecinto: string;
  perfilOcupacion: number;
  alturaPromedio: string;
  sensorCo2: boolean;
  levelId: number | null;
}

const LOCAL_STORAGE_KEY = "recintoFormData";

const RecintoEdit: React.FC = () => {
  const [projectName, setProjectName] = useState<string>("Nombre del Proyecto");
  const [projectDepartment, setProjectDepartment] = useState<string>("Región");
  const [projectId, setProjectId] = useState<string>("");

  // ---------------------------
  //  Estados para los campos del formulario restantes
  // ---------------------------
  const [nombreRecinto, setNombreRecinto] = useState<string>("");
  const [perfilOcupacion, setPerfilOcupacion] = useState<number>(0);
  const [alturaPromedio, setAlturaPromedio] = useState<string>(""); // Se enviará como número
  const [sensorCo2, setSensorCo2] = useState<boolean>(false);
  const [levelId, setLevelId] = useState<number | null>(1);
  const [enclosureProfiles, setEnclosureProfiles] = useState<
    { id: number; name: string }[]
  >([]);

  // Estado para controlar las secciones colapsables
  const [isEdificacionExpanded, setIsEdificacionExpanded] = useState<boolean>(false); // Inicialmente colapsado
  const [isThermalExpanded, setIsThermalExpanded] = useState<boolean>(true); // Inicialmente expandido

  // Estados y funciones para el modal de detalles del perfil de ocupación
  const [showPerfilModal, setShowPerfilModal] = useState(false);
  const [perfilDetail, setPerfilDetail] = useState<any>(null);
  const [loadingPerfilDetail, setLoadingPerfilDetail] = useState(false);

  // Funciones para alternar la visibilidad de las secciones
  const toggleEdificacionSection = () => {
    setIsEdificacionExpanded(!isEdificacionExpanded);
  };

  const toggleThermalSection = () => {
    setIsThermalExpanded(!isThermalExpanded);
  };

  const handleShowPerfilDetail = async () => {
    if (!perfilOcupacion) return;
    setLoadingPerfilDetail(true);
    setShowPerfilModal(true);
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`${constantUrlApiEndpoint}/enclosure-typing-detail/${perfilOcupacion}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error("Error al obtener detalles del perfil");
      const data = await res.json();
      setPerfilDetail(data);
    } catch (e) {
      setPerfilDetail(null);
    } finally {
      setLoadingPerfilDetail(false);
    }
  };

  // ---------------------------
  //  Recuperar datos del proyecto y del formulario guardados en localStorage
  // ---------------------------
  useEffect(() => {
    const name = localStorage.getItem("project_name_edit") || "Nombre del Proyecto";
    const department = localStorage.getItem("project_department_edit") || "Región";
    const pid = localStorage.getItem("project_id") || "";
    console.log("PROJECT ID: ", pid)
    setProjectName(name);
    setProjectDepartment(department);
    setProjectId(pid);

    const savedFormData = localStorage.getItem(LOCAL_STORAGE_KEY);
    if (savedFormData) {
      const data: IFormData = JSON.parse(savedFormData);
      setNombreRecinto(data.nombreRecinto);
      setPerfilOcupacion(data.perfilOcupacion);
      setAlturaPromedio(data.alturaPromedio);
      setSensorCo2(data.sensorCo2);
      setLevelId(data.levelId);
    }
  }, []);

  // ---------------------------
  //  Guardar cambios del formulario en localStorage
  // ---------------------------
  useEffect(() => {
    const formData: IFormData = {
      nombreRecinto,
      perfilOcupacion,
      alturaPromedio,
      sensorCo2,
      levelId,
    };
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(formData));
  }, [nombreRecinto, perfilOcupacion, alturaPromedio, sensorCo2, levelId]);

  // ---------------------------
  //  useEffect para cargar Perfiles de ocupación (desplegable)
  // ---------------------------
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) return;

    const fetchProfiles = async () => {
      try {
        const response = await fetch(
          `${constantUrlApiEndpoint}/user/enclosures-typing/`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );
        if (!response.ok) {
          throw new Error("Error al cargar los perfiles de ocupación");
        }
        const data = await response.json();
        setEnclosureProfiles(data);
      } catch (error) {
        console.error(error);
      }
    };

    fetchProfiles();
  }, []);

  const handleSave = async () => {
    // Se reemplaza la coma por el punto para convertir correctamente el valor a número
    const altura = parseFloat(alturaPromedio.replace(",", "."));
    if (
      !nombreRecinto.trim() ||
      !perfilOcupacion ||
      !alturaPromedio.trim() ||
      isNaN(altura) ||
      altura <= 0
    ) {
      notify(
        "Por favor, complete todos los campos requeridos y asegúrese de que la altura sea un número positivo"
      );
      return;
    }

    try {
      const token = localStorage.getItem("token");
      if (!token) {
        return;
      }

      const recintoId = localStorage.getItem("recinto_id");
      if (!recintoId) {
        notify("ID del recinto no encontrado");
        return;
      }

      const payload = {
        name_enclosure: nombreRecinto,
        occupation_profile_id: perfilOcupacion,
        height: altura,
        co2_sensor: sensorCo2 ? "Si" : "No",
        level_id: levelId,
      };

      console.log("Payload a enviar:", payload);

      const response = await fetch(
        `${constantUrlApiEndpoint}/enclosure-generals-update/${projectId}/${recintoId}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            accept: "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(payload),
        }
      );

      const result = await response.json();
      console.log("Status del response:", response.status);
      console.log("Respuesta del servidor:", result);

      if (!response.ok) {
        notify(result.detail || "Error al actualizar los datos");
        return;
      }

      notify("Recinto actualizado correctamente");

      // Colapsar la sección de edificación después de actualizar
      setIsEdificacionExpanded(false);

      // Mostrar la sección de características térmicas expandida
      setIsThermalExpanded(true);
    } catch (error) {
      console.error("Error en handleSave:", error);
      notify("Error al actualizar los datos");
    }
  };

  // Función para limpiar el formulario y localStorage
  const handleCrearOtroRecinto = () => {
    setNombreRecinto("");
    setPerfilOcupacion(0);
    setAlturaPromedio("");
    setSensorCo2(false);
    setLevelId(1);
    localStorage.removeItem(LOCAL_STORAGE_KEY);
    localStorage.removeItem('recinto_id');
    window.location.reload();
  };

  const route = useRouter()
  const handleBack = () => {
    route.push("workflow-part2-edit?step=4")
  };

  return (
    <>
      {/* Card del título y encabezado del proyecto con Breadcrumb alineado a la derecha */}
      <Card>
        <div>
          <Title text="Edición de Recinto" />
          <div className="d-flex justify-content-between align-items-center">
            <ProjectInfoHeader
              projectName={projectName}
              region={projectDepartment}
              project_id={projectId ?? ""}
            />
            <Breadcrumb
              items={[
                { title: "Inicio", href: "/" },
                { title: "Editar Recinto", href: "/recinto-edit" },
              ]}
            />
          </div>
        </div>
      </Card>

      {/* Card con los campos restantes "Características de la edificación" - Collapsible */}
      <Card>
        <div>
          <div className="d-flex justify-content-between align-items-center" 
               style={styles.collapsibleHeader} 
               onClick={toggleEdificacionSection}>
            <Title text="Características de la edificación" />
            <button className="btn btn-link p-0">
              <i className={`bi ${isEdificacionExpanded ? 'bi-chevron-up' : 'bi-chevron-down'}`}></i>
            </button>
          </div>

          {isEdificacionExpanded && (
            <>
              <div className="row mt-4" style={styles.smallerForm}>
                {/* Campo: Nombre Recinto */}
                <div className="col-6 mb-3">
                  <label htmlFor="nombreRecinto" className="form-label">
                    Nombre Recinto
                  </label>
                  <input
                    id="nombreRecinto"
                    type="text"
                    className="form-control"
                    placeholder="Ej: Sala 1"
                    value={nombreRecinto}
                    onChange={(e) => setNombreRecinto(e.target.value)}
                  />
                </div>

                {/* Campo: Perfil de Ocupación */}
                <div className="col-6 mb-3 d-flex align-items-end">
                  <div className="flex-grow-1">
                    <label htmlFor="perfilOcupacion" className="form-label">
                      Tipologías del recinto
                    </label>
                    <select
                      id="perfilOcupacion"
                      className="form-select"
                      value={perfilOcupacion || ""}
                      onChange={(e) =>
                        setPerfilOcupacion(parseInt(e.target.value))
                      }
                    >
                      <option value="">Seleccione un perfil de ocupación</option>
                      {enclosureProfiles.map((profile) => (
                        <option key={profile.id} value={profile.id}>
                          {profile.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <i
                    className="bi bi-info-circle ms-2 mb-1"
                    style={{ fontSize: '1.5rem', cursor: perfilOcupacion ? 'pointer' : 'not-allowed', color: perfilOcupacion ? '#0dcaf0' : '#adb5bd' }}
                    title="Ver detalles del perfil de ocupación"
                    onClick={perfilOcupacion ? handleShowPerfilDetail : undefined}
                  ></i>
                </div>

                {/* Campo: Altura Promedio Recinto */}
                <div className="col-6 mb-3">
                  <label htmlFor="alturaPromedio" className="form-label">
                    Altura Promedio Recinto (m)
                  </label>
                  <input
                    id="alturaPromedio"
                    type="text"
                    className="form-control"
                    placeholder="Ej: 2.5 (en metros)"
                    value={alturaPromedio}
                    onChange={(e) => {
                      const value = e.target.value;
                      // Solo se permiten los dígitos 0-9, el punto y la coma
                      const regex = /^[0-9.,]*$/;
                      if (regex.test(value)) {
                        setAlturaPromedio(value);
                      }
                    }}
                  />
                </div>

                {/* Campo: Nivel de Recinto */}
                <div className="col-6 mb-3">
                  <label htmlFor="levelId" className="form-label">
                    Nivel de Recinto
                  </label>
                  <input
                    id="levelId"
                    type="number"
                    className="form-control"
                    placeholder="Ej: 1"
                    min="1"
                    value={levelId || ''}
                    onChange={(e) => {
                      const value = e.target.value;
                      setLevelId(value ? parseInt(value) : null);
                    }}
                  />
                </div>

                {/* Campo: Sensor CO2 */}
                <div className="col-6 mb-3">
                  <label htmlFor="sensorCo2" className="form-label">
                    Sensor CO2
                  </label>
                  <select
                    id="sensorCo2"
                    className="form-select"
                    value={sensorCo2 ? "Si" : "No"}
                    onChange={(e) => setSensorCo2(e.target.value === "Si")}
                  >
                    <option value="Si">Si</option>
                    <option value="No">No</option>
                  </select>
                </div>
              </div>

            </>
          )}
              {/* Botones: Regresar a la izquierda y Actualizar Datos a la derecha */}
              <div className="d-flex justify-content-between align-items-center">
                <CustomButton variant="back" onClick={handleBack}>
                  <ArrowLeft className="me-2" size={18} />
                  Regresar
                </CustomButton>
                
                <div>
                  <CustomButton onClick={handleCrearOtroRecinto} className="me-2" color="orange">
                    <Plus className="me-2" size={18} />
                    Crear otro recinto
                  </CustomButton>
                  <CustomButton variant="save" onClick={handleSave}>
                    <Save className="me-2" size={18} color="white"/>
                    Actualizar Datos
                  </CustomButton>
                </div>
              </div>
        </div>
      </Card>

      {/* Card para "Características térmicas de la envolvente" - Collapsible */}
      <Card>
        <div>
          <div className="d-flex justify-content-between align-items-center"
               style={styles.collapsibleHeader}
               onClick={toggleThermalSection}>
            <Title text="Características térmicas de la envolvente" />
            <button className="btn btn-link p-0">
              <i className={`bi ${isThermalExpanded ? 'bi-chevron-up' : 'bi-chevron-down'}`}></i>
            </button>
          </div>
          {isThermalExpanded && (
            <div className="mt-2">
              <RecintoCaractersComponent />
            </div>
          )}
        </div>
      </Card>

      {/* Modal para mostrar detalles del perfil de ocupación */}
      {showPerfilModal && (
        <div className="modal fade show" tabIndex={-1} style={{ display: 'block' }}>
          <div className="modal-dialog modal-lg">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Detalles del Perfil de Ocupación (horas/día)</h5>
                <button type="button" className="btn-close" onClick={() => setShowPerfilModal(false)}></button>
              </div>
              <div className="modal-body">
                {loadingPerfilDetail ? (
                  <div className="text-center">
                    <div className="spinner-border" role="status">
                      <span className="visually-hidden">Cargando...</span>
                    </div>
                  </div>
                ) : perfilDetail ? (
                  <div>
                    {/* Ventilación */}
                    <h6>Ventilación</h6>
                    <ul>
                      <li><strong>Infiltraciones:</strong> {perfilDetail.ventilation_flows?.infiltraciones !== undefined ? Number(perfilDetail.ventilation_flows.infiltraciones).toFixed(2) : '-'} 1/h</li>
                    <li><strong>Ventilación nocturna:</strong> {perfilDetail.ventilation_flows?.caudal_impuesto?.vent_noct !== undefined ? Number(perfilDetail.ventilation_flows.caudal_impuesto.vent_noct).toFixed(2) : '-'} m³/h</li>
                    <li><strong>Recuperador de calor:</strong> {perfilDetail.ventilation_flows?.recuperador_calor !== undefined ? Number(perfilDetail.ventilation_flows.recuperador_calor).toFixed(2) : '-'} %</li>
                    <li><strong>IDA:</strong> {perfilDetail.ventilation_flows?.cauldal_min_salubridad?.ida ?? '-'} l/s·persona</li>
                    <li><strong>R. pers:</strong> {perfilDetail.ventilation_flows?.cauldal_min_salubridad?.r_pers !== undefined ? Number(perfilDetail.ventilation_flows.cauldal_min_salubridad.r_pers).toFixed(2) : '-'} m²/persona</li>
                    <li><strong>Ocupación:</strong> {perfilDetail.ventilation_flows?.cauldal_min_salubridad?.ocupacion ?? '-'} </li>
                    </ul>
                    {/* Iluminación */}
                    <h6>Iluminación</h6>
                    <ul>
                      <li><strong>Estrategia:</strong> {perfilDetail.lightning?.estrategia ?? '-'}</li>
                      <li><strong>Potencia base:</strong> {perfilDetail.lightning?.potencia_base !== undefined ? Number(perfilDetail.lightning.potencia_base).toFixed(2) : '-'} W/m²</li>
                    <li><strong>Potencia propuesta:</strong> {perfilDetail.lightning?.potencia_propuesta !== undefined ? Number(perfilDetail.lightning.potencia_propuesta).toFixed(2) : '-'} W/m²</li>
                    </ul>
                    {/* Cargas internas */}
                    <h6>Cargas internas</h6>
                    <ul>
                      <li><strong>Equipos:</strong> {perfilDetail.internal_loads?.equipos !== undefined ? Number(perfilDetail.internal_loads.equipos).toFixed(2) : '-'} W/m²</li>
                      <li><strong>Usuarios:</strong> {perfilDetail.internal_loads?.usuarios !== undefined ? Number(perfilDetail.internal_loads.usuarios).toFixed(2) : '-'} W/persona</li>
                    <li><strong>Calor latente:</strong> {perfilDetail.internal_loads?.calor_latente !== undefined ? Number(perfilDetail.internal_loads.calor_latente).toFixed(2) : '-'} W/persona</li>
                      <li><strong>Calor sensible:</strong> {perfilDetail.internal_loads?.calor_sensible !== undefined ? Number(perfilDetail.internal_loads.calor_sensible).toFixed(2) : '-'} W/persona</li>
                    <li><strong>Horario laboral:</strong> {perfilDetail.internal_loads?.horario?.laboral?.inicio !== undefined && perfilDetail.internal_loads?.horario?.laboral?.fin !== undefined ? `${perfilDetail.internal_loads.horario.laboral.inicio} - ${perfilDetail.internal_loads.horario.laboral.fin}` : '-'} horas</li>
                      <li><strong>Funcionamiento semanal:</strong> {perfilDetail.internal_loads?.horario?.funcionamiento_semanal ?? '-'}</li>
                    </ul>
                    {/* Clima y programación */}
                    <h6>Clima y programación</h6>
                    <ul>
                      <li><strong>Climatizado:</strong> {perfilDetail.schedule_weather?.recinto?.climatizado ?? '-'}</li>
                      <li><strong>Desfase clima:</strong> {perfilDetail.schedule_weather?.recinto?.desfase_clima !== undefined ? Number(perfilDetail.schedule_weather.recinto.desfase_clima).toFixed(2) : '-'}</li>
                    </ul>
                  </div>
                ) : (
                  <p>No se encontraron detalles para este perfil de ocupación.</p>
                )}
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowPerfilModal(false)}>
                  Cerrar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default RecintoEdit;
