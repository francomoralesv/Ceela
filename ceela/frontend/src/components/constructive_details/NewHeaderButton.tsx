// NewHeaderButton.tsx
import React, { useState } from "react";
import CustomButton from "@/components/common/CustomButton";
import ModalCreate from "@/components/common/ModalCreate";
import axios from "axios";
import { notify } from "@/utils/notify";
import { constantUrlApiEndpoint } from "@/utils/constant-url-endpoint";

export interface NewHeaderButtonProps {
  /**
   * Tipo de detalle: 'muros', 'techumbre' o 'pisos'
   */
  tab: "muros" | "techumbre" | "pisos";
  /**
   * Callback que se dispara luego de crear el detalle de forma exitosa, por ejemplo para refrescar la tabla.
   */
  onNewCreated?: () => void;
}

const titleMapping: { [key in NewHeaderButtonProps["tab"]]: string } = {
  muros: "Muro",
  techumbre: "Techo",
  pisos: "Piso",
};

const NewHeaderButton: React.FC<NewHeaderButtonProps> = ({
  tab,
  onNewCreated,
}) => {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newDetalle, setNewDetalle] = useState({
    name_detail: "",
    colorExterior: "Intermedio",
    colorInterior: "Intermedio",
    vertical_lambda: "",
    vertical_e_aisl: "",
    vertical_d: "",
    horizontal_lambda: "",
    horizontal_e_aisl: "",
    horizontal_d: "",
  });

  // Función de obtención del token desde localStorage.
  const getToken = (): string | null => {
    const token = localStorage.getItem("token");
    if (!token) {
      notify("Token no encontrado", "Inicia sesión.");
    }
    return token;
  };

  // Función para guardar el nuevo detalle.
  const handleSaveDetalle = async () => {
    if (!newDetalle.name_detail.trim()) {
      notify("Por favor, complete el nombre del detalle.");
      return;
    }
    const projectId = localStorage.getItem("project_id");
    const token = getToken();
    if (!token || !projectId) return;

    // Se determina el tipo de detalle a crear
    const type = titleMapping[tab] || "Muro";

    // Se define el payload según el tipo; en caso de 'Piso', se envían los valores de aislamiento
    let payload;
    if (type === "Piso") {
      payload = {
        name_detail: newDetalle.name_detail,
        info: {
          ref_aisl_vertical: {
            lambda: parseFloat(newDetalle.vertical_lambda),
            e_aisl: parseFloat(newDetalle.vertical_e_aisl),
            d: parseFloat(newDetalle.vertical_d),
          },
          ref_aisl_horizontal: {
            lambda: parseFloat(newDetalle.horizontal_lambda),
            e_aisl: parseFloat(newDetalle.horizontal_e_aisl),
            d: parseFloat(newDetalle.horizontal_d),
          },
        },
      };
    } else {
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
      notify(`Detalle de ${type} creado exitosamente.`);
      // Se cierra el modal y se reinicia el formulario
      setShowCreateModal(false);
      setNewDetalle({
        name_detail: "",
        colorExterior: "Intermedio",
        colorInterior: "Intermedio",
        vertical_lambda: "",
        vertical_e_aisl: "",
        vertical_d: "",
        horizontal_lambda: "",
        horizontal_e_aisl: "",
        horizontal_d: "",
      });
      if (onNewCreated) onNewCreated();
    } catch (error) {
      console.error("Error al crear el detalle constructivo:", error);
      notify("Ya existe un detalle con el nombre asignado.");
    }
  };

  // Función para prevenir el ingreso de signos negativos en los inputs numéricos.
  const preventMinus = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === '-') {
      e.preventDefault();
    }
  };

  return (
    <>
      <CustomButton variant="save" onClick={() => setShowCreateModal(true)}>
        + Nuevo
      </CustomButton>
      {showCreateModal && (
        <ModalCreate
          isOpen={true}
          title={`Crear Nuevo ${titleMapping[tab]}`}
          onClose={() => {
            setShowCreateModal(false);
            setNewDetalle({
              name_detail: "",
              colorExterior: "Intermedio",
              colorInterior: "Intermedio",
              vertical_lambda: "",
              vertical_e_aisl: "",
              vertical_d: "",
              horizontal_lambda: "",
              horizontal_e_aisl: "",
              horizontal_d: "",
            });
          }}
          onSave={handleSaveDetalle}
          saveLabel={`Crear ${titleMapping[tab]}`}
        >
          <form>
            <div className="form-group">
              <label>Nombre <span style={{ color: "red" }}>*</span></label>
              <input
                type="text"
                className="form-control"
                value={newDetalle.name_detail}
                onChange={(e) =>
                  setNewDetalle({ ...newDetalle, name_detail: e.target.value })
                }
              />
            </div>
            {tab === "pisos" ? (
              <>
                <h5 className="mt-4">Aislamiento Vertical</h5>
                <div className="row">
                  <div className="col-md-4">
                    <div className="form-group">
                      <label>λ [W/mK]</label>
                      <input
                        type="number"
                        step="0.01"
                        className="form-control"
                        value={newDetalle.vertical_lambda}
                        onKeyDown={preventMinus}
                        onChange={(e) =>
                          setNewDetalle({
                            ...newDetalle,
                            vertical_lambda: e.target.value,
                          })
                        }
                      />
                    </div>
                  </div>
                  <div className="col-md-4">
                    <div className="form-group">
                      <label>e Aisl [cm]</label>
                      <input
                        type="number"
                        step="0.1"
                        className="form-control"
                        value={newDetalle.vertical_e_aisl}
                        onKeyDown={preventMinus}
                        onChange={(e) =>
                          setNewDetalle({
                            ...newDetalle,
                            vertical_e_aisl: e.target.value,
                          })
                        }
                      />
                    </div>
                  </div>
                  <div className="col-md-4">
                    <div className="form-group">
                      <label>D [cm]</label>
                      <input
                        type="number"
                        step="0.1"
                        className="form-control"
                        value={newDetalle.vertical_d}
                        onKeyDown={preventMinus}
                        onChange={(e) =>
                          setNewDetalle({
                            ...newDetalle,
                            vertical_d: e.target.value,
                          })
                        }
                      />
                    </div>
                  </div>
                </div>

                <h5 className="mt-3">Aislamiento Horizontal</h5>
                <div className="row">
                  <div className="col-md-4">
                    <div className="form-group">
                      <label>λ [W/mK]</label>
                      <input
                        type="number"
                        min="0"
                        step="any"
                        className="form-control"
                        value={newDetalle.horizontal_lambda}
                        onKeyDown={preventMinus}
                        onChange={(e) =>
                          setNewDetalle({
                            ...newDetalle,
                            horizontal_lambda: e.target.value,
                          })
                        }
                      />
                    </div>
                  </div>
                  <div className="col-md-4">
                    <div className="form-group">
                      <label>e Aisl [cm]</label>
                      <input
                        type="number"
                        min="0"
                        step="any"
                        className="form-control"
                        value={newDetalle.horizontal_e_aisl}
                        onKeyDown={preventMinus}
                        onChange={(e) =>
                          setNewDetalle({
                            ...newDetalle,
                            horizontal_e_aisl: e.target.value,
                          })
                        }
                      />
                    </div>
                  </div>
                  <div className="col-md-4">
                    <div className="form-group">
                      <label>D [cm]</label>
                      <input
                        type="number"
                        min="0"
                        step="any"
                        className="form-control"
                        value={newDetalle.horizontal_d}
                        onKeyDown={preventMinus}
                        onChange={(e) =>
                          setNewDetalle({
                            ...newDetalle,
                            horizontal_d: e.target.value,
                          })
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
              <>
                <div className="form-group">
                  <label>Color Exterior</label>
                  <select
                    className="form-control"
                    value={newDetalle.colorExterior}
                    onChange={(e) =>
                      setNewDetalle({
                        ...newDetalle,
                        colorExterior: e.target.value,
                      })
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
                      setNewDetalle({
                        ...newDetalle,
                        colorInterior: e.target.value,
                      })
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
    </>
  );
};

export default NewHeaderButton;
