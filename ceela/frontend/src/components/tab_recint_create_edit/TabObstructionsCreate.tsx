import React, { useState, useEffect, useCallback, KeyboardEvent } from "react";
import TablesParameters from "@/components/tables/TablesParameters";
import CustomButton from "../common/CustomButton";
import { notify } from "@/utils/notify";
import { constantUrlApiEndpoint } from "@/utils/constant-url-endpoint";
import ModalCreate from "../common/ModalCreate";
import ActionButtons from "@/components/common/ActionButtons";
import ActionButtonsConfirm from "@/components/common/ActionButtonsConfirm";
import { Plus } from "lucide-react";

/* -------------------------------------------------------------------------- */
/*  Tipos                                                                     */
/* -------------------------------------------------------------------------- */

interface AngleAzimutOption {
  range_az: string;
  orientation: string;
}

interface DivisionAPI {
  a: number;
  b: number;
  d: number;
  division: string;
  division_id: number;
  num_orientation: number;
  orientation_id: number;
  is_deleted: boolean;
}

interface ObstructionsData {
  id: number; // orientation_id
  division_id: number | null;
  index: number;
  división: string;
  floor_id: number;
  a: number;
  b: number;
  d: number;
  anguloAzimut: string;
  orientación: any;
  obstrucción: number; // num_orientation
  mainRow: boolean;
}

interface EditingValues {
  roof_id: number;
  characteristic: string;
  area: number;
}

interface EditingDivisionValues {
  division: string;
  division_id: number | null;
  a: number;
  b: number;
  d: number;
}

/* -------------------------------------------------------------------------- */
/*  Hook reutilizable para cargar obstrucciones                               */
/* -------------------------------------------------------------------------- */
const useObstructionsFetch = (token: string) => {
  const [tableData, setTableData] = useState<ObstructionsData[]>([]);
  const [tableLoading, setLoading] = useState<boolean>(false);

  const fetchObstructions = useCallback(() => {
    const enclosureId = localStorage.getItem("recinto_id");
    if (!enclosureId) {
      notify("No se encontró el recinto_id en el LocalStorage", "error");
      return;
    }

    setLoading(true);
    fetch(`${constantUrlApiEndpoint}/obstruction/${enclosureId}`, {
      headers: {
        accept: "application/json",
        Authorization: `Bearer ${token}`,
      },
    })
      .then((r) => r.json())
      .then((data) => {
        const rows: ObstructionsData[] = [];

        data.orientations.forEach((o: any) => {
          /** ----------------------------------------------------------------
           * 1) Filtrar divisiones eliminadas
           * 2) Ordenarlas por num_orientation
           * ----------------------------------------------------------------*/
          const divisions: DivisionAPI[] =
            o.divisions
              ?.filter((d: DivisionAPI) => !d.is_deleted)
              .sort(
                (a: DivisionAPI, b: DivisionAPI) => a.num_orientation - b.num_orientation,
              ) || [];

          /** ---------------------------------------------------------------
           * Si NO hay divisiones todavía, creamos la fila principal;        *
           * cuando haya al menos una división, esa fila ya no es necesaria. *
           * -------------------------------------------------------------- */
          if (divisions.length === 0) {
            rows.push({
              id: o.orientation_id,
              division_id: null,
              index: rows.length + 1,
              división: "-",
              floor_id: o.enclosure_id,
              a: 0,
              b: 0,
              d: 0,
              anguloAzimut: o.azimut,
              orientación: o.orientation,
              obstrucción: 0,
              mainRow: true,
            });
          }

          /** ---------------------------------------------------------------
           * Añadimos las divisiones existentes                              *
           * -------------------------------------------------------------- */
          divisions.forEach((div, i) => {
            rows.push({
              id: o.orientation_id,
              division_id: div.division_id,
              index: rows.length + 1,
              división: div.division,
              floor_id: o.enclosure_id,
              a: div.a,
              b: div.b,
              d: div.d,
              anguloAzimut: o.azimut,
              orientación: o.orientation,
              obstrucción: i + 1, // enumerar 1,2,3…
              mainRow: false,
            });
          });
        });

        setTableData(rows);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching table data:", err);
        notify("Error al cargar datos de obstrucciones", "error");
        setLoading(false);
      });
  }, [token]);

  useEffect(fetchObstructions, [fetchObstructions]);

  return { tableData, setTableData, tableLoading, fetchObstructions };
};

/* -------------------------------------------------------------------------- */
/*  Componente                                                                */
/* -------------------------------------------------------------------------- */

const ObstructionTable: React.FC = () => {
  const token = localStorage.getItem("token") || "";

  /* ---------- Estados principales provenientes del hook ------------------ */
  const { tableData, setTableData, tableLoading, fetchObstructions } =
    useObstructionsFetch(token);

  /* ---------- Estados propios del componente ---------------------------- */
  const [editingRowId, setEditingRowId] = useState<number | null>(null);

  // Modal Obstrucciones
  const [showModal, setShowModal] = useState(false);
  const [angleOptions, setAngleOptions] = useState<AngleAzimutOption[]>([]);
  const [selectedAngle, setSelectedAngle] = useState<string>("");

  // División inline
  const [editingDivisionRowId, setEditingDivisionRowId] = useState<number | null>(null);
  const [editingDivisionValues, setEditingDivisionValues] = useState<EditingDivisionValues>({
    division: "",
    division_id: null,
    a: 0,
    b: 0,
    d: 0,
  });

  // Modal Crear División
  const [showDivisionModal, setShowDivisionModal] = useState(false);
  const [selectedDivision, setSelectedDivision] = useState("División 1");
  const [aValue, setAValue] = useState<string>("");
  const [bValue, setBValue] = useState<string>("");
  const [dValue, setDValue] = useState<string>("");
  const [currentOrientation, setCurrentOrientation] = useState<ObstructionsData | null>(null);

  // Confirmaciones
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [rowToDelete, setRowToDelete] = useState<ObstructionsData | null>(null);
  const [showConfirmDivisionModal, setShowConfirmDivisionModal] = useState(false);
  const [rowToDeleteDivision, setRowToDeleteDivision] = useState<ObstructionsData | null>(null);

  /* ---------------------------------------------------------------------- */
  /*  Utilidades                                                             */
  /* ---------------------------------------------------------------------- */
  const preventMinus = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "-") e.preventDefault();
  };

  const formatAngleOption = (o: AngleAzimutOption) => `${o.range_az} (${o.orientation})`;

  /* ---------------------------------------------------------------------- */
  /*  Cargar opciones ángulo azimut para el modal                            */
  /* ---------------------------------------------------------------------- */
  useEffect(() => {
    if (!showModal) return;

    setSelectedAngle("");
    fetch(`${constantUrlApiEndpoint}/angle-azimut-and-orientation`, {
      headers: {
        accept: "application/json",
        Authorization: `Bearer ${token}`,
      },
    })
      .then((r) => r.json())
      .then((data: AngleAzimutOption[]) => setAngleOptions(data))
      .catch((err) => {
        console.error("Error fetching angle azimut options:", err);
        notify("Error al cargar las opciones de ángulo azimut", "error");
      });
  }, [showModal, token]);

  /* ---------------------------------------------------------------------- */
  /*  CRUD ORIENTACIÓN                                                      */
  /* ---------------------------------------------------------------------- */
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
      .then((r) => r.json())
      .then(() => {
        fetchObstructions();
        notify("Orientación actualizada correctamente", "success");
      })
      .catch((e) => {
        console.error("Error updating orientation:", e);
        notify("Error al actualizar orientación", "error");
      })
      .finally(() => setEditingRowId(null));
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
        fetchObstructions();
        notify("Obstrucción eliminada exitosamente", "success");
      })
      .catch((e) => {
        console.error("Error deleting orientation:", e);
        notify("Error al eliminar obstrucción", "error");
      })
      .finally(() => {
        setShowConfirmModal(false);
        setRowToDelete(null);
      });
  };

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
      .then((r) => r.json())
      .then(() => {
        fetchObstructions();
        setShowModal(false);
        notify("Obstrucción creada correctamente", "success");
      })
      .catch((e) => {
        console.error("Error al crear orientación:", e);
        notify("Error al crear orientación", "error");
      });
  };

  /* ---------------------------------------------------------------------- */
  /*  CRUD DIVISIÓN                                                         */
  /* ---------------------------------------------------------------------- */
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
      .then(() => {
        fetchObstructions();
        notify("División actualizada correctamente", "success");
      })
      .catch((e) => {
        console.error("Error updating division:", e);
        notify("Error al actualizar división", "error");
      })
      .finally(() => setEditingDivisionRowId(null));
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
        fetchObstructions();
        notify("División eliminada exitosamente", "success");
      })
      .catch((e) => {
        console.error("Error deleting division:", e);
        notify("Error al eliminar división", "error");
      })
      .finally(() => {
        setShowConfirmDivisionModal(false);
        setRowToDeleteDivision(null);
      });
  };

  const handleCreateDivision = () => {
    if (
      aValue === "" ||
      bValue === "" ||
      dValue === "" ||
      Number(aValue) < 0 ||
      Number(bValue) < 0 ||
      Number(dValue) < 0
    ) {
      notify("Los valores de A, B y D deben ser números no negativos", "error");
      return;
    }

    if (!currentOrientation) {
      notify("No se ha seleccionado una orientación para agregar la división", "error");
      return;
    }

    const payload = {
      division: selectedDivision,
      a: Number(aValue),
      b: Number(bValue),
      d: Number(dValue),
    };

    fetch(`${constantUrlApiEndpoint}/division-create/${currentOrientation.id}`, {
      method: "POST",
      headers: {
        accept: "application/json",
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    })
      .then(() => {
        fetchObstructions();
        setShowDivisionModal(false);
        /* limpio modal */
        setSelectedDivision("División 1");
        setAValue("");
        setBValue("");
        setDValue("");
        notify("División creada correctamente", "success");
      })
      .catch((e) => {
        console.error("Error al crear División:", e);
        notify("Error al crear División", "error");
      });
  };

  /* ---------------------------------------------------------------------- */
  /*  Columnas                                                               */
  /* ---------------------------------------------------------------------- */
  const columns = [
    {
      headerName: "Ángulo Azimut",
      field: "anguloAzimut",
      renderCell: (row: ObstructionsData) =>
        // Muestra en la fila “principal” (obstrucción 0) o en la primera división (obstrucción 1)
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
        // Solo botones en la fila principal o en la primera división
        if (row.obstrucción > 1) return "";
  
        return editingRowId === row.id ? (
          <ActionButtonsConfirm
            onAccept={() => handleEdit(row)}
            onCancel={() => setEditingRowId(null)}
          />
        ) : (
          <ActionButtons
            onEdit={() => {
              setEditingRowId(row.id);
              setSelectedAngle(row.anguloAzimut);
            }}
            onDelete={() => handleDelete(row)}
          />
        );
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
        if (editingDivisionRowId === row.id && row.division_id === editingDivisionValues.division_id) {
          return (
            <select
              className="form-control"
              value={editingDivisionValues.division}
              onChange={(e) =>
                setEditingDivisionValues({ ...editingDivisionValues, division: e.target.value })
              }
            >
              {["División 1", "División 2", "División 3", "División 4", "División 5"].map(
                (div, i) => (
                  <option key={i} value={div}>
                    {div}
                  </option>
                ),
              )}
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
        if (editingDivisionRowId === row.id && row.division_id === editingDivisionValues.division_id) {
          return (
            <input
              type="number"
              className="form-control"
              min={0}
              value={editingDivisionValues.a}
              onChange={(e) =>
                setEditingDivisionValues({ ...editingDivisionValues, a: Number(e.target.value) })
              }
              onKeyDown={preventMinus}
            />
          );
        }
        return row.a === 0 ? "-" : row.a;
      },
    },
    {
      headerName: "B [m]",
      field: "b",
      renderCell: (row: ObstructionsData) => {
        if (editingDivisionRowId === row.id && row.division_id === editingDivisionValues.division_id) {
          return (
            <input
              type="number"
              className="form-control"
              min={0}
              value={editingDivisionValues.b}
              onChange={(e) =>
                setEditingDivisionValues({ ...editingDivisionValues, b: Number(e.target.value) })
              }
              onKeyDown={preventMinus}
            />
          );
        }
        return row.b === 0 ? "-" : row.b;
      },
    },
    {
      headerName: "D [m]",
      field: "d",
      renderCell: (row: ObstructionsData) => {
        if (editingDivisionRowId === row.id && row.division_id === editingDivisionValues.division_id) {
          return (
            <input
              type="number"
              className="form-control"
              min={0}
              value={editingDivisionValues.d}
              onChange={(e) =>
                setEditingDivisionValues({ ...editingDivisionValues, d: Number(e.target.value) })
              }
              onKeyDown={preventMinus}
            />
          );
        }
        return row.d === 0 ? "-" : row.d;
      },
    },
    {
      headerName: "Acciones",
      field: "accionesDivision",
      renderCell: (row: ObstructionsData) => {
        if (editingDivisionRowId === row.id) {
          return (
            <ActionButtonsConfirm
              onAccept={() => handleAcceptDivisionEdit(row)}
              onCancel={() => setEditingDivisionRowId(null)}
            />
          );
        }
        return (
          <>
            {row.división !== "-" && (
              <>
                <CustomButton
                  variant="editIcon"
                  onClick={() => {
                    setEditingDivisionRowId(row.id);
                    setEditingDivisionValues({
                      division: row.división,
                      division_id: row.division_id,
                      a: row.a,
                      b: row.b,
                      d: row.d,
                    });
                  }}
                >
                  <i className="fa fa-edit" />
                </CustomButton>
                <CustomButton
                  variant="deleteIcon"
                  onClick={() => {
                    setRowToDeleteDivision(row);
                    setShowConfirmDivisionModal(true);
                  }}
                  style={{ marginLeft: "-15px" }}
                >
                  <i className="fa fa-trash" />
                </CustomButton>
              </>
            )}
            <CustomButton
              onClick={() => {
                setCurrentOrientation(row);
                setShowDivisionModal(true);
              }}
              style={{ marginLeft: "2px" }}
            >
              <i className="fa fa-plus" />
            </CustomButton>
          </>
        );
      },
    },
  ];

  /* ---------------------------------------------------------------------- */
  /*  Render                                                                 */
  /* ---------------------------------------------------------------------- */
  return (
    <div>
      <div style={{ marginTop: "20px" }}>
        <div className="d-flex justify-content-end gap-2 w-100">
          <CustomButton variant="save" onClick={() => setShowModal(true)}>
            <Plus className="me-1" size={16} />
            Nuevas Obstrucciones
          </CustomButton>
        </div>
      </div>

      {tableLoading ? (
        <div className="text-center p-4">
          <p>Cargando datos de obstrucciones...</p>
        </div>
      ) : (
        <TablesParameters columns={columns} data={tableData} />
      )}

      {/* ---------------------------- Modal Obstrucción --------------------- */}
      <ModalCreate
        isOpen={showModal}
        saveLabel="Crear Obstrucción"
        onClose={() => setShowModal(false)}
        onSave={handleCreateObstruction}
        title="Crear Obstrucción"
      >
        <div className="form-group">
          <label htmlFor="angleAzimutSelect">Ángulo Azimut</label>
          <select
            id="angleAzimutSelect"
            className="form-control"
            value={selectedAngle}
            onChange={(e) => setSelectedAngle(e.target.value)}
          >
            <option value="" disabled>
              Seleccione una opción
            </option>
            {angleOptions
              .filter((o) => !tableData.some((r) => r.anguloAzimut === o.range_az))
              .map((o, i) => (
                <option key={i} value={o.range_az}>
                  {formatAngleOption(o)}
                </option>
              ))}
          </select>
        </div>
      </ModalCreate>

      {/* ----------------------------- Modal División ----------------------- */}
      <ModalCreate
        isOpen={showDivisionModal}
        saveLabel="Crear División"
        onClose={() => {
          setShowDivisionModal(false);
          setCurrentOrientation(null);
        }}
        onSave={handleCreateDivision}
        title="Crear División"
      >
        <div className="form-group">
          <label htmlFor="divisionSelect">División</label>
          <select
            id="divisionSelect"
            className="form-control"
            value={selectedDivision}
            onChange={(e) => setSelectedDivision(e.target.value)}
          >
            {["División 1", "División 2", "División 3", "División 4", "División 5"].map(
              (div, i) => (
                <option key={i} value={div}>
                  {div}
                </option>
              ),
            )}
          </select>
        </div>
        <div className="form-group mt-2">
          <label htmlFor="aInput">A [m] Diferencia altura media, fachada y obstáculo</label>
          <input
            id="aInput"
            type="number"
            className="form-control"
            min={0}
            value={aValue}
            onChange={(e) => setAValue(e.target.value)}
            onKeyDown={preventMinus}
          />
        </div>
        <div className="form-group mt-2">
          <label htmlFor="bInput">B [m] Distancia con el obstáculo
          </label>
          <input
            id="bInput"
            type="number"
            className="form-control"
            min={0}
            value={bValue}
            onChange={(e) => setBValue(e.target.value)}
            onKeyDown={preventMinus}
          />
        </div>
        <div className="form-group mt-2">
          <label htmlFor="dInput">D [m] Ancho del obstáculo</label>
          <input
            id="dInput"
            type="number"
            className="form-control"
            min={0}
            value={dValue}
            onChange={(e) => setDValue(e.target.value)}
            onKeyDown={preventMinus}
          />
        </div>
      </ModalCreate>

      {/* ---------------------- Confirmar eliminación orientación ----------- */}
      <ModalCreate
        isOpen={showConfirmModal}
        saveLabel="Confirmar"
        onClose={() => {
          setShowConfirmModal(false);
          setRowToDelete(null);
        }}
        onSave={confirmDeletion}
        title="Confirmación de Eliminación"
      >
        <p>¿Estás seguro de eliminar esta obstrucción?</p>
      </ModalCreate>

      {/* ---------------------- Confirmar eliminación división ------------- */}
      <ModalCreate
        isOpen={showConfirmDivisionModal}
        saveLabel="Confirmar"
        onClose={() => {
          setShowConfirmDivisionModal(false);
          setRowToDeleteDivision(null);
        }}
        onSave={confirmDivisionDeletion}
        title="Confirmación de Eliminación"
      >
        <p>¿Estás seguro de eliminar esta división?</p>
      </ModalCreate>
    </div>
  );
};

export default ObstructionTable;
