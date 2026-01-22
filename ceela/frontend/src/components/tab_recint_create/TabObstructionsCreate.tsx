import React, { useState, useEffect, KeyboardEvent } from "react";
import TablesParameters from "@/components/tables/TablesParameters";
import CustomButton from "../common/CustomButton";
import { notify } from "@/utils/notify";
import { constantUrlApiEndpoint } from "@/utils/constant-url-endpoint";
import ModalCreate from "../common/ModalCreate";
import ActionButtons from "@/components/common/ActionButtons";
import ActionButtonsConfirm from "@/components/common/ActionButtonsConfirm";
import { Plus } from "lucide-react";

/**
 * Tipos auxiliares -----------------------------------------------------------
 */
interface AngleAzimutOption {
  range_az: string;
  orientation: string;
}

interface ObstructionsData {
  uniqueKey: string;            // Identificador único por fila
  divisionKey?: string;         // Identificador único de la división (solo filas secundarias)
  id: number;                   // orientation_id (clave de la orientación)
  division_id: number | null;   // division_id (clave de la división)
  index: number;                // índice incremental solo visual
  división: string;             // "División 1", "División 2", ...  ó "-" si no hay
  floor_id: number;             // enclosure_id
  b: number;
  a: number;
  d: number;
  anguloAzimut: string;
  orientación: any;
  obstrucción: number;          // num_orientation (0 cuando es fila principal)
  mainRow: boolean;             // true si es la fila "padre" de la orientación
}

interface EditingValues {
  roof_id: number;
  characteristic: string;
  area: number;
}

/**
 * Componente principal -------------------------------------------------------
 */
const ObstructionTable: React.FC = () => {
  /** ----------------------------------------------------------------------
   * Estados generales
   * ---------------------------------------------------------------------*/
  const [editingRowKey, setEditingRowKey] = useState<string | null>(null);
  const [tableData, setTableData] = useState<ObstructionsData[]>([]);
  const [tableLoading, setTableLoading] = useState<boolean>(false);

  /** Estados para la creación de obstrucción (orientación) */
  const [showModal, setShowModal] = useState(false);
  const [angleOptions, setAngleOptions] = useState<AngleAzimutOption[]>([]);
  const [selectedAngle, setSelectedAngle] = useState<string>("");

  /** Estados y helpers para la edición de orientación */
  const [editingValues, setEditingValues] = useState<EditingValues>({
    roof_id: 0,
    characteristic: "",
    area: 0,
  });

  /** Estados para la edición inline de división */
  const [editingDivisionRowKey, setEditingDivisionRowKey] = useState<string | null>(null);
  const [editingDivisionValues, setEditingDivisionValues] = useState({
    division: "",
    a: 0,
    b: 0,
    d: 0,
  });

  /** Estados para crear división */
  const [showDivisionModal, setShowDivisionModal] = useState(false);
  const [selectedDivision, setSelectedDivision] = useState("División 1");
  const [aValue, setAValue] = useState<string>("");
  const [bValue, setBValue] = useState<string>("");
  const [dValue, setDValue] = useState<string>("");
  const [currentOrientation, setCurrentOrientation] = useState<ObstructionsData | null>(null);

  /** Modales de confirmación */
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [rowToDelete, setRowToDelete] = useState<ObstructionsData | null>(null);
  const [showConfirmDivisionModal, setShowConfirmDivisionModal] = useState(false);
  const [rowToDeleteDivision, setRowToDeleteDivision] = useState<ObstructionsData | null>(null);

  /**  ---------------------------------------------------------------------
   *  NOTA: Se mantiene divisionCounter y getNextDivisionCounter para respetar
   *  la solicitud "sin quitar funciones", aunque el back‑end ahora entrega
   *  num_orientation y ya no son necesarios.
   *  ---------------------------------------------------------------------*/
  const [divisionCounter, setDivisionCounter] = useState<number>(0);
  const getNextDivisionCounter = (angle: string) => {
    const existingNumbers = tableData
      .filter((row) => row.anguloAzimut === angle && row.división !== "-")
      .map((row) => row.obstrucción);
    let counter = 1;
    while (existingNumbers.includes(counter)) counter++;
    return counter;
  };

  const token = localStorage.getItem("token") || "";

  /** ----------------------------------------------------------------------
   * Carga inicial de datos: GET /obstruction/{enclosure_id}
   * ---------------------------------------------------------------------*/
  useEffect(() => {
    const enclosureId = localStorage.getItem("recinto_id");
    if (!enclosureId) {
      notify("No se encontró el recinto_id en el LocalStorage", "error");
      return;
    }

    setTableLoading(true);

    fetch(`${constantUrlApiEndpoint}/obstruction/${enclosureId}`, {
      method: "GET",
      headers: {
        accept: "application/json",
        Authorization: `Bearer ${token}`,
      },
    })
      .then((response) => response.json())
      .then((data) => {
        /**
         * Armamos un array "flat" con una fila principal por orientación
         * y una fila secundaria por cada división que traiga el back‑end.
         */
        const mappedData: ObstructionsData[] = [];

        data.orientations.forEach((orientation: any, index: number) => {
          // Solo agregar la fila principal si no hay divisiones
          if (orientation.divisions.length === 0) {
            mappedData.push({
              uniqueKey: `orientation-${orientation.orientation_id}`,
              id: orientation.orientation_id,
              division_id: null,
              index: mappedData.length + 1,
              división: "-",
              floor_id: orientation.enclosure_id,
              a: 0,
              b: 0,
              d: 0,
              anguloAzimut: orientation.azimut,
              orientación: orientation.orientation,
              obstrucción: 0,
              mainRow: true,
            });
          }

          // ----- filas de divisiones -----
          orientation.divisions.forEach((div: any) => {
            mappedData.push({
              uniqueKey: `orientation-${orientation.orientation_id}-division-${div.division_id}`,
              divisionKey: `division-${div.division_id}`,
              id: orientation.orientation_id,
              division_id: div.division_id,
              index: mappedData.length + 1,
              división: div.division,
              floor_id: orientation.enclosure_id,
              a: div.a,
              b: div.b,
              d: div.d,
              anguloAzimut: orientation.azimut,
              orientación: orientation.orientation,
              obstrucción: div.num_orientation, // <- valor directo del back‑end
              mainRow: false,
            });
          });
        });

        setTableData(mappedData);
        setTableLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching table data:", error);
        notify("Error al cargar datos de obstrucciones", "error");
        setTableLoading(false);
      });
  }, [token]);

  /** ----------------------------------------------------------------------
   * Al abrir modal de obstrucciones -> cargar opciones de ángulo/azimut
   * ---------------------------------------------------------------------*/
  useEffect(() => {
    if (!showModal) return;
    setSelectedAngle("");

    fetch(`${constantUrlApiEndpoint}/angle-azimut-and-orientation`, {
      method: "GET",
      headers: {
        accept: "application/json",
        Authorization: `Bearer ${token}`,
      },
    })
      .then((response) => response.json())
      .then((data: AngleAzimutOption[]) => setAngleOptions(data))
      .catch((error) => {
        console.error("Error fetching angle azimut options:", error);
        notify("Error al cargar las opciones de ángulo azimut", "error");
      });
  }, [showModal, token]);

  /** ----------------------------------------------------------------------
   * CRUD ORIENTACIÓN (mainRow)
   * ---------------------------------------------------------------------*/
  const handleEdit = (row: ObstructionsData) => {
    const newAngle = window.prompt("Seleccione el nuevo ángulo azimut:", row.anguloAzimut);
    if (!newAngle) return;

    fetch(`${constantUrlApiEndpoint}/orientation-update/${row.id}`, {
      method: "PUT",
      headers: {
        accept: "application/json",
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ azimut: newAngle }),
    })
      .then((response) => response.json())
      .then((data) => {
        const updatedRow = { ...row, anguloAzimut: data.azimut, orientación: data.orientation };
        setTableData((prev) => prev.map((r) => (r.id === row.id && r.mainRow ? updatedRow : r)));
        notify("Orientación actualizada correctamente", "success");
      })
      .catch((error) => {
        console.error("Error updating orientation:", error);
        notify("Error al actualizar orientación", "error");
      });
  };

  const handleDelete = (row: ObstructionsData) => {
    setRowToDelete(row);
    setShowConfirmModal(true);
  };

  const confirmDeletion = () => {
    if (!rowToDelete) return;

    fetch(`${constantUrlApiEndpoint}/obstruction/${rowToDelete.id}`, {
      method: "DELETE",
      headers: {
        accept: "application/json",
        Authorization: `Bearer ${token}`,
      },
    })
      .then(() => {
        setTableData((prev) => prev.filter((r) => r.id !== rowToDelete.id));
        notify("Obstrucción eliminada exitosamente", "success");
        setShowConfirmModal(false);
        setRowToDelete(null);
      })
      .catch((error) => {
        console.error("Error deleting orientation:", error);
        notify("Error al eliminar obstrucción", "error");
        setShowConfirmModal(false);
        setRowToDelete(null);
      });
  };

  const handleCancel = () => {
    setEditingRowKey(null);
    setEditingValues({ roof_id: 0, characteristic: "", area: 0 });
  };

  const handleAcceptEdit = (row: ObstructionsData) => {
    fetch(`${constantUrlApiEndpoint}/orientation-update/${row.id}`, {
      method: "PUT",
      headers: {
        accept: "application/json",
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ azimut: selectedAngle }),
    })
      .then((response) => response.json())
      .then((data) => {
        const updatedRow = { ...row, anguloAzimut: data.azimut, orientación: data.orientation };
        setTableData((prev) => prev.map((r) => (r.uniqueKey === row.uniqueKey ? updatedRow : r)));
        notify("Orientación actualizada correctamente", "success");
        setEditingRowKey(null);
      })
      .catch((error) => {
        console.error("Error updating orientation:", error);
        notify("Error al actualizar orientación", "error");
      });
  };

  /** ----------------------------------------------------------------------
   * CRUD DIVISIÓN (filas secundarias)
   * ---------------------------------------------------------------------*/
  const handleCancelDivisionEdit = () => setEditingDivisionRowKey(null);

  const handleAcceptDivisionEdit = (row: ObstructionsData) => {
    if (!row.division_id) {
      notify("No se encontró el id de división para actualizar", "error");
      return;
    }

    const payload = {
      division: editingDivisionValues.division,
      a: editingDivisionValues.a,
      b: editingDivisionValues.b,
      d: editingDivisionValues.d,
    };

    fetch(`${constantUrlApiEndpoint}/division-update/${row.division_id}`, {
      method: "PUT",
      headers: {
        accept: "application/json",
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    })
      .then((response) => response.json())
      .then((data) => {
        const updatedRow: ObstructionsData = {
          ...row,
          división: data.division,
          a: data.a,
          b: data.b,
          d: data.d,
          division_id: data.id,
          mainRow: row.mainRow,
          obstrucción: data.num_orientation, // se actualiza si cambió
        };
        setTableData((prev) => prev.map((r) => (r.uniqueKey === row.uniqueKey ? updatedRow : r)));
        notify("División actualizada correctamente", "success");
        setEditingDivisionRowKey(null);
      })
      .catch((error) => {
        console.error("Error updating division:", error);
        notify("Error al actualizar división", "error");
      });
  };

  const confirmDivisionDeletion = () => {
    if (!rowToDeleteDivision || !rowToDeleteDivision.division_id) {
      notify("No se encontró el id de división para eliminar", "error");
      setShowConfirmDivisionModal(false);
      setRowToDeleteDivision(null);
      return;
    }

    fetch(`${constantUrlApiEndpoint}/division-delete/${rowToDeleteDivision.division_id}`, {
      method: "DELETE",
      headers: {
        accept: "application/json",
        Authorization: `Bearer ${token}`,
      },
    })
      .then(() => {
        // Después de eliminar, refrescar los datos para actualizar las obstrucciones
        const enclosureId = localStorage.getItem("recinto_id");
        return fetch(`${constantUrlApiEndpoint}/obstruction/${enclosureId}`, {
          headers: {
            accept: "application/json",
            Authorization: `Bearer ${token}`,
          },
        });
      })
      .then(response => response.json())
      .then(data => {
        const mappedData: ObstructionsData[] = [];
        data.orientations.forEach((orientation: any, index: number) => {
          // Solo agregar la fila principal si no hay divisiones
          if (orientation.divisions.length === 0) {
            mappedData.push({
              uniqueKey: `orientation-${orientation.orientation_id}`,
              id: orientation.orientation_id,
              division_id: null,
              index: mappedData.length + 1,
              división: "-",
              floor_id: orientation.enclosure_id,
              a: 0,
              b: 0,
              d: 0,
              anguloAzimut: orientation.azimut,
              orientación: orientation.orientation,
              obstrucción: 0,
              mainRow: true,
            });
          }

          orientation.divisions.forEach((div: any) => {
            mappedData.push({
              uniqueKey: `orientation-${orientation.orientation_id}-division-${div.division_id}`,
              divisionKey: `division-${div.division_id}`,
              id: orientation.orientation_id,
              division_id: div.division_id,
              index: mappedData.length + 1,
              división: div.division,
              floor_id: orientation.enclosure_id,
              a: div.a,
              b: div.b,
              d: div.d,
              anguloAzimut: orientation.azimut,
              orientación: orientation.orientation,
              obstrucción: div.num_orientation,
              mainRow: false,
            });
          });
        });

        setTableData(mappedData);
        notify("División eliminada exitosamente", "success");
        setShowConfirmDivisionModal(false);
        setRowToDeleteDivision(null);
      })
      .catch((error) => {
        console.error("Error deleting division:", error);
        notify("Error al eliminar división", "error");
        setShowConfirmDivisionModal(false);
        setRowToDeleteDivision(null);
      });
  };

  /** ----------------------------------------------------------------------
   * Helpers UI
   * ---------------------------------------------------------------------*/
  const preventMinus = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "-") e.preventDefault();
  };

  const handleAngleChange = (e: React.ChangeEvent<HTMLSelectElement>) => setSelectedAngle(e.target.value);

  /** ----------------------------------------------------------------------
   * CREAR ORIENTACIÓN (modal principal)
   * ---------------------------------------------------------------------*/
  const handleCreateObstruction = () => {
    if (!selectedAngle) {
      notify("Debe seleccionar un ángulo azimut", "error");
      return;
    }

    const enclosureId = localStorage.getItem("recinto_id");
    if (!enclosureId) {
      notify("No se encontró el recinto_id en el LocalStorage", "error");
      return;
    }

    fetch(`${constantUrlApiEndpoint}/orientation-create/${enclosureId}`, {
      method: "POST",
      headers: {
        accept: "application/json",
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ azimut: selectedAngle }),
    })
      .then((response) => response.json())
      .then((data) => {
        const newObstruction: ObstructionsData = {
          uniqueKey: `orientation-${data.id}`,
          id: data.id,
          division_id: null,
          index: tableData.length + 1,
          división: "-",
          floor_id: 0,
          b: 0,
          a: 0,
          d: 0,
          anguloAzimut: selectedAngle,
          orientación: data.orientation,
          obstrucción: 0,
          mainRow: true,
        };

        setTableData((prev) => [...prev, newObstruction]);
        setShowModal(false);
        notify("Obstrucción creada correctamente", "success");
      })
      .catch((error) => {
        console.error("Error al crear orientación:", error);
        notify("Error al crear orientación", "error");
      });
  };

  /** ----------------------------------------------------------------------
   * CREAR DIVISIÓN (modal secundario)
   * ---------------------------------------------------------------------*/
  const handleCreateDivision = () => {
    if (aValue === "" || bValue === "" || dValue === "" || Number(aValue) < 0 || Number(bValue) < 0 || Number(dValue) < 0) {
      notify("Los valores de A, B y D deben ser números no negativos", "error");
      return;
    }

    if (!currentOrientation) {
      notify("No se ha seleccionado una orientación para agregar la división", "error");
      return;
    }

    const payload = { division: selectedDivision, a: Number(aValue), b: Number(bValue), d: Number(dValue) };

    fetch(`${constantUrlApiEndpoint}/division-create/${currentOrientation.id}`, {
      method: "POST",
      headers: {
        accept: "application/json",
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    })
      .then((response) => response.json())
      .then((data) => {
        // Después de crear, refrescar los datos para actualizar las obstrucciones
        const enclosureId = localStorage.getItem("recinto_id");
        return fetch(`${constantUrlApiEndpoint}/obstruction/${enclosureId}`, {
          headers: {
            accept: "application/json",
            Authorization: `Bearer ${token}`,
          },
        }).then(response => response.json());
      })
      .then(data => {
        const mappedData: ObstructionsData[] = [];
        data.orientations.forEach((orientation: any, index: number) => {
          // Solo agregar la fila principal si no hay divisiones
          if (orientation.divisions.length === 0) {
            mappedData.push({
              uniqueKey: `orientation-${orientation.orientation_id}`,
              id: orientation.orientation_id,
              division_id: null,
              index: mappedData.length + 1,
              división: "-",
              floor_id: orientation.enclosure_id,
              a: 0,
              b: 0,
              d: 0,
              anguloAzimut: orientation.azimut,
              orientación: orientation.orientation,
              obstrucción: 0,
              mainRow: true,
            });
          }

          orientation.divisions.forEach((div: any) => {
            mappedData.push({
              uniqueKey: `orientation-${orientation.orientation_id}-division-${div.division_id}`,
              divisionKey: `division-${div.division_id}`,
              id: orientation.orientation_id,
              division_id: div.division_id,
              index: mappedData.length + 1,
              división: div.division,
              floor_id: orientation.enclosure_id,
              a: div.a,
              b: div.b,
              d: div.d,
              anguloAzimut: orientation.azimut,
              orientación: orientation.orientation,
              obstrucción: div.num_orientation,
              mainRow: false,
            });
          });
        });

        setTableData(mappedData);
        setSelectedDivision("División 1");
        setAValue("");
        setBValue("");
        setDValue("");
        setShowDivisionModal(false);
        notify("División creada correctamente", "success");
      })
      .catch((error) => {
        console.error("Error al crear División:", error);
        notify("Error al crear División", "error");
      });
  };

  /** ----------------------------------------------------------------------
   * Definición de columnas (AG‑Grid / DataTable) ---------------------------*/
  const columns = [
    {
      headerName: "Ángulo Azimut",
      field: "anguloAzimut",
      renderCell: (row: ObstructionsData) => 
        row.obstrucción <= 1 ? row.anguloAzimut : "",
    },
    {
      headerName: "Orientación",
      field: "orientación",
      renderCell: (row: ObstructionsData) => 
        row.obstrucción <= 1 ? row.orientación ?? "-" : "",
    },
    {
      headerName: "Acciones",
      field: "acciones",
      renderCell: (row: ObstructionsData) => {
        if (row.obstrucción > 1) return null; // No mostrar acciones en filas secundarias
        return editingRowKey === row.uniqueKey ? (
          <ActionButtonsConfirm 
          onAccept={() => handleAcceptEdit(row)} 
          onCancel={handleCancel} />
        ) :
        <ActionButtons onDelete={() => handleDelete(row)} onEdit={() => { setEditingRowKey(row.uniqueKey); setSelectedAngle(row.anguloAzimut); }} />;
      },
    },
    {
      headerName: "Obstrucción",
      field: "obstrucción",
      renderCell: (row: ObstructionsData) => (row.obstrucción === 0 ? "-" : row.obstrucción),
    },
    {
      headerName: "División",
      field: "división",
      renderCell: (row: ObstructionsData) => {
        if (editingDivisionRowKey === row.uniqueKey) {
          return (
            <select className="form-control" value={editingDivisionValues.division} onChange={(e) => setEditingDivisionValues({ ...editingDivisionValues, division: e.target.value })}>
              {["División 1", "División 2", "División 3", "División 4", "División 5"].map((div, idx) => (
                <option key={idx} value={div}>{div}</option>
              ))}
            </select>
          );
        }
        return row.división;
      },
    },
    {
      headerName: "A [m]",
      field: "a",
      renderCell: (row: ObstructionsData) => {
        if (editingDivisionRowKey === row.uniqueKey) {
          return (
            <input type="number" className="form-control" min={0} value={editingDivisionValues.a} onChange={(e) => setEditingDivisionValues({ ...editingDivisionValues, a: Number(e.target.value) })} onKeyDown={preventMinus} />
          );
        }
        return row.a === 0 ? "-" : row.a;
      },
    },
    {
      headerName: "B [m]",
      field: "b",
      renderCell: (row: ObstructionsData) => {
        if (editingDivisionRowKey === row.uniqueKey) {
          return (
            <input type="number" className="form-control" min={0} value={editingDivisionValues.b} onChange={(e) => setEditingDivisionValues({ ...editingDivisionValues, b: Number(e.target.value) })} onKeyDown={preventMinus} />
          );
        }
        return row.b === 0 ? "-" : row.b;
      },
    },
    {
      headerName: "D [m]",
      field: "d",
      renderCell: (row: ObstructionsData) => {
        if (editingDivisionRowKey === row.uniqueKey) {
          return (
            <input type="number" className="form-control" min={0} value={editingDivisionValues.d} onChange={(e) => setEditingDivisionValues({ ...editingDivisionValues, d: Number(e.target.value) })} onKeyDown={preventMinus} />
          );
        }
        return row.d === 0 ? "-" : row.d;
      },
    },
    {
      headerName: "Acciones",
      field: "accionesDivision",
      renderCell: (row: ObstructionsData) => {
        if (editingDivisionRowKey === row.uniqueKey) {
          return <ActionButtonsConfirm onAccept={() => handleAcceptDivisionEdit(row)} onCancel={handleCancelDivisionEdit} />;
        }
        return (
          <>
            {row.división !== "-" && (
              <>
                <CustomButton variant="editIcon" onClick={() => { setEditingDivisionRowKey(row.uniqueKey); setEditingDivisionValues({ division: row.división, a: row.a, b: row.b, d: row.d }); }}>
                  <i className="fa fa-edit" />
                </CustomButton>
                <CustomButton variant="deleteIcon" onClick={() => { setRowToDeleteDivision(row); setShowConfirmDivisionModal(true); }} style={{ marginLeft: "-15px" }}>
                  <i className="fa fa-trash" />
                </CustomButton>
              </>
            )}
            <CustomButton onClick={() => { setCurrentOrientation(row); setShowDivisionModal(true); }} style={{ marginLeft: "2px" }}>
              <i className="fa fa-plus" />
            </CustomButton>
          </>
        );
      },
    },
  ];

  /** ----------------------------------------------------------------------
   * Render
   * ---------------------------------------------------------------------*/
  return (
    <div>
      {/* Botón crear obstrucción */}
      <div style={{ marginTop: "20px" }}>
        <div className="d-flex justify-content-end gap-2 w-100">
          <CustomButton variant="save" onClick={() => setShowModal(true)}>
            <Plus className="me-1" size={16} />
            Nuevas Obstrucciones
          </CustomButton>
        </div>
      </div>

      {/* Tabla */}
      {tableLoading ? (
        <div className="text-center p-4"><p>Cargando datos de obstrucciones...</p></div>
      ) : (
        <TablesParameters columns={columns} data={tableData} />
      )}

      {/* Modal crear Obstrucción */}
      <ModalCreate isOpen={showModal} saveLabel="Crear Obstrucción" onClose={() => setShowModal(false)} onSave={handleCreateObstruction} title="Crear Obstrucción">
        <div className="form-group">
          <label htmlFor="angleAzimutSelect">Ángulo Azimut</label>
          <select id="angleAzimutSelect" className="form-control" value={selectedAngle} onChange={handleAngleChange}>
            <option value="" disabled>Seleccione una opción</option>
            {angleOptions.filter((angle) => !tableData.some((obs) => obs.anguloAzimut === angle.range_az)).map((angle, idx) => (
              <option key={idx} value={angle.range_az}>{`${angle.range_az}  (${angle.orientation})`}</option>
            ))}
          </select>
        </div>
      </ModalCreate>

      {/* Modal crear División */}
      <ModalCreate isOpen={showDivisionModal} saveLabel="Crear División" onClose={() => { setShowDivisionModal(false); setCurrentOrientation(null); }} onSave={handleCreateDivision} title="Crear División">
        <div className="form-group">
          <label htmlFor="divisionSelect">División</label>
          <select id="divisionSelect" className="form-control" value={selectedDivision} onChange={(e) => setSelectedDivision(e.target.value)}>
            {["División 1", "División 2", "División 3", "División 4", "División 5"].map((div, idx) => (
              <option key={idx} value={div}>{div}</option>
            ))}
          </select>
        </div>
        <div className="form-group mt-2">
          <label htmlFor="aInput">A [m] Diferencia de altura media entre la fachada y el obstáculo
          </label>
          <input id="aInput" type="number" className="form-control" min={0} value={aValue} onChange={(e) => setAValue(e.target.value)} onKeyDown={preventMinus} />
        </div>
        <div className="form-group mt-2">
          <label htmlFor="bInput">B [m] Distancia con el obstáculo. </label>
          <input id="bInput" type="number" className="form-control" min={0} value={bValue} onChange={(e) => setBValue(e.target.value)} onKeyDown={preventMinus} />
        </div>
        <div className="form-group mt-2">
          <label htmlFor="dInput">D [m] Ancho del obstáculo</label>
          <input id="dInput" type="number" className="form-control" min={0} value={dValue} onChange={(e) => setDValue(e.target.value)} onKeyDown={preventMinus} />
        </div>
      </ModalCreate>

      {/* Modal confirm delete Obstrucción */}
      <ModalCreate isOpen={showConfirmModal} saveLabel="Confirmar" onClose={() => { setShowConfirmModal(false); setRowToDelete(null); }} onSave={confirmDeletion} title="Confirmación de Eliminación">
        <p>¿Estás seguro de eliminar esta obstrucción?</p>
      </ModalCreate>

      {/* Modal confirm delete División */}
      <ModalCreate isOpen={showConfirmDivisionModal} saveLabel="Confirmar" onClose={() => { setShowConfirmDivisionModal(false); setRowToDeleteDivision(null); }} onSave={confirmDivisionDeletion} title="Confirmación de Eliminación">
        <p>¿Estás seguro de eliminar esta división?</p>
      </ModalCreate>
    </div>
  );
};

export default ObstructionTable;
