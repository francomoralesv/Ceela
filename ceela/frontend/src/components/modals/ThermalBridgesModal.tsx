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
  detailOptions: WallDetail[];
  onSaveSuccess?: () => void; // Callback to trigger after saving
}

const ThermalBridgesModal: FC<ThermalBridgesModalProps> = (props) => {
  const [editingBridgeId, setEditingBridgeId] = useState<number | null>(null);
  const [editingBridgeData, setEditingBridgeData] =
    useState<ThermalBridge | null>();
  const [detailOptions, setDetailOptions] = useState<WallDetail[]>(
    props.detailOptions
  );
  useEffect(() => {
    console.log("data mounted");
    setEditingBridgeData(props.bridgeData);
    setDetailOptions(props.detailOptions);
  });

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
    console.log("props.detailOptions", detailOptions);
    console.log("Guardar puentes térmicos");

    if (!props.bridgeId || !editingBridgeData) return;
    const authData = getAuthData();
    if (!authData) return;
    try {
      const response = await fetch(
        `${constantUrlApiEndpoint}/thermal-bridge-update/${props.bridgeId}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${authData.token}`,
          },
          body: JSON.stringify(editingBridgeData),
        }
      );
      if (!response.ok) throw new Error("Error al actualizar puente térmico");
      notify("Puente térmico actualizado exitosamente");
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
      title="Puentes Térmicos"
      saveLabel="Guardar"
    >
      <div className="flex flex-col gap-4">P01</div>
      <div className="flex flex-row gap-4">
        <input
          type="number"
          name="po1_length"
          min="0"
          step="0.01"
          value={editingBridgeData?.po1_length ?? 0}
          onKeyDown={(e) => {
            if (e.key === "-") e.preventDefault();
          }}
          onChange={handleEditBridgeChange}
          onBlur={(e) => {
            const rounded = parseFloat(e.target.value).toFixed(2);
            setEditingBridgeData({
              ...editingBridgeData!,
              po1_length: Number(rounded),
            });
          }}
          className="form-control form-control-sm"
        />
        <select
          name="po1_id_element"
          value={editingBridgeData?.po1_id_element ?? ""}
          onChange={handleEditBridgeChange}
          className="form-control form-control-sm"
        >
          <option value="">Seleccione...</option>
          {detailOptions.map((detail) => (
            <option key={detail.id} value={detail.id}>
              {detail.name_detail}
            </option>
          ))}
        </select>
      </div>
      <div className="flex flex-col gap-4">P02</div>
      <div className="flex flex-row gap-4">
        <input
          type="number"
          name="po2_length"
          min="0"
          step="0.01"
          value={editingBridgeData?.po2_length ?? 0}
          onKeyDown={(e) => {
            if (e.key === "-") e.preventDefault();
          }}
          onChange={handleEditBridgeChange}
          onBlur={(e) => {
            const rounded = parseFloat(e.target.value).toFixed(2);
            setEditingBridgeData({
              ...editingBridgeData!,
              po1_length: Number(rounded),
            });
          }}
          className="form-control form-control-sm"
        />
        <select
          name="po2_id_element"
          value={editingBridgeData?.po2_id_element ?? ""}
          onChange={handleEditBridgeChange}
          className="form-control form-control-sm"
        >
          <option value="">Seleccione...</option>
          {detailOptions.map((detail) => (
            <option key={detail.id} value={detail.id}>
              {detail.name_detail}
            </option>
          ))}
        </select>
      </div>
      <div className="flex flex-col gap-4">P03</div>
      <div className="flex flex-row gap-4">
        <input
          type="number"
          name="po3_length"
          min="0"
          step="0.01"
          value={editingBridgeData?.po3_length ?? 0}
          onKeyDown={(e) => {
            if (e.key === "-") e.preventDefault();
          }}
          onChange={handleEditBridgeChange}
          onBlur={(e) => {
            const rounded = parseFloat(e.target.value).toFixed(2);
            setEditingBridgeData({
              ...editingBridgeData!,
              po1_length: Number(rounded),
            });
          }}
          className="form-control form-control-sm"
        />
        <select
          name="po3_id_element"
          value={editingBridgeData?.po3_id_element ?? ""}
          onChange={handleEditBridgeChange}
          className="form-control form-control-sm"
        >
          <option value="">Seleccione...</option>
          {detailOptions.map((detail) => (
            <option key={detail.id} value={detail.id}>
              {detail.name_detail}
            </option>
          ))}
        </select>
      </div>
      <div className="flex flex-col gap-4">P04</div>
      <div className="flex flex-row gap-4">
        <input
          type="number"
          name="po4_length"
          min="0"
          step="0.01"
          value={editingBridgeData?.po4_length ?? 0}
          onKeyDown={(e) => {
            if (e.key === "-") e.preventDefault();
          }}
          onChange={handleEditBridgeChange}
          onBlur={(e) => {
            const rounded = parseFloat(e.target.value).toFixed(2);
            setEditingBridgeData({
              ...editingBridgeData!,
              po1_length: Number(rounded),
            });
          }}
          className="form-control form-control-sm"
        />
        <input
          type="number"
          name="po4_e_aislacion"
          min="0"
          step="0.01"
          value={editingBridgeData?.po4_e_aislacion ?? 0}
          onKeyDown={(e) => {
            if (e.key === "-") e.preventDefault();
          }}
          onChange={handleEditBridgeChange}
          onBlur={(e) => {
            const rounded = parseFloat(e.target.value).toFixed(2);
            setEditingBridgeData({
              ...editingBridgeData!,
              po4_e_aislacion: Number(rounded),
            });
          }}
          className="form-control form-control-sm"
        />
        <select
          name="po4_id_element"
          value={editingBridgeData?.po4_id_element ?? ""}
          onChange={handleEditBridgeChange}
          className="form-control form-control-sm"
        >
          <option value="">Seleccione...</option>
          {detailOptions.map((detail) => (
            <option key={detail.id} value={detail.id}>
              {detail.name_detail}
            </option>
          ))}
        </select>
      </div>
    </ModalCreate>
  );
};

export default ThermalBridgesModal;
