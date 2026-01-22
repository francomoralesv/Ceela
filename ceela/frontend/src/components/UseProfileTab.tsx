import ActionButtons from "@/components/common/ActionButtons";
import ActionButtonsConfirm from "@/components/common/ActionButtonsConfirm";
import CustomButton from "@/components/common/CustomButton";
import HorizontalTabs from "@/components/common/HorizontalTabs";
import Profileschedules from "@/components/common/Profileschedules";
import SearchParameters from "@/components/inputs/SearchParameters";
import TablesParameters from "@/components/tables/TablesParameters";
import { notify } from "@/utils/notify";
import axios from "axios";
import React, { useEffect, useState } from "react";
import ModalCreate from "../components/common/ModalCreate";
import { constantUrlApiEndpoint } from "../utils/constant-url-endpoint";

// Interfaces originales de datos (como vienen de la API)
interface Ventilacion {
  id: string;
  code: string;
  name: string;
  building_conditions: any[];
}

interface Iluminacion {
  id: string;
  code: string;
  name: string;
  building_conditions: any[];
}

interface CargasInternas {
  id: string;
  code: string;
  name: string;
  building_conditions: any[];
}

interface HorarioClima {
  id: string;
  code: string;
  name: string;
  building_conditions: any[];
}

// Tipos para las pestañas
type TabKey = "ventilacion" | "iluminacion" | "cargas" | "horario";

// Tipo para la fila en edición
interface EditingRow {
  id: string;
  tab: TabKey;
  values: any;
  original: any;
}

// Interfaz para el item a eliminar
interface ItemToDelete {
  id: string;
  name: string;
  tab: TabKey;
}

const UseProfileTab: React.FC<{
  refreshTrigger?: number;
  primaryColorProp?: string;
}> = ({ refreshTrigger = 0, primaryColorProp }) => {
  const [primaryColor, setPrimaryColor] = useState("#3ca7b7");
  const [activeTab, setActiveTab] = useState<TabKey>("ventilacion");
  const [rolUser, setRolUser] = useState<string>("");

  // Estados para almacenar datos crudos (raw) de cada pestaña
  const [ventilacionRaw, setVentilacionRaw] = useState<Ventilacion[]>([]);
  const [iluminacionRaw, setIluminacionRaw] = useState<Iluminacion[]>([]);
  const [cargasRaw, setCargasRaw] = useState<CargasInternas[]>([]);
  const [horarioRaw, setHorarioRaw] = useState<HorarioClima[]>([]);

  // Estados de búsqueda para cada pestaña
  const [searchVentilacion, setSearchVentilacion] = useState("");
  const [searchIluminacion, setSearchIluminacion] = useState("");
  const [searchCargas, setSearchCargas] = useState("");
  const [searchHorario, setSearchHorario] = useState("");

  // Estado para el modal de creación
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [newRecintoName, setNewRecintoName] = useState("");

  // Estado para el modal de eliminación
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [itemToDelete, setItemToDelete] = useState<ItemToDelete | null>(null);

  // Estado para refrescar las tablas
  const [refresh, setRefresh] = useState(0);

  // Estado para llevar el registro de la fila que se está editando
  const [editingRow, setEditingRow] = useState<EditingRow | null>(null);

  // Nuevo estado para el modal de Profileschedules
  const [isProfileSchedulesModalOpen, setIsProfileSchedulesModalOpen] =
    useState(false);

  // Función auxiliar para formatear los valores mostrados en las tablas.
  // Si el valor es "N/A" o equivale a 0, se retorna un guion ("-").
  const formatDisplayValue = (value: any): string => {
    if (value === "N/A") return "-";
    const num = parseFloat(value);
    if (!isNaN(num) && num === 0) return "-";
    return value;
  };

  // Función para abrir el modal de creación
  const handleNuevoClick = (tab: TabKey) => {
    setIsCreateModalOpen(true);
  };

  // Función para abrir el modal de eliminación
  const handleDeleteClick = (tab: TabKey, id: string, name: string) => {
    setItemToDelete({ id, name, tab });
    setIsDeleteModalOpen(true);
  };

  // Función para realizar el DELETE y eliminar un recinto
  const handleDeleteConfirm = async () => {
    if (!itemToDelete) return;

    const token = localStorage.getItem("token");
    if (!token || !rolUser) return;

    const url = `${constantUrlApiEndpoint}/enclosures-typing/${itemToDelete.id}/delete?section=${rolUser}`;
    const headers = {
      accept: "application/json",
      Authorization: `Bearer ${token}`,
    };

    try {
      await axios.delete(url, { headers });
      notify("Recinto eliminado exitosamente");
      setIsDeleteModalOpen(false);
      setItemToDelete(null);
      setRefresh((prev) => prev + 1);
    } catch (error: any) {
      setIsDeleteModalOpen(false);
      if (
        error.response &&
        error.response.data &&
        error.response.data.detail === "No se encontró la tipología de recinto"
      ) {
        notify(
          "No se puede eliminar un recinto por defecto o creado por el admin"
        );
      }
    }
  };

  // Función para realizar el POST y crear un nuevo recinto
  const handleCreateSave = () => {
    const token = localStorage.getItem("token");
    if (!token || !rolUser) return;
    const url = `${constantUrlApiEndpoint}/${rolUser}/enclosures-typing-create/`;
    fetch(url, {
      method: "POST",
      headers: {
        accept: "application/json",
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ name: newRecintoName }),
    })
      .then((res) => {
        if (!res.ok) {
          return res.json().then((errorData) => {
            throw errorData;
          });
        }
        return res.json();
      })
      .then((data) => {
        notify("Recinto creado exitosamente");
        setIsCreateModalOpen(false);
        setNewRecintoName("");
        setRefresh((prev) => prev + 1);
      })
      .catch((err) => {
        if (
          err.detail ===
          "Error al crear tipo de recinto: El nombre debe tener al menos dos caracteres"
        ) {
          notify("El Nombre del recinto debe contener al menos 2 letras");
        } else {
          console.error("Error al crear recinto", err);
        }
      });
  };

  // Función para obtener un valor CSS
  const getCssVarValue = (varName: string, fallback: string): string => {
    if (typeof window === "undefined") return fallback;
    const value = getComputedStyle(document.documentElement)
      .getPropertyValue(varName)
      .trim();
    return value || fallback;
  };

  // Se ejecuta una sola vez para obtener el rol del usuario y el color primario
  useEffect(() => {
    setPrimaryColor(
      primaryColorProp || getCssVarValue("--primary-color", "#3ca7b7")
    );
    const roleId = localStorage.getItem("role_id");
    if (roleId === "1") {
      setRolUser("admin");
    } else if (roleId === "2") {
      setRolUser("user");
    }
  }, [primaryColorProp]);

  // 1. Ventilación y caudales
  useEffect(() => {
    if (!rolUser) return;
    const token = localStorage.getItem("token");
    const url = `${constantUrlApiEndpoint}/${rolUser}/enclosures-typing/?type=ventilation_flows`;
    fetch(url, { headers: { Authorization: `Bearer ${token}` } })
      .then((res) => res.json())
      .then((data) => {
        let enclosures: any[] = [];
        if (Array.isArray(data)) {
          enclosures = data;
        } else if (Array.isArray(data.results)) {
          enclosures = data.results;
        } else {
          console.error("Formato de respuesta no esperado:", data);
        }
        setVentilacionRaw(enclosures);
      })
      .catch((err) => console.error("Error al obtener ventilacion:", err));
  }, [rolUser, refresh, refreshTrigger]);

  // 2. Iluminación
  useEffect(() => {
    if (!rolUser) return;
    const token = localStorage.getItem("token");
    const url = `${constantUrlApiEndpoint}/${rolUser}/enclosures-typing/?type=lightning`;
    fetch(url, { headers: { Authorization: `Bearer ${token}` } })
      .then((res) => res.json())
      .then((data) => {
        let enclosures: any[] = [];
        if (Array.isArray(data)) {
          enclosures = data;
        } else if (Array.isArray(data.results)) {
          enclosures = data.results;
        } else {
          console.error("Formato de respuesta no esperado:", data);
        }
        setIluminacionRaw(enclosures);
      })
      .catch((err) => console.error("Error al obtener iluminacion:", err));
  }, [rolUser, refresh, refreshTrigger]);

  // 3. Cargas internas
  useEffect(() => {
    if (!rolUser) return;
    const token = localStorage.getItem("token");
    const url = `${constantUrlApiEndpoint}/${rolUser}/enclosures-typing/?type=internal_loads`;
    fetch(url, { headers: { Authorization: `Bearer ${token}` } })
      .then((res) => res.json())
      .then((data) => {
        let enclosures: any[] = [];
        if (Array.isArray(data)) {
          enclosures = data;
        } else if (Array.isArray(data.results)) {
          enclosures = data.results;
        } else {
          console.error("Formato de respuesta no esperado:", data);
        }
        setCargasRaw(enclosures);
      })
      .catch((err) => console.error("Error al obtener cargas internas:", err));
  }, [rolUser, refresh, refreshTrigger]);

  // 4. Horario y Clima
  useEffect(() => {
    if (!rolUser) return;
    const token = localStorage.getItem("token");
    const url = `${constantUrlApiEndpoint}/${rolUser}/enclosures-typing/?type=schedule_weather`;
    fetch(url, { headers: { Authorization: `Bearer ${token}` } })
      .then((res) => res.json())
      .then((data) => {
        let enclosures: any[] = [];
        if (Array.isArray(data)) {
          enclosures = data;
        } else if (Array.isArray(data.results)) {
          enclosures = data.results;
        } else {
          console.error("Formato de respuesta no esperado:", data);
        }
        setHorarioRaw(enclosures);
      })
      .catch((err) => console.error("Error al obtener horario y clima:", err));
  }, [rolUser, refresh, refreshTrigger]);

  // Handlers para edición
  const handleStartEdit = (tab: TabKey, enclosure: any, initialValues: any) => {
    console.log("Iniciando edición del enclosure con id:", enclosure.id);
    setEditingRow({
      id: enclosure.id,
      tab,
      values: {
        ...initialValues,
        rPers: (
          enclosure.building_conditions[0]?.details?.cauldal_min_salubridad
            ?.r_pers ?? 0
        ).toFixed(2),
      },
      original: enclosure,
    });
  };

  const handleEditChange = (field: string, value: any) => {
    setEditingRow((prev) =>
      prev ? { ...prev, values: { ...prev.values, [field]: value } } : null
    );
  };

  const handleCancelEdit = () => {
    setEditingRow(null);
  };

  // Función para guardar la edición, construyendo el payload según la pestaña
  const handleSave = (tab: TabKey, enclosure: any) => {
    if (!editingRow) return;
    const token = localStorage.getItem("token");
    if (!token) return;

    let payload: any = {};
    if (tab === "ventilacion") {
      payload = {
        type: "ventilation_flows",
        attributes: {
          cauldal_min_salubridad: {
            ida: editingRow.values.ida,
            ocupacion: editingRow.values.ocupacion,
          },
          caudal_impuesto: {
            vent_noct: parseFloat(editingRow.values.caudalImpuestoVentNoct),
          },
          infiltraciones: parseFloat(editingRow.values.infiltraciones),
          recuperador_calor: parseFloat(editingRow.values.recuperadorCalor),
        },
      };
    } else if (tab === "iluminacion") {
      payload = {
        type: "lightning",
        attributes: {
          potencia_base: parseFloat(editingRow.values.potenciaBase),
          estrategia: editingRow.values.estrategia,
          potencia_propuesta: parseFloat(editingRow.values.potenciaPropuesta),
        },
      };
    } else if (tab === "cargas") {
      payload = {
        type: "internal_loads",
        attributes: {
          usuarios: parseFloat(editingRow.values.usuarios),
          calor_latente: parseFloat(editingRow.values.calorLatente),
          calor_sensible: parseFloat(editingRow.values.calorSensible),
          equipos: parseFloat(editingRow.values.equipos),
          horario: {
            funcionamiento_semanal: editingRow.values.funcionamientoSemanal,
            laboral: {
              inicio: parseFloat(editingRow.values.laboralInicio),
              fin: parseFloat(editingRow.values.laboralFin),
            },
          },
        },
      };
    } else if (tab === "horario") {
      payload = {
        type: "schedule_weather",
        attributes: {
          recinto: {
            climatizado: editingRow.values.climatizado,
            desfase_clima: parseFloat(editingRow.values.hrsDesfaseClimaInv),
          },
        },
      };
    }

    const url = `${constantUrlApiEndpoint}/building_condition/${enclosure.id}/update?section=${rolUser}`;

    fetch(url, {
      method: "PATCH",
      headers: {
        accept: "application/json",
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    })
      .then((res) => res.json())
      .then((data) => {
        notify("Actualizado con éxito.");
        setEditingRow(null);
        setRefresh((prev) => prev + 1);
      })
      .catch((err) => console.error("Error en actualización:", err));
  };

  // Funciones para construir cada fila de tabla según el tipo de dato
  const mapVentilacionRow = (enclosure: any) => {
    const isDefault =
      enclosure.building_conditions[0]?.created_status === "default" ||
      enclosure.building_conditions[0]?.created_status === "cloned";
    const condition = enclosure.building_conditions[0]?.details || {};
    const minSalubridad = condition.cauldal_min_salubridad || {};
    const isEditing =
      editingRow &&
      editingRow.id === enclosure.id &&
      editingRow.tab === "ventilacion";
    const rPersValue = (minSalubridad.r_pers ?? 0).toFixed(2);
    const values = isEditing
      ? editingRow.values
      : {
        rPers: rPersValue,
        ida: minSalubridad.ida || "N/A",
        ocupacion: minSalubridad.ocupacion || "N/A",
        caudalImpuestoVentNoct: (
          condition.caudal_impuesto?.vent_noct ?? 0
        ).toFixed(2),
        infiltraciones: (condition.infiltraciones ?? 0).toFixed(2),
        recuperadorCalor: condition.recuperador_calor ?? 0,
      };
    return {
      code_ifc: enclosure.code_ifc || "-",
      codigoRecinto: !isDefault ? (
        <span style={{ color: primaryColor, fontWeight: "bold" }}>
          {enclosure.code}
        </span>
      ) : (
        enclosure.code
      ),
      tipologiaRecinto: !isDefault ? (
        <span style={{ color: primaryColor, fontWeight: "bold" }}>
          {enclosure.name}
        </span>
      ) : (
        enclosure.name
      ),
      rPers: !isDefault ? (
        <span style={{ color: primaryColor, fontWeight: "bold" }}>
          {formatDisplayValue(rPersValue)}
        </span>
      ) : (
        formatDisplayValue(rPersValue)
      ),
      ida: isEditing ? (
        <select
          className="form-control form-control-sm"
          value={editingRow.values.ida}
          onChange={(e) => handleEditChange("ida", e.target.value)}
        >
          <option value="IDA1">IDA1</option>
          <option value="IDA2">IDA2</option>
          <option value="IDA3">IDA3</option>
        </select>
      ) : !isDefault ? (
        <span style={{ color: primaryColor, fontWeight: "bold" }}>
          {formatDisplayValue(values.ida)}
        </span>
      ) : (
        formatDisplayValue(values.ida)
      ),
      ocupacion: isEditing ? (
        <select
          className="form-control form-control-sm"
          value={editingRow.values.ocupacion}
          onChange={(e) => handleEditChange("ocupacion", e.target.value)}
        >
          <option value="Ejercicio Bajo">Ejercicio Bajo</option>
          <option value="Ejercicio Medio">Ejercicio Medio</option>
          <option value="Ejercicio Alto">Ejercicio Alto</option>
          <option value="Jardin Infantil">Jardin Infantil</option>
          <option value="Colegio">Colegio</option>
          <option value="Sedentario">Sedentario</option>
        </select>
      ) : !isDefault ? (
        <span style={{ color: primaryColor, fontWeight: "bold" }}>
          {formatDisplayValue(values.ocupacion)}
        </span>
      ) : (
        formatDisplayValue(values.ocupacion)
      ),
      caudalImpuestoVentNoct: isEditing ? (
        <input
          type="number"
          min="0"
          className="form-control form-control-sm"
          value={editingRow.values.caudalImpuestoVentNoct}
          onChange={(e) => {
            if (e.target.value.startsWith("-") || e.target.value === "-")
              return;
            handleEditChange("caudalImpuestoVentNoct", e.target.value);
          }}
          onKeyDown={(e) => {
            if (e.key === "-") e.preventDefault();
          }}
        />
      ) : !isDefault ? (
        <span style={{ color: primaryColor, fontWeight: "bold" }}>
          {formatDisplayValue(values.caudalImpuestoVentNoct)}
        </span>
      ) : (
        formatDisplayValue(values.caudalImpuestoVentNoct)
      ),
      // Nueva columna: Infiltraciones [1/h]
      infiltraciones:
        isEditing && !isDefault ? (
          <input
            type="number"
            min="0"
            className="form-control form-control-sm"
            value={editingRow.values.infiltraciones}
            onChange={(e) => {
              if (e.target.value.startsWith("-") || e.target.value === "-")
                return;
              handleEditChange("infiltraciones", e.target.value);
            }}
            onKeyDown={(e) => {
              if (e.key === "-") e.preventDefault();
            }}
          />
        ) : isDefault ? (
          formatDisplayValue(values.infiltraciones)
        ) : (
          <span style={{ color: primaryColor, fontWeight: "bold" }}>
            {formatDisplayValue(values.infiltraciones)}
          </span>
        ),

      // Nueva columna: Recuperador de calor [%]
      recuperadorCalor: isEditing ? (
        <input
          type="number"
          min="0"
          max="100"
          className="form-control form-control-sm"
          value={editingRow.values.recuperadorCalor}
          onChange={(e) => {
            const value = e.target.value;
            if (value.startsWith("-") || value === "-") return;
            const numericValue = parseFloat(value);
            if (numericValue > 100) return; // Limita a 100
            handleEditChange("recuperadorCalor", value);
          }}
          onKeyDown={(e) => {
            if (e.key === "-" || e.key === "e") e.preventDefault();
          }}
        />
      ) : !isDefault ? (
        <span style={{ color: primaryColor, fontWeight: "bold" }}>
          {formatDisplayValue(values.recuperadorCalor)}
        </span>
      ) : (
        formatDisplayValue(values.recuperadorCalor)
      ),
      accion: isEditing ? (
        <ActionButtonsConfirm
          onAccept={() => handleSave("ventilacion", enclosure)}
          onCancel={handleCancelEdit}
        />
      ) : (
        <ActionButtons
          onEdit={() =>
            handleStartEdit("ventilacion", enclosure, {
              ida: minSalubridad.ida || "",
              ocupacion: minSalubridad.ocupacion || "",
              caudalImpuestoVentNoct: condition.caudal_impuesto?.vent_noct || 0,
              infiltraciones: condition.infiltraciones || 0,
              recuperadorCalor: condition.recuperador_calor || 0,
            })
          }
          onDelete={() =>
            handleDeleteClick("ventilacion", enclosure.id, enclosure.name)
          }
        />
      ),
    };
  };

  const mapIluminacionRow = (enclosure: any) => {
    const isDefault =
      enclosure.building_conditions[0]?.created_status === "default" ||
      enclosure.building_conditions[0]?.created_status === "cloned";
    const condition = enclosure.building_conditions.find(
      (cond: any) => cond.type === "lightning"
    );
    const details = condition ? condition.details : {};
    const isEditing =
      editingRow &&
      editingRow.id === enclosure.id &&
      editingRow.tab === "iluminacion";
    const values = isEditing
      ? editingRow.values
      : {
        potenciaBase: (details.potencia_base ?? 0).toFixed(2),
        estrategia: details.estrategia || "",
        potenciaPropuesta: (details.potencia_propuesta ?? 0).toFixed(2),
      };

    return {
      code_ifc: enclosure.code_ifc || "-",
      codigoRecinto: !isDefault ? (
        <span style={{ color: primaryColor, fontWeight: "bold" }}>
          {enclosure.code}
        </span>
      ) : (
        enclosure.code
      ),
      tipologiaRecinto: !isDefault ? (
        <span style={{ color: primaryColor, fontWeight: "bold" }}>
          {enclosure.name}
        </span>
      ) : (
        enclosure.name
      ),
      potenciaBase:
        isEditing && !isDefault ? (
          <input
            type="number"
            min="0"
            className="form-control form-control-sm"
            value={editingRow?.values.potenciaBase}
            onChange={(e) => {
              if (e.target.value.startsWith("-") || e.target.value === "-")
                return;
              handleEditChange("potenciaBase", e.target.value);
            }}
            onKeyDown={(e) => {
              if (e.key === "-") e.preventDefault();
            }}
          />
        ) : (
          <span
            style={
              !isDefault ? { color: primaryColor, fontWeight: "bold" } : {}
            }
          >
            {formatDisplayValue(values.potenciaBase)}
          </span>
        ),
      estrategia: isEditing ? (
        <select
          className="form-control form-control-sm"
          value={editingRow?.values.estrategia}
          onChange={(e) => handleEditChange("estrategia", e.target.value)}
        >
          <option value="Sin estrategia">Sin estrategia</option>
          <option value="Dimmer">Dimmer</option>
          <option value="Sectorizacion">Sectorizacion</option>
          <option value="Sensor de Luz Nat">Sensor de Luz Nat</option>
        </select>
      ) : !isDefault ? (
        <span style={{ color: primaryColor, fontWeight: "bold" }}>
          {formatDisplayValue(values.estrategia)}
        </span>
      ) : (
        formatDisplayValue(values.estrategia)
      ),
      potenciaPropuesta: !isDefault ? (
        <span style={{ color: primaryColor, fontWeight: "bold" }}>
          {formatDisplayValue(values.potenciaPropuesta)}
        </span>
      ) : (
        formatDisplayValue(values.potenciaPropuesta)
      ),
      accion: isEditing ? (
        <ActionButtonsConfirm
          onAccept={() => handleSave("iluminacion", enclosure)}
          onCancel={handleCancelEdit}
        />
      ) : (
        <ActionButtons
          onEdit={() =>
            handleStartEdit("iluminacion", enclosure, {
              potenciaBase: details.potencia_base || 0,
              estrategia: details.estrategia || "",
              potenciaPropuesta: details.potencia_propuesta || 0,
            })
          }
          onDelete={() =>
            handleDeleteClick("iluminacion", enclosure.id, enclosure.name)
          }
        />
      ),
    };
  };

  const mapCargasRow = (enclosure: any) => {
    const isDefault =
      enclosure.building_conditions[0]?.created_status === "default" ||
      enclosure.building_conditions[0]?.created_status === "cloned";
    const condition = enclosure.building_conditions[0]?.details || {};
    const isEditing =
      editingRow &&
      editingRow.id === enclosure.id &&
      editingRow.tab === "cargas";
    const values = isEditing
      ? editingRow.values
      : {
        usuarios: (condition.usuarios ?? 0).toFixed(2),
        calorLatente: (condition.calor_latente ?? 0).toFixed(2),
        calorSensible: (condition.calor_sensible ?? 0).toFixed(2),
        equipos: (condition.equipos ?? 0).toFixed(2),
        funcionamientoSemanal:
          condition.horario?.funcionamiento_semanal || "",
      };

    return {
      code_ifc: enclosure.code_ifc || "-",
      codigoRecinto: !isDefault ? (
        <span style={{ color: primaryColor, fontWeight: "bold" }}>
          {enclosure.code}
        </span>
      ) : (
        enclosure.code
      ),
      tipologiaRecinto: !isDefault ? (
        <span style={{ color: primaryColor, fontWeight: "bold" }}>
          {enclosure.name}
        </span>
      ) : (
        enclosure.name
      ),
      // Para las siguientes columnas se muestra el input en modo edición solo si la fila no es default.
      usuarios:
        isEditing && !isDefault ? (
          <input
            type="number"
            min="0"
            className="form-control form-control-sm"
            value={editingRow.values.usuarios}
            onChange={(e) => {
              if (e.target.value.startsWith("-") || e.target.value === "-")
                return;
              handleEditChange("usuarios", e.target.value);
            }}
            onKeyDown={(e) => {
              if (e.key === "-") e.preventDefault();
            }}
          />
        ) : (
          <span
            style={
              !isDefault ? { color: primaryColor, fontWeight: "bold" } : {}
            }
          >
            {formatDisplayValue(values.usuarios)}
          </span>
        ),
      calorLatente:
        isEditing && !isDefault ? (
          <input
            type="number"
            min="0"
            className="form-control form-control-sm"
            value={editingRow.values.calorLatente}
            onChange={(e) => {
              if (e.target.value.startsWith("-") || e.target.value === "-")
                return;
              handleEditChange("calorLatente", e.target.value);
            }}
            onKeyDown={(e) => {
              if (e.key === "-") e.preventDefault();
            }}
          />
        ) : (
          <span
            style={
              !isDefault ? { color: primaryColor, fontWeight: "bold" } : {}
            }
          >
            {formatDisplayValue(values.calorLatente)}
          </span>
        ),
      calorSensible:
        isEditing && !isDefault ? (
          <input
            type="number"
            min="0"
            className="form-control form-control-sm"
            value={editingRow.values.calorSensible}
            onChange={(e) => {
              if (e.target.value.startsWith("-") || e.target.value === "-")
                return;
              handleEditChange("calorSensible", e.target.value);
            }}
            onKeyDown={(e) => {
              if (e.key === "-") e.preventDefault();
            }}
          />
        ) : (
          <span
            style={
              !isDefault ? { color: primaryColor, fontWeight: "bold" } : {}
            }
          >
            {formatDisplayValue(values.calorSensible)}
          </span>
        ),
      equipos:
        isEditing && !isDefault ? (
          <input
            type="number"
            min="0"
            className="form-control form-control-sm"
            value={editingRow.values.equipos}
            onChange={(e) => {
              if (e.target.value.startsWith("-") || e.target.value === "-")
                return;
              handleEditChange("equipos", e.target.value);
            }}
            onKeyDown={(e) => {
              if (e.key === "-") e.preventDefault();
            }}
          />
        ) : (
          <span
            style={
              !isDefault ? { color: primaryColor, fontWeight: "bold" } : {}
            }
          >
            {formatDisplayValue(values.equipos)}
          </span>
        ),
      funcionamientoSemanal: isEditing ? (
        <select
          className="form-control form-control-sm"
          value={editingRow.values.funcionamientoSemanal}
          onChange={(e) =>
            handleEditChange("funcionamientoSemanal", e.target.value)
          }
        >
          <option value="7x0">7x0</option>
          <option value="6x1">6x1</option>
          <option value="5x2">5x2</option>
          <option value="4x3">4x3</option>
          <option value="3x4">3x4</option>
          <option value="2x5">2x5</option>
          <option value="1x6">1x6</option>
          <option value="0x7">0x7</option>
        </select>
      ) : !isDefault ? (
        <span style={{ color: primaryColor, fontWeight: "bold" }}>
          {formatDisplayValue(values.funcionamientoSemanal)}
        </span>
      ) : (
        formatDisplayValue(values.funcionamientoSemanal)
      ),

      accion: isEditing ? (
        <ActionButtonsConfirm
          onAccept={() => handleSave("cargas", enclosure)}
          onCancel={handleCancelEdit}
        />
      ) : (
        <div style={{ display: "flex", gap: "5px", alignItems: "center" }}>
          <ActionButtons
            onEdit={() =>
              handleStartEdit("cargas", enclosure, {
                usuarios: condition.usuarios || 0,
                calorLatente: condition.calor_latente || 0,
                calorSensible: condition.calor_sensible || 0,
                equipos: condition.equipos || 0,
                funcionamientoSemanal:
                  condition.horario?.funcionamiento_semanal || "",
              })
            }
            onDelete={() =>
              handleDeleteClick("cargas", enclosure.id, enclosure.name)
            }
          />
            <CustomButton
              className="btn-table-list"
              onClick={() => {
                localStorage.setItem("perfil_id", enclosure.id);
                setIsProfileSchedulesModalOpen(true);
              }}
            >
              <i className="fa fa-clock-o"></i>
            </CustomButton>
        </div>
      ),
    };
  };

  const mapHorarioRow = (enclosure: any) => {
    const isDefault =
      enclosure.building_conditions[0]?.created_status === "default" ||
      enclosure.building_conditions[0]?.created_status === "cloned";
    const details = enclosure.building_conditions[0]?.details || {};
    const recinto = details.recinto || { climatizado: "N/A", desfase_clima: 0 };
    const isEditing =
      editingRow &&
      editingRow.id === enclosure.id &&
      editingRow.tab === "horario";
    const values = isEditing
      ? editingRow.values
      : {
        climatizado: recinto.climatizado,
        hrsDesfaseClimaInv: recinto.desfase_clima
          ? recinto.desfase_clima.toFixed(2)
          : "N/A",
      };

    return {
      code_ifc: enclosure.code_ifc || "-",

      codigoRecinto: !isDefault ? (
        <span style={{ color: primaryColor, fontWeight: "bold" }}>
          {enclosure.code}
        </span>
      ) : (
        enclosure.code
      ),
      tipologiaRecinto: !isDefault ? (
        <span style={{ color: primaryColor, fontWeight: "bold" }}>
          {enclosure.name}
        </span>
      ) : (
        enclosure.name
      ),
      climatizado: isEditing ? (
        <select
          className="form-control form-control-sm"
          value={editingRow.values.climatizado}
          onChange={(e) => handleEditChange("climatizado", e.target.value)}
        >
          <option value="Si">Si</option>
          <option value="No">No</option>
        </select>
      ) : !isDefault ? (
        <span style={{ color: primaryColor, fontWeight: "bold" }}>
          {formatDisplayValue(values.climatizado)}
        </span>
      ) : (
        formatDisplayValue(values.climatizado)
      ),
      hrsDesfaseClimaInv: isEditing ? (
        <input
          type="number"
          min="0"
          className="form-control form-control-sm"
          value={editingRow.values.hrsDesfaseClimaInv}
          onChange={(e) => {
            if (e.target.value.startsWith("-") || e.target.value === "-")
              return;
            handleEditChange("hrsDesfaseClimaInv", e.target.value);
          }}
          onKeyDown={(e) => {
            if (e.key === "-") e.preventDefault();
          }}
        />
      ) : !isDefault ? (
        <span style={{ color: primaryColor, fontWeight: "bold" }}>
          {formatDisplayValue(values.hrsDesfaseClimaInv)}
        </span>
      ) : (
        formatDisplayValue(values.hrsDesfaseClimaInv)
      ),
      accion: isEditing ? (
        <ActionButtonsConfirm
          onAccept={() => handleSave("horario", enclosure)}
          onCancel={handleCancelEdit}
        />
      ) : (
        <ActionButtons
          onEdit={() =>
            handleStartEdit("horario", enclosure, {
              climatizado: recinto.climatizado || "",
              hrsDesfaseClimaInv: recinto.desfase_clima || 0,
            })
          }
          onDelete={() =>
            handleDeleteClick("horario", enclosure.id, enclosure.name)
          }
        />
      ),
    };
  };

  // Filtrado según búsqueda
  const filteredVentilacion = ventilacionRaw
    .filter(
      (item) =>
        item.code.toLowerCase().includes(searchVentilacion.toLowerCase()) ||
        item.name.toLowerCase().includes(searchVentilacion.toLowerCase())
    )
    .map(mapVentilacionRow);

  const filteredIluminacion = iluminacionRaw
    .filter(
      (item) =>
        item.code.toLowerCase().includes(searchIluminacion.toLowerCase()) ||
        item.name.toLowerCase().includes(searchIluminacion.toLowerCase())
    )
    .map(mapIluminacionRow);

  const filteredCargas = cargasRaw
    .filter(
      (item) =>
        item.code.toLowerCase().includes(searchCargas.toLowerCase()) ||
        item.name.toLowerCase().includes(searchCargas.toLowerCase())
    )
    .map(mapCargasRow);

  const filteredHorario = horarioRaw
    .filter(
      (item) =>
        item.code.toLowerCase().includes(searchHorario.toLowerCase()) ||
        item.name.toLowerCase().includes(searchHorario.toLowerCase())
    )
    .map(mapHorarioRow);

  // Propiedades de búsqueda según pestaña activa
  const getSearchProps = () => {
    switch (activeTab) {
      case "ventilacion":
        return {
          value: searchVentilacion,
          onChange: setSearchVentilacion,
          onNew: () => handleNuevoClick("ventilacion"),
          placeholder: "Buscar perfil de uso...",
        };
      case "iluminacion":
        return {
          value: searchIluminacion,
          onChange: setSearchIluminacion,
          onNew: () => handleNuevoClick("iluminacion"),
          placeholder: "Buscar perfil de uso...",
        };
      case "cargas":
        return {
          value: searchCargas,
          onChange: setSearchCargas,
          onNew: () => handleNuevoClick("cargas"),
          placeholder: "Buscar perfil de uso...",
        };
      case "horario":
        return {
          value: searchHorario,
          onChange: setSearchHorario,
          onNew: () => handleNuevoClick("horario"),
          placeholder: "Buscar perfil de uso...",
        };
      default:
        return {
          value: "",
          onChange: () => { },
          onNew: () => { },
          placeholder: "Buscar perfil de uso...",
        };
    }
  };
  return (
    <div className="p-3">
      {/* Barra de búsqueda */}
      <div className="mb-4">
        <SearchParameters {...getSearchProps()} />
      </div>
      {/* Navegación por pestañas */}
      <div className="card shadow-sm mb-4">
        <div className="card-header bg-white p-0">
            <HorizontalTabs
              tabs={[
                { key: "ventilacion", label: "Ventilación y caudales" },
                { key: "iluminacion", label: "Iluminación" },
                { key: "cargas", label: "Cargas internas" },
                { key: "horario", label: "Climatización" }
              ]}
              currentTab={activeTab}
              onTabChange={(tab) => setActiveTab(tab as TabKey)}
            />        </div>
        <div className="card-body pt-3">
          {/* Contenedor de la tabla */}
          <div className="overflow-auto" style={{ maxHeight: "500px" }}>
            {activeTab === "ventilacion" && (
              <div className="p-2">
                <TablesParameters
                  columns={[
                    {
                      headerName: "Código IFC",
                      field: "code_ifc",
                    },
                    { headerName: "Codigo de Recinto", field: "codigoRecinto" },
                    {
                      headerName: "Tipologia de Recinto",
                      field: "tipologiaRecinto",
                    },
                    { headerName: "R-pers [L/s]", field: "rPers" },
                    { headerName: "IDA", field: "ida" },
                    { headerName: "Ocupacion", field: "ocupacion" },
                    {
                      headerName: "Caudal Impuesto Vent Noct",
                      field: "caudalImpuestoVentNoct",
                    },
                    { headerName: "Infiltraciones [1/h]", field: "infiltraciones" },
                    {
                      headerName: "Recuperador de calor [%]",
                      field: "recuperadorCalor",
                    },
                    {
                      headerName: "Acciones",
                      field: "accion",
                      headerStyle: { width: "100px" },
                      sortable: false,
                    },
                  ]}
                  data={filteredVentilacion}
                />
              </div>
            )}

            {activeTab === "iluminacion" && (
              <div className="p-2">
                <TablesParameters
                  columns={[
                    {
                      headerName: "Código IFC",
                      field: "code_ifc",
                    },
                    { headerName: "Codigo de Recinto", field: "codigoRecinto" },
                    {
                      headerName: "Tipologia de Recinto",
                      field: "tipologiaRecinto",
                    },
                    { headerName: "Potencia Base [W/m2]", field: "potenciaBase" },
                    { headerName: "Estrategia", field: "estrategia" },
                    {
                      headerName: "Potencia Propuesta [W/m2]",
                      field: "potenciaPropuesta",
                    },
                    {
                      headerName: "Acciones",
                      field: "accion",
                      headerStyle: { width: "100px" },
                      sortable: false,
                    },
                  ]}
                  data={filteredIluminacion}
                />
              </div>
            )}

            {activeTab === "cargas" && (
              <div className="p-2">
                <TablesParameters
                  columns={[
                    {
                      headerName: "Código IFC",
                      field: "code_ifc",
                    },
                    { headerName: "Codigo de Recinto", field: "codigoRecinto" },
                    {
                      headerName: "Tipologia de Recinto",
                      field: "tipologiaRecinto",
                    },
                    { headerName: "Usuarios [m2/pers]", field: "usuarios" },
                    { headerName: "Calor Latente [W/pers]", field: "calorLatente" },
                    {
                      headerName: "Calor Sensible [W/pers]",
                      field: "calorSensible",
                    },
                    { headerName: "Equipos [W/m2]", field: "equipos" },
                    {
                      headerName: "Funcionamiento Semanal",
                      field: "funcionamientoSemanal",
                    },
                    { headerName: "Acciones", field: "accion", sortable: false },
                  ]}
                  data={filteredCargas}
                />
              </div>
            )}

            {activeTab === "horario" && (
              <div className="p-2">
                <TablesParameters
                  columns={[
                    {
                      headerName: "Código IFC",
                      field: "code_ifc",
                    },
                    { headerName: "Codigo de Recinto", field: "codigoRecinto" },
                    {
                      headerName: "Tipologia de Recinto",
                      field: "tipologiaRecinto",
                    },
                    { headerName: "Climatizado", field: "climatizado" },
                    {
                      headerName: "Hrs Desfase Clima (Inv)",
                      field: "hrsDesfaseClimaInv",
                    },
                    { headerName: "Acciones", field: "accion", sortable: false },
                  ]}
                  data={filteredHorario}
                />
              </div>
            )}
          </div>

          {/* Modal de creación de nuevo recinto */}
          <ModalCreate
            isOpen={isCreateModalOpen}
            onClose={() => setIsCreateModalOpen(false)}
            onSave={handleCreateSave}
            title="Crear nuevo perfil de ocupación"
            saveLabel="Crear Perfil"
          >
            <div>
              <label htmlFor="recinto-name">Nombre del perfil de ocupación</label>
              <input
                id="recinto-name"
                type="text"
                value={newRecintoName}
                onChange={(e) => setNewRecintoName(e.target.value)}
                placeholder="Ingrese el nombre del perfil"
                style={{ width: "100%", padding: "8px", marginTop: "8px" }}
              />
            </div>
          </ModalCreate>

          {/* Modal de confirmación de eliminación */}
          <ModalCreate
            isOpen={isDeleteModalOpen}
            onClose={() => setIsDeleteModalOpen(false)}
            onSave={handleDeleteConfirm}
            title="Confirmar eliminación"
            saveLabel="Eliminar"
          >
            <div>
              <p>
                ¿Está seguro que desea eliminar el recinto{" "}
                <strong>{itemToDelete?.name}</strong>?
              </p>
            </div>
          </ModalCreate>

          {/* Modal que muestra el componente Profileschedules */}
          <ModalCreate
            isOpen={isProfileSchedulesModalOpen}
            onClose={() => setIsProfileSchedulesModalOpen(false)}
            onSave={() => setIsProfileSchedulesModalOpen(false)}
            title="Perfil de uso diario"
            modalStyle={{ maxWidth: "50vw", maxHeight: "90vh", padding: "32px" }}
            hideFooter={true}
          >
            <Profileschedules onUpdate={() => setRefresh((prev) => prev + 1)} />
          </ModalCreate>      </div>
      </div>
    </div>
  );
};

export default UseProfileTab;
