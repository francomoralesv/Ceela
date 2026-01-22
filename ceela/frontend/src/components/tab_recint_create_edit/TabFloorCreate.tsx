import ActionButtons from "@/components/common/ActionButtons";
import ActionButtonsConfirm from "@/components/common/ActionButtonsConfirm";
import TablesParameters from "@/components/tables/TablesParameters";
import { constantUrlApiEndpoint } from "@/utils/constant-url-endpoint";
import { displayValue } from "@/utils/formatters";
import { notify } from "@/utils/notify";
import { Plus } from "lucide-react";
import React, { useEffect, useState } from "react";
import CustomButton from "../common/CustomButton";
import ModalCreate from "../common/ModalCreate";

// Interfaz para la respuesta de la API de pisos existentes
interface FloorEnclosure {
  id: number;
  floor_id: number;
  name: string;
  characteristic: string;
  area: number;
  parameter: number;
  is_ventilated: string;
  enclosure_id: number;
  po6_l: number;
  u: number;
  value_u: number;
}

// Definimos la interfaz de nuestros datos para la tabla
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

// Interfaz para las opciones de pisos
interface FloorOption {
  id: number;
  name_detail: string;
  value_u: number;
}

const TabFloorCreate: React.FC = () => {
  const enclosure_id = localStorage.getItem("recinto_id") || "12";
  console.log("Enclosure ID:", enclosure_id);
  const projectId = localStorage.getItem("project_id") || "37";
  const token = localStorage.getItem("token") || "";

  const [tableData, setTableData] = useState<FloorData[]>([]);
  const [editingRowIndex, setEditingRowIndex] = useState<number | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [floorOptions, setFloorOptions] = useState<FloorOption[]>([]);
  const [loading, setLoading] = useState(false);
  const [tableLoading, setTableLoading] = useState(false);

  // Estados para el formulario del modal
  const [floorId, setFloorId] = useState<number>(0);
  const [characteristic, setCharacteristic] = useState<string>("");
  const [area, setArea] = useState<number>(0);
  const [parameter, setParameter] = useState<number>(0);
  const [isVentilated, setIsVentilated] = useState<string>("");

  // Estado para los valores de edición
  const [editValues, setEditValues] = useState<{
    floor_id: number;
    characteristic: string;
    area: number;
    parameter: number;
    is_ventilated: string;
  }>({
    floor_id: 0,
    characteristic: "",
    area: 0,
    parameter: 0,
    is_ventilated: "",
  });

  // Estados para el modal de confirmación de eliminación
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [rowToDelete, setRowToDelete] = useState<FloorData | null>(null);

  // Función para formatear valores en las celdas: si es 0 o "N/A" muestra guion ("-")
  const formatCellValue = (value: any, decimalPlaces?: number): string => {
    if (value === 0 || value === "0" || value === "N/A" || !value ) {
      return "-";
    }

    if (decimalPlaces !== undefined && typeof value === "number") {
      return value.toFixed(decimalPlaces);
    }
    return value?.toString();
  };

  // Manejador para prevenir la entrada del guión
  const handlePreventHyphen = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "-") {
      e.preventDefault();
    }
  };

  // Cargar las opciones de pisos y los datos de la tabla al montar el componente
  useEffect(() => {
    fetchFloorOptions();
    fetchTableData();
  }, []);

  // Función para obtener las opciones de pisos
  const fetchFloorOptions = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `${constantUrlApiEndpoint}/project/${projectId}/details/Piso`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error("Error al obtener las opciones de pisos");
      }

      const data = await response.json();
      setFloorOptions(data);
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setLoading(false);
    }
  };

  // Función para obtener los datos de la tabla
  const fetchTableData = async () => {
    setTableLoading(true);
    try {
      const response = await fetch(
        `${constantUrlApiEndpoint}/floor-enclosures/${enclosure_id}`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error("Error al obtener los datos de pisos");
      }

      const data: FloorEnclosure[] = await response.json();

      // Mantener el orden original usando el índice actual si existe
      const formattedData: FloorData[] = data.map((item) => {
        const existingRow = tableData.find(row => row.id === item.id);
        return {
          id: item.id,
          index: existingRow?.index ?? tableData.length,
          pisos: item.name,
          floor_id: item.floor_id,
          caracteristicas: item.characteristic,
          area: item.area,
          uValue: item.u || item.value_u,
          perimetroSuelo: item.parameter,
          pisoVentilado: item.is_ventilated,
          ptP06L: item.po6_l,
        };
      });

      // Ordenar por el índice original antes de actualizar el estado
      formattedData.sort((a, b) => a.index - b.index);
      setTableData(formattedData);
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setTableLoading(false);
    }
  };

  // Maneja la acción de editar: se guarda el índice de la fila en edición
  const handleEditRow = (row: FloorData) => {
    setEditingRowIndex(row.index);
    // Inicializar los valores de edición con los valores actuales de la fila
    setEditValues({
      floor_id: row.floor_id,
      characteristic: row.caracteristicas,
      area: row.area,
      parameter: row.perimetroSuelo,
      is_ventilated: row.pisoVentilado,
    });
  };

  // Abre el modal de confirmación para eliminar
  const handleShowDeleteModal = (row: FloorData) => {
    setRowToDelete(row);
    setShowDeleteModal(true);
  };

  // Cierra el modal de confirmación para eliminar
  const handleCloseDeleteModal = () => {
    setShowDeleteModal(false);
    setRowToDelete(null);
  };

  // Maneja la eliminación: se remueve la fila y se muestra una notificación
  const handleDeleteRow = async () => {
    if (!rowToDelete) return;

    try {
      const response = await fetch(
        `${constantUrlApiEndpoint}/floor-enclosures-delete/${rowToDelete.id}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error("Error al eliminar el registro");
      }

      notify("Registro eliminado correctamente");
      // Cerrar el modal de confirmación
      setShowDeleteModal(false);
      setRowToDelete(null);
      // Actualizar la tabla después de eliminar
      fetchTableData();
    } catch (error) {
      console.error("Error:", error);
      notify("Error al eliminar el registro");
    }
  };

  // Valida los datos de edición
  const validateEditForm = () => {
    if (
      editValues.floor_id === 0 ||
      !editValues.characteristic ||
      editValues.area === undefined ||
      editValues.area === null
    ) {
      notify("Debe completar todos los campos del formulario correctamente");
      return false;
    }
    return true;
  };

  // Aceptar cambios y enviar a la API
  const handleAcceptRow = async (row: FloorData) => {
    if (!validateEditForm()) {
      return;
    }

    try {
      const response = await fetch(
        `${constantUrlApiEndpoint}/floor-enclosures-update/${row.id}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            floor_id: editValues.floor_id,
            characteristic: editValues.characteristic,
            area: editValues.area,
            parameter: editValues.parameter,
            is_ventilated: editValues.is_ventilated,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Error al actualizar el registro");
      }

      notify("Cambios guardados correctamente");
      setEditingRowIndex(null);
      // Actualizar la tabla después de editar
      fetchTableData();
    } catch (error) {
      console.error("Error:", error);
      notify("Error al guardar los cambios");
    }
  };

  // Cancelar la edición
  const handleCancelRow = () => {
    setEditingRowIndex(null);
    // Reiniciar los valores de edición
    setEditValues({
      floor_id: 0,
      characteristic: "",
      area: 0,
      parameter: 0,
      is_ventilated: "",
    });
  };

  // Manejadores para cambios en los valores de edición
  const handleEditChange = (field: string, value: string | number) => {
    setEditValues({
      ...editValues,
      [field]: value,
    });
  };

  // Renderizar celda editable
  const renderEditableCell = (field: string, row: FloorData) => {
    switch (field) {
      case "pisos":
        return (
          <select
            className="form-control"
            value={editValues.floor_id}
            onChange={(e) =>
              handleEditChange("floor_id", Number(e.target.value))
            }
          >
            <option value={0}>Seleccione un piso</option>
            {floorOptions.map((option) => (
              <option key={option.id} value={option.id}>
                {option.name_detail}
              </option>
            ))}
          </select>
        );
      case "caracteristicas":
        return (
          <select
            className="form-control"
            value={editValues.characteristic}
            onChange={(e) => handleEditChange("characteristic", e.target.value)}
          >
            <option value="">Seleccione una opción</option>
            <option value="Exterior">Exterior</option>
            <option value="Interior climatizado">Interior climatizado</option>
            <option value="Interior no climatizado">
              Interior no climatizado
            </option>
          </select>
        );
      case "area":
        return (
          <input
            type="number"
            min={0}
            className="form-control"
            value={editValues.area}
            onChange={(e) => handleEditChange("area", Number(e.target.value))}
            onKeyDown={handlePreventHyphen}
          />
        );
      case "perimetroSuelo":
        return (
          <input
            type="number"
            min={0}
            className="form-control"
            value={editValues.parameter}
            onChange={(e) =>
              handleEditChange("parameter", Number(e.target.value))
            }
            onKeyDown={handlePreventHyphen}
          />
        );
      case "pisoVentilado":
        return (
          <select
            className="form-control"
            value={editValues.is_ventilated}
            onChange={(e) => handleEditChange("is_ventilated", e.target.value)}
          >
            <option value="">Seleccione una opción</option>
            <option value="Ventilado">Ventilado</option>
            <option value="No Ventilado">No Ventilado</option>
          </select>
        );
      default:
        return row[field as keyof FloorData];
    }
  };

  // Definición de columnas para la tabla
  const columns = [
    {
      headerName: "Pisos",
      field: "pisos",
      renderCell: (row: FloorData) => {
        return editingRowIndex === row.index
          ? renderEditableCell("pisos", row)
          : formatCellValue(row.pisos);
      },
    },
    {
      headerName: "Características espacio contiguo al elemento",
      field: "caracteristicas",
      renderCell: (row: FloorData) => {
        return editingRowIndex === row.index
          ? renderEditableCell("caracteristicas", row)
          : formatCellValue(row.caracteristicas);
      },
    },
    {
      headerName: "Área [m²]",
      field: "area",
      renderCell: (row: FloorData) => {
        return editingRowIndex === row.index
          ? renderEditableCell("area", row)
          : displayValue(row.area, true);
      },
    },
    {
      headerName: "U [W/m²K]",
      field: "uValue",
      renderCell: (row: FloorData) => {
        return row.uValue === 0 ? "-" : formatCellValue(row.uValue, 2);
      },
    },
    {
      headerName: "Perímetro Suelo [m]",
      field: "perimetroSuelo",
      renderCell: (row: FloorData) => {
        return editingRowIndex === row.index
          ? renderEditableCell("perimetroSuelo", row)
          : formatCellValue(row.perimetroSuelo);
      },
    },
    {
      headerName: "Piso ventilado",
      field: "pisoVentilado",
      renderCell: (row: FloorData) => {
        return editingRowIndex === row.index
          ? renderEditableCell("pisoVentilado", row)
          : formatCellValue(row.pisoVentilado);
      },
    },
    {
      headerName: "PT P06 L [m]",
      field: "ptP06L",
      renderCell: (row: FloorData) => formatCellValue(row.ptP06L),
    },
    {
      headerName: "Acciones",
      field: "acciones",
      renderCell: (row: FloorData) => {
        return editingRowIndex === row.index ? (
          <ActionButtonsConfirm
            onAccept={() => handleAcceptRow(row)}
            onCancel={() => handleCancelRow()}
          />
        ) : (
          <ActionButtons
            onEdit={() => handleEditRow(row)}
            onDelete={() => handleShowDeleteModal(row)}
          />
        );
      },
    },
  ];

  // Cierra el modal y reinicia los campos
  const handleModalClose = () => {
    setShowModal(false);
    setFloorId(0);
    setCharacteristic("");
    setArea(0);
    setParameter(0);
    setIsVentilated("");
  };

  // Función para validar los campos del formulario
  const validateForm = () => {
    if (
      floorId === 0 ||
      !characteristic ||
      area === undefined ||
      area === null
    ) {
      notify("Debe completar todos los campos del formulario correctamente");
      return false;
    }
    return true;
  };

  // Función que se ejecuta al confirmar la creación en el modal
  const handleModalSave = async () => {
    // Validar que todos los campos estén completos
    if (!validateForm()) {
      return; // Detener la ejecución si la validación falla
    }

    const payload = {
      floor_id: floorId,
      characteristic: characteristic,
      area: area,
      parameter: parameter,
      is_ventilated: isVentilated,
    };

    try {
      const response = await fetch(
        `${constantUrlApiEndpoint}/floor-enclosures-create/${enclosure_id}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(payload),
        }
      );

      if (!response.ok) {
        throw new Error("Error en la creación");
      }

      notify("Piso creado exitosamente");
      handleModalClose();
      // Actualizar los datos de la tabla después de la creación
      fetchTableData();
    } catch (error) {
      console.error("Error:", error);
      notify("Error al crear el piso");
    }
  };

  return (
    <div>
      <div style={{ marginTop: "20px" }}>
        <div className="d-flex justify-content-end gap-2 w-100">
          <CustomButton variant="save" onClick={() => setShowModal(true)}>
            <Plus className="me-1" size={16} />
            Nuevo Piso
          </CustomButton>
        </div>
      </div>
      {tableLoading ? (
        <div className="text-center p-4">
          <p>Cargando datos de pisos...</p>
        </div>
      ) : (
        <TablesParameters columns={columns} data={tableData} />
      )}

      {/* Modal de Creación */}
      <ModalCreate
        isOpen={showModal}
        onClose={handleModalClose}
        onSave={handleModalSave}
        saveLabel="Crear Piso"
        title="Crear Piso"
      >
        <div className="container">
          <div className="row mb-3">
            <div className="col-md-4">
              <label htmlFor="floorId">
                Piso <span style={{ color: "red" }}>*</span>
              </label>
            </div>
            <div className="col-md-8">
              <select
                id="floorId"
                className="form-control"
                value={floorId}
                onChange={(e) => setFloorId(Number(e.target.value))}
                disabled={loading}
              >
                <option value={0}>Seleccione un piso</option>
                {floorOptions.map((option) => (
                  <option key={option.id} value={option.id}>
                    {option.name_detail}
                  </option>
                ))}
              </select>
              {loading && (
                <small className="text-muted">Cargando opciones...</small>
              )}
            </div>
          </div>

          <div className="row mb-3">
            <div className="col-md-4">
              <label htmlFor="characteristic">
                Característica <span style={{ color: "red" }}>*</span>
              </label>
            </div>
            <div className="col-md-8">
              <select
                id="characteristic"
                className="form-control"
                value={characteristic}
                onChange={(e) => setCharacteristic(e.target.value)}
              >
                <option value="">Seleccione una opción</option>
                <option value="Exterior">Exterior</option>
                <option value="Interior climatizado">Interior climatizado</option>
                <option value="Interior no climatizado">
                  Interior no climatizado
                </option>
              </select>
            </div>
          </div>

          <div className="row mb-3">
            <div className="col-md-4">
              <label htmlFor="area">
                Área [m²] <span style={{ color: "red" }}>*</span>
              </label>
            </div>
            <div className="col-md-8">
              <input
                type="number"
                id="area"
                className="form-control"
                value={area}
                onChange={(e) => setArea(Number(e.target.value))}
                onKeyDown={handlePreventHyphen}
              />
            </div>
          </div>

          <div className="row mb-3">
            <div className="col-md-4">
              <label htmlFor="parameter">Perímetro Suelo [m]</label>
            </div>
            <div className="col-md-8">
              <input
                type="number"
                id="parameter"
                className="form-control"
                value={parameter}
                onChange={(e) => setParameter(Number(e.target.value))}
                onKeyDown={handlePreventHyphen}
              />
            </div>
          </div>

          <div className="row mb-3">
            <div className="col-md-4">
              <label htmlFor="isVentilated">Ventilado</label>
            </div>
            <div className="col-md-8">
              <select
                id="isVentilated"
                className="form-control"
                value={isVentilated}
                onChange={(e) => setIsVentilated(e.target.value)}
              >
                <option value="">Seleccione una opción</option>
                <option value="Ventilado">Ventilado</option>
                <option value="No Ventilado">No Ventilado</option>
              </select>
            </div>
          </div>
          {/* Texto de datos obligatorios */}
          <div className="row">
            <div className="col-12" style={{ textAlign: "left" }}>
              <p style={{ color: "red", margin: 0 }}>(*) Datos obligatorios</p>
            </div>
          </div>
        </div>
      </ModalCreate>

      {/* Modal de Confirmación de Eliminación */}
      <ModalCreate
        isOpen={showDeleteModal}
        onClose={handleCloseDeleteModal}
        onSave={handleDeleteRow}
        saveLabel="Eliminar"
        title="Confirmar Eliminación"
      >
        <div className="container">
          <div className="row mb-3">
            <p>
              ¿Está seguro que desea eliminar el piso{" "}
              <strong>{rowToDelete?.pisos}</strong>?
            </p>
          </div>
        </div>
      </ModalCreate>
    </div>
  );
};

export default TabFloorCreate;
