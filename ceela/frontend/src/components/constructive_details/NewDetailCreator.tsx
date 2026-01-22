// NewDetailCreator.tsx
import React, { useState } from "react";
import axios from "axios";
import ModalCreate from "@/components/common/ModalCreate";
import CustomButton from "@/components/common/CustomButton";
import { notify } from "@/utils/notify";
import { constantUrlApiEndpoint } from "@/utils/constant-url-endpoint";

export type DetailType = "Muro" | "Techo" | "Piso";

interface NewDetailCreatorProps {
  /**
   * Tipo de detalle a crear: puede ser "Muro", "Techo" o "Piso".
   * Este valor se usa para construir el endpoint y definir el formulario.
   */
  detailType: DetailType;
  /**
   * Función callback que se ejecuta una vez se haya creado el detalle.
   * Por ejemplo, para refrescar la tabla de detalles.
   */
  onDetailCreated: () => void;
}

/**
 * Componente que encapsula el botón de creación de un nuevo detalle constructivo.
 * Al hacer clic en el botón se abre un modal con el formulario correspondiente y se ejecuta
 * la llamada al endpoint indicado para crear el detalle en la base de datos.
 */
const NewDetailCreator: React.FC<NewDetailCreatorProps> = ({
  detailType,
  onDetailCreated,
}) => {
  const [showModal, setShowModal] = useState(false);
  interface NewDetail {
    name_detail: string;
    colorInterior: string;
    colorExterior: string;
    vertical_lambda: number | undefined;
    vertical_e_aisl: number | undefined;
    vertical_d: number | undefined;
    horizontal_lambda: number | undefined;
    horizontal_e_aisl: number | undefined;
    horizontal_d: number | undefined;
  }
  
  const [newDetail, setNewDetail] = useState<NewDetail>({
    name_detail: "",
    colorInterior: "Intermedio",
    colorExterior: "Intermedio",
    vertical_lambda: undefined,
    vertical_e_aisl: undefined,
    vertical_d: undefined,
    horizontal_lambda: undefined,
    horizontal_e_aisl: undefined,
    horizontal_d: undefined,
  });

  const getToken = (): string | null => {
    const token = localStorage.getItem("token");
    if (!token) {
      notify("Token no encontrado", "Inicia sesión.");
    }
    return token;
  };

  const handleSaveDetail = async () => {
    if (!newDetail.name_detail.trim()) {
      notify("Por favor, complete el campo de nombre.");
      return;
    }
    if (
      detailType !== "Piso" &&
      (!newDetail.colorInterior || !newDetail.colorExterior)
    ) {
      notify("Por favor, complete los campos de color interior y exterior.");
      return;
    }

    const token = getToken();
    if (!token) return;

    let payload;
    if (detailType === "Piso") {
      payload = {
        name_detail: newDetail.name_detail,
        info: {
          ref_aisl_vertical: {
            d: newDetail.vertical_d,
            e_aisl: newDetail.vertical_e_aisl,
            lambda: newDetail.vertical_lambda,
          },
          ref_aisl_horizontal: {
            d: newDetail.horizontal_d,
            e_aisl: newDetail.horizontal_e_aisl,
            lambda: newDetail.horizontal_lambda,
          },
        },
      };
    } else {
      // Para muros y techos se envían los colores interior y exterior
      payload = {
        name_detail: newDetail.name_detail,
        info: {
          surface_color: {
            interior: { name: newDetail.colorInterior },
            exterior: { name: newDetail.colorExterior },
          },
        },
      };
    }

    try {
      const url = `${constantUrlApiEndpoint}/admin/${detailType}/detail-part-create`;
      const headers = {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      };
      await axios.post(url, payload, { headers });
      notify("Detalle creado exitosamente.");
      // Ejecuta el callback para actualizar la lista de detalles (o cualquier acción deseada)
      onDetailCreated();
      // Cierra el modal y resetea el formulario
      setShowModal(false);
      setNewDetail({
        name_detail: "",
        colorExterior: "Intermedio",
        colorInterior: "Intermedio",
        vertical_lambda: undefined,
        vertical_e_aisl: undefined,
        vertical_d: undefined,
        horizontal_lambda: undefined,
        horizontal_e_aisl: undefined,
        horizontal_d: undefined,
      });
    } catch (error) {
      if (axios.isAxiosError(error)) {
        console.error(
          "Error al crear detalle constructivo:",
          error.response || error
        );
        if (
          error.response &&
          error.response.data &&
          error.response.data.detail
        ) {
          notify(error.response.data.detail);
        } else {
          notify("Error al crear el Detalle Constructivo.");
        }
      } else if (error instanceof Error) {
        console.error("Error al crear detalle constructivo:", error.message);
        notify("Error al crear el Detalle Constructivo.");
      } else {
        console.error("Error al crear detalle constructivo:", error);
      }
    }
  };

  return (
    <>
      {/* Botón que abre el modal para crear nuevo detalle */}
      <CustomButton variant="save" onClick={() => setShowModal(true)}>
        + Nuevo
      </CustomButton>

      {showModal && (
        <ModalCreate
          isOpen={true}
          title={`Crear Nuevo ${detailType}`}
          onClose={() => {
            setShowModal(false);
            // Resetea el formulario al cerrar el modal
            setNewDetail({
              name_detail: "",
              colorExterior: "Intermedio",
              colorInterior: "Intermedio",
              vertical_lambda: undefined,
              vertical_e_aisl: undefined,
              vertical_d: undefined,
              horizontal_lambda: undefined,
              horizontal_e_aisl: undefined,
              horizontal_d: undefined,
            });
          }}
          onSave={handleSaveDetail}
          saveLabel={`Crear ${detailType}`}
        >
          <form>
            <div className="form-group">
              <label>Nombre <span style={{ color: "red" }}>*</span></label>
              <input
                type="text"
                className="form-control"
                value={newDetail.name_detail}
                onChange={(e) =>
                  setNewDetail((prev) => ({
                    ...prev,
                    name_detail: e.target.value,
                  }))
                }
              />
            </div>
            {detailType === "Piso" ? (
              <>
                <div className="mt-4"><h5>Aislamiento Vertical</h5>
                  <div className="row">
                    <div className="col-md-4">
                      <div className="form-group">
                        <label>λ [W/mK]</label>
                        <input
                          type="number"
                          min="0"
                          step="any"
                          className="form-control"
                          value={newDetail.vertical_lambda || ''}
                          onChange={(e) =>
                            setNewDetail((prev) => ({
                              ...prev,
                              vertical_lambda: parseFloat(e.target.value) || undefined,
                            }))
                          }
                          onKeyDown={(e) => {
                            if (e.key === '-' || e.key === 'e') {
                              e.preventDefault();
                            }
                          }}
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
                          value={newDetail.vertical_e_aisl || ''}
                          onChange={(e) =>
                            setNewDetail((prev) => ({
                              ...prev,
                              vertical_e_aisl: parseFloat(e.target.value) || undefined,
                            }))
                          }
                          onKeyDown={(e) => {
                            if (e.key === '-' || e.key === 'e') {
                              e.preventDefault();
                            }
                          }}
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
                          value={newDetail.vertical_d || ''}
                          onChange={(e) =>
                            setNewDetail((prev) => ({
                              ...prev,
                              vertical_d: parseFloat(e.target.value) || undefined,
                            }))
                          }
                          onKeyDown={(e) => {
                            if (e.key === '-' || e.key === 'e') {
                              e.preventDefault();
                            }
                          }}
                        />
                      </div>
                    </div>
                  </div>

                  <h5 className="mt-4">Aislamiento Horizontal</h5>
                  <div className="row">
                    <div className="col-md-4">
                      <div className="form-group">
                        <label>λ [W/mK]</label>
                        <input
                          type="number"
                          min="0"
                          step="any"
                          className="form-control"
                          value={newDetail.horizontal_lambda || ''}
                          onChange={(e) =>
                            setNewDetail((prev) => ({
                              ...prev,
                              horizontal_lambda: parseFloat(e.target.value) || undefined,
                            }))
                          }
                          onKeyDown={(e) => {
                            if (e.key === '-' || e.key === 'e') {
                              e.preventDefault();
                            }
                          }}
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
                          value={newDetail.horizontal_e_aisl || ''}
                          onChange={(e) =>
                            setNewDetail((prev) => ({
                              ...prev,
                              horizontal_e_aisl: parseFloat(e.target.value) || undefined,
                            }))
                          }
                          onKeyDown={(e) => {
                            if (e.key === '-' || e.key === 'e') {
                              e.preventDefault();
                            }
                          }}
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
                          value={newDetail.horizontal_d || ''}
                          onChange={(e) =>
                            setNewDetail((prev) => ({
                              ...prev,
                              horizontal_d: parseFloat(e.target.value) || undefined,
                            }))
                          }
                          onKeyDown={(e) => {
                            if (e.key === '-' || e.key === 'e') {
                              e.preventDefault();
                            }
                          }}
                        />
                      </div>
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
                    value={newDetail.colorExterior}
                    onChange={(e) =>
                      setNewDetail((prev) => ({
                        ...prev,
                        colorExterior: e.target.value,
                      }))
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
                    value={newDetail.colorInterior}
                    onChange={(e) =>
                      setNewDetail((prev) => ({
                        ...prev,
                        colorInterior: e.target.value,
                      }))
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

export default NewDetailCreator;
