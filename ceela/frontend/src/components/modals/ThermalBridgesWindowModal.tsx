import React, { ChangeEvent, FC, useEffect, useState } from "react";
import ModalCreate from "../common/ModalCreate";
// import { ThermalBridgeWindow } from "@/shared/interfaces/thermalBridge.interface";
import { WallDetail } from "@/shared/interfaces/WallDetail.interface";
import { constantUrlApiEndpoint } from "@/utils/constant-url-endpoint";
import { notify } from "@/utils/notify";

interface ThermalBridgesWindowModalProps {
  isOpen: boolean;
  handleClose: () => void;
  bridgeId: number | null;
  // bridgeData: ThermalBridgeWindow | null;
  bridgeData: any;
  detailOptions: WallDetail[];
  onSaveSuccess?: () => void; // Callback to trigger after saving
}

const ThermalBridgesWindowModal: FC<ThermalBridgesWindowModalProps> = (
  props
) => {
  const favInputStyle = {
    height: "20px",
    fontSize: "14px",
    width: "120px",
  };
  const token = localStorage.getItem("token") || "";

  const [editingBridgeId, setEditingBridgeId] = useState<number | null>(null);
  const [editingBridgeData, setEditingBridgeData] = useState<Record<
    string,
    any
  > | null>(null);
  const [detailOptions, setDetailOptions] = useState<WallDetail[]>(
    props.detailOptions
  );
  const [favEditData, setFavEditData] = useState<any>(null);

  useEffect(() => {
    console.log("data mounted");
    console.log("props.bridgeId", props.bridgeId);
    console.log("props.favEditData", props.bridgeData);
    setFavEditData(props.bridgeData);
    // console.log("props.bridgeData", props.bridgeData);
    setDetailOptions(props.detailOptions);
  }, [props.bridgeId]);

  const getAuthData = () => {
    const token = localStorage.getItem("token");
    const enclosure_id = localStorage.getItem("recinto_id");
    if (!token) {
      notify("Error: No se encontró el token en el localStorage.");
      return null;
    }
    if (!enclosure_id) {
      return null;
    }
    return { token, enclosure_id };
  };

  const handleSaveThermalBridgesModal = async () => {
    const {
      fav1_D,
      fav1_L,
      fav2izq_P,
      fav2izq_S,
      fav2der_P,
      fav2der_S,
      fav3_E,
      fav3_T,
      fav3_beta,
      fav3_alpha,
    } = favEditData;

    // Validar que ninguno sea negativo
    if (
      fav1_D < 0 ||
      fav1_L < 0 ||
      fav2izq_P < 0 ||
      fav2izq_S < 0 ||
      fav2der_P < 0 ||
      fav2der_S < 0 ||
      fav3_E < 0 ||
      fav3_T < 0 ||
      fav3_beta < 0 ||
      fav3_alpha < 0
    ) {
      notify("No se permiten valores negativos en FAV");
      return;
    }

    const favUrl = `${constantUrlApiEndpoint}/window/fav-enclosures-update/${favEditData.fav_id}`;
    try {
      const response = await fetch(favUrl, {
        method: "PUT",
        headers: {
          accept: "application/json",
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          fav1: {
            d: fav1_D,
            l: fav1_L,
          },
          fav2_izq: {
            p: fav2izq_P,
            s: fav2izq_S,
          },
          fav2_der: {
            p: fav2der_P,
            s: fav2der_S,
          },
          fav3: {
            e: fav3_E,
            t: fav3_T,
            beta: fav3_beta,
            alfa: fav3_alpha,
          },
        }),
      });
      if (!response.ok) throw new Error("Error al actualizar los favs");
      const favDataResponse = await response.json();
      console.log("Actualización FAV:", favDataResponse);
      notify("FAV actualizado exitosamente");
      setEditingBridgeId(null);
      setEditingBridgeData(null);
      if (props.onSaveSuccess) {
        props.onSaveSuccess();
      }
    } catch (error) {
      console.error(error);
      notify("Error al actualizar los favs");
    }
    props.handleClose();
  };

  // ThermalBridgesModalClose
  function handleCloseThermalBridgesModal() {
    // Aquí puedes definir la lógica para guardar los puentes térmicos
    console.log("Cerrar puentes térmicos");
    setEditingBridgeId(null);
    setEditingBridgeData(null);
    props.handleClose();
  }

  const handleEditBridgeChange = (
    e: ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setEditingBridgeData((prev: Record<string, any> | null) =>
      prev
        ? { ...prev, [name]: name.startsWith("po") ? Number(value) : value }
        : null
    );
  };
  const handleFavEditChange = (field: string, value: any) => {
    setFavEditData((prev: any) => ({ ...prev, [field]: value }));
  };
  // Aquí puedes definir el contenido del modal
  return (
    <ModalCreate
      isOpen={props.isOpen}
      // onClose={props.handleClose}
      onClose={props.handleClose}
      onSave={handleSaveThermalBridgesModal}
      title="Factor de Accesibilidad"
      saveLabel="Guardar"
    >
      <div className="container-fluid p-0">
        <div className="flex flex-col gap-4">FAV 1</div>
        <div className="row mb-3">
          <div className="col-4">
            <label htmlFor="po1_length" className="form-label">
              D [m]
            </label>
            <input
              type="number"
              min="0"
              step="any"
              className="form-control"
              style={favInputStyle}
              value={favEditData?.fav1_D ?? ""}
              onChange={(e) =>
                handleFavEditChange("fav1_D", Number(e.target.value))
              }
              onKeyDown={(e) => {
                if (e.key === "-") {
                  e.preventDefault();
                }
              }}
            />
          </div>
          <div className="col-4">
            <label htmlFor="po1_id_element" className="form-label">
              L [m]
            </label>
            <input
              type="number"
              min="0"
              step="any"
              className="form-control"
              style={favInputStyle}
              value={favEditData?.fav1_L ?? ""}
              onChange={(e) =>
                handleFavEditChange("fav1_L", Number(e.target.value))
              }
              onKeyDown={(e) => {
                if (e.key === "-") {
                  e.preventDefault();
                }
              }}
            />
          </div>
        </div>
        <div className="flex flex-col gap-4">FAV 2 izq </div>
        <div className="row mb-3">
          <div className="col-4">
            <label htmlFor="po2_length">P [m] </label>
            <input
              type="number"
              min="0"
              step="any"
              className="form-control"
              style={favInputStyle}
              value={favEditData?.fav2izq_P ?? ""}
              onChange={(e) =>
                handleFavEditChange("fav2izq_P", Number(e.target.value))
              }
              onKeyDown={(e) => {
                if (e.key === "-") {
                  e.preventDefault();
                }
              }}
            />
          </div>
          <div className="col-4">
            <label htmlFor="po2_id_element" className="form-label">
              S [m]
            </label>
            <input
              type="number"
              min="0"
              step="any"
              className="form-control"
              style={favInputStyle}
              value={favEditData?.fav2izq_S ?? ""}
              onChange={(e) =>
                handleFavEditChange("fav2izq_S", Number(e.target.value))
              }
              onKeyDown={(e) => {
                if (e.key === "-") {
                  e.preventDefault();
                }
              }}
            />
          </div>
        </div>
        <div className="flex flex-col gap-4">FAV 2 Der </div>
        <div className="row mb-3">
          <div className="col-4">
            <label htmlFor="po3_length" className="form-label">
              P [m]
            </label>
            <input
              type="number"
              min="0"
              step="any"
              className="form-control"
              style={favInputStyle}
              value={favEditData?.fav2der_P ?? ""}
              onChange={(e) =>
                handleFavEditChange("fav2der_P", Number(e.target.value))
              }
              onKeyDown={(e) => {
                if (e.key === "-") {
                  e.preventDefault();
                }
              }}
            />
          </div>
          <div className="col-4">
            <label htmlFor="po3_id_element" className="form-label">
              S [m]
            </label>
            <input
              type="number"
              min="0"
              step="any"
              className="form-control"
              style={favInputStyle}
              value={favEditData?.fav2der_S ?? ""}
              onChange={(e) =>
                handleFavEditChange("fav2der_S", Number(e.target.value))
              }
              onKeyDown={(e) => {
                if (e.key === "-") {
                  e.preventDefault();
                }
              }}
            />
          </div>
        </div>
        <div className="flex flex-col gap-4">FAV 3 </div>
        <div className="row mb-3">
          <div className="col-3">
            <label htmlFor="po4_length" className="form-label">
              E [m]
            </label>
            <input
              type="number"
              min="0"
              step="any"
              className="form-control"
              style={favInputStyle}
              value={favEditData?.fav3_E ?? ""}
              onChange={(e) =>
                handleFavEditChange("fav3_E", Number(e.target.value))
              }
              onKeyDown={(e) => {
                if (e.key === "-") {
                  e.preventDefault();
                }
              }}
            />
          </div>
          <div className="col-3">
            <label htmlFor="po4_id_element" className="form-label">
              T [m]
            </label>
            <input
              type="number"
              min="0"
              step="any"
              className="form-control"
              style={favInputStyle}
              value={favEditData?.fav3_T ?? ""}
              onChange={(e) =>
                handleFavEditChange("fav3_T", Number(e.target.value))
              }
              onKeyDown={(e) => {
                if (e.key === "-") {
                  e.preventDefault();
                }
              }}
            />
          </div>
          <div className="col-3">
            <label htmlFor="po4_e_aislacion" className="form-label">
              β [°]
            </label>
            <input
              type="number"
              min="0"
              step="any"
              className="form-control"
              style={favInputStyle}
              value={favEditData?.fav3_beta ?? ""}
              onChange={(e) =>
                handleFavEditChange("fav3_beta", Number(e.target.value))
              }
              onKeyDown={(e) => {
                if (e.key === "-") {
                  e.preventDefault();
                }
              }}
            />
          </div>
          <div className="col-3">
            <label htmlFor="po4_e_aislacion" className="form-label">
              α [°]
            </label>
            <input
              type="number"
              min="0"
              step="any"
              className="form-control"
              style={favInputStyle}
              value={favEditData?.fav3_alpha ?? ""}
              onChange={(e) =>
                handleFavEditChange("fav3_alpha", Number(e.target.value))
              }
              onKeyDown={(e) => {
                if (e.key === "-") {
                  e.preventDefault();
                }
              }}
            />
          </div>
        </div>
      </div>
    </ModalCreate>
  );
};

export default ThermalBridgesWindowModal;
