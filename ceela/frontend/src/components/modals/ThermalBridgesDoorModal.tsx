import React, { ChangeEvent, FC, useEffect, useState } from "react";
import ModalCreate from "../common/ModalCreate";
import { ThermalBridge } from "@/shared/interfaces/thermalBridge.interface";
import { WallDetail } from "@/shared/interfaces/WallDetail.interface";
import { constantUrlApiEndpoint } from "@/utils/constant-url-endpoint";
import { notify } from "@/utils/notify";

interface ThermalBridgesModalProps {
  isOpen: boolean;
  handleClose: () => void;
  bridgeId: number | null;
  bridgeData: ThermalBridge | null;
  detailOptions?: WallDetail[];
  onSaveSuccess?: () => void; // Callback to trigger after saving
}

const ThermalBridgesDoorModal: FC<ThermalBridgesModalProps> = (props) => {
  const token = localStorage.getItem("token") || "";

  const [editingBridgeId, setEditingBridgeId] = useState<number | null>(null);
  const [editingBridgeData, setEditingBridgeData] =
    useState<ThermalBridge | null>();
  const [favEditData, setFavEditData] = useState<any>(null);

  /*const [detailOptions, setDetailOptions] = useState<WallDetail[]>(
    props.detailOptions
  );*/
  useEffect(() => {
    console.log("data mounted");
    console.log("props.bridgeId", props.bridgeId);
    console.log("props.favEditData", props.bridgeData);
    setFavEditData(props.bridgeData);
    // console.log("props.bridgeData", props.bridgeData);
    // setDetailOptions(props.detailOptions);
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
  // ThermalBridgesModalSave
  async function handleSaveThermalBridgesModal() {
    // Aquí puedes definir la lógica para guardar los puentes térmicos
    // console.log("props.detailOptions", detailOptions);
    console.log("Guardar puentes térmicos");

    const {
      fav1D,
      fav1L,
      fav2izq_P,
      fav2izq_S,
      fav2der_P,
      fav2der_S,
      fav3_E,
      fav3_T,
      fav3_beta,
      fav3_alpha,
    } = favEditData;

    if (
      fav1D < 0 ||
      fav1L < 0 ||
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

    const authData = getAuthData();
    if (!authData) return;
    try {
      const response = await fetch(
        `${constantUrlApiEndpoint}/door/fav-enclosures-update/${favEditData.fav_id}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            fav1: { d: favEditData.fav1D, l: favEditData.fav1L },
            fav2_izq: { p: favEditData.fav2izqP, s: favEditData.fav2izqS },
            fav2_der: { p: favEditData.fav2DerP, s: favEditData.fav2DerS },
            fav3: {
              e: favEditData.fav3E,
              t: favEditData.fav3T,
              beta: favEditData.fav3Beta,
              alfa: favEditData.fav3Alpha,
            },
          }),
        }
      );
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
      notify("Error al actualizar puente térmico");
      console.error(error);
    }

    props.handleClose();
  }
  const handleFavEditChange = (field: string, value: any) => {
    setFavEditData((prev: any) => ({ ...prev, [field]: value }));
  };
  // ThermalBridgesModalClose
  function handleCloseThermalBridgesModal() {
    // Aquí puedes definir la lógica para guardar los puentes térmicos
    console.log("Cerrar puentes térmicos");
    setEditingBridgeId(null);
    setEditingBridgeData(null);
    props.handleClose();
  }
  // Estilo para inputs FAV
  const favInputStyle = { height: "20px", fontSize: "14px", width: "120px" };

  const handleEditBridgeChange = (
    e: ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setEditingBridgeData((prev) =>
      prev
        ? { ...prev, [name]: name.startsWith("po") ? Number(value) : value }
        : null
    );
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
              value={favEditData?.fav1D ?? ""}
              onKeyDown={(e) => {
                if (e.key === "-") {
                  e.preventDefault();
                }
              }}
              onChange={(e) =>
                handleFavEditChange("fav1D", Number(e.target.value))
              }
            />
          </div>
          <div className="col-4">
            <label htmlFor="po1_length" className="form-label">
              L [m]
            </label>
            <input
              type="number"
              min="0"
              step="any"
              className="form-control"
              style={favInputStyle}
              value={favEditData?.fav1L ?? ""}
              onKeyDown={(e) => {
                if (e.key === "-") {
                  e.preventDefault();
                }
              }}
              onChange={(e) =>
                handleFavEditChange("fav1L", Number(e.target.value))
              }
            />
          </div>
        </div>
        <div className="flex flex-col gap-4">FAV 2 Izq</div>
        <div className="row mb-3">
          <div className="col-4">
            <label htmlFor="po2_length">P [m]</label>
            <input
              type="number"
              min="0"
              step="any"
              className="form-control"
              style={favInputStyle}
              value={favEditData?.fav2izqP ?? ""}
              onKeyDown={(e) => {
                if (e.key === "-") {
                  e.preventDefault();
                }
              }}
              onChange={(e) =>
                handleFavEditChange("fav2izqP", Number(e.target.value))
              }
            />
          </div>
          <div className="col-4">
            <label htmlFor="po2_length">S [m]</label>
            <input
              type="number"
              min="0"
              step="any"
              className="form-control"
              style={favInputStyle}
              value={favEditData?.fav2izqS ?? ""}
              onKeyDown={(e) => {
                if (e.key === "-") {
                  e.preventDefault();
                }
              }}
              onChange={(e) =>
                handleFavEditChange("fav2izqS", Number(e.target.value))
              }
            />
          </div>
        </div>
        <div className="flex flex-col gap-4">FAV 2 DER</div>
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
              value={favEditData?.fav2DerP ?? ""}
              onKeyDown={(e) => {
                if (e.key === "-") {
                  e.preventDefault();
                }
              }}
              onChange={(e) =>
                handleFavEditChange("fav2DerP", Number(e.target.value))
              }
            />
          </div>
          <div className="col-4">
            <label htmlFor="po3_length" className="form-label">
              S [m]
            </label>
            <input
              type="number"
              min="0"
              step="any"
              className="form-control"
              style={favInputStyle}
              value={favEditData?.fav2DerS ?? ""}
              onKeyDown={(e) => {
                if (e.key === "-") {
                  e.preventDefault();
                }
              }}
              onChange={(e) =>
                handleFavEditChange("fav2DerS", Number(e.target.value))
              }
            />
          </div>
        </div>
        <div className="flex flex-col gap-4">FAV 3</div>
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
              value={favEditData?.fav3E ?? ""}
              onKeyDown={(e) => {
                if (e.key === "-") {
                  e.preventDefault();
                }
              }}
              onChange={(e) =>
                handleFavEditChange("fav3E", Number(e.target.value))
              }
            />
          </div>
          <div className="col-3">
            <label htmlFor="po4_length" className="form-label">
              T [m]
            </label>
            <input
              type="number"
              min="0"
              step="any"
              className="form-control"
              style={favInputStyle}
              value={favEditData?.fav3T ?? ""}
              onKeyDown={(e) => {
                if (e.key === "-") {
                  e.preventDefault();
                }
              }}
              onChange={(e) =>
                handleFavEditChange("fav3T", Number(e.target.value))
              }
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
              value={favEditData?.fav3Beta ?? ""}
              onKeyDown={(e) => {
                if (e.key === "-") {
                  e.preventDefault();
                }
              }}
              onChange={(e) =>
                handleFavEditChange("fav3Beta", Number(e.target.value))
              }
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
              value={favEditData?.fav3Alpha ?? ""}
              onKeyDown={(e) => {
                if (e.key === "-") {
                  e.preventDefault();
                }
              }}
              onChange={(e) =>
                handleFavEditChange("fav3Alpha", Number(e.target.value))
              }
            />
          </div>
        </div>
      </div>
    </ModalCreate>
  );
};

export default ThermalBridgesDoorModal;
