import ActionButtonsConfirm from "@/components/common/ActionButtonsConfirm";
import CustomButton from "@/components/common/CustomButton";
import DeleteDetailButton from "@/components/common/DeleteDetailButton";
import ModalCreate from "@/components/common/ModalCreate";
import TablesParameters from "@/components/tables/TablesParameters";
import { constantUrlApiEndpoint } from "@/utils/constant-url-endpoint";
import { notify } from "@/utils/notify";
import axios from "axios";
import React, { useCallback, useEffect, useState } from "react";

export interface Detail {
  id_detail?: number;
  id?: number;
  scantilon_location: string;
  name_detail: string;
  material_id: number;
  material: string;
  layer_thickness: number;
  created_status: string; // "default", "created" o "global"
}

export interface Material {
  id: number;
  name: string;
}

interface DetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedItem: { id: number; name_detail: string };
  refreshParent?: () => void;
  materials: Material[];
  fetchMaterials: () => void;
}

const DetailModal: React.FC<DetailModalProps> = ({
  isOpen,
  onClose,
  selectedItem,
  refreshParent,
  materials,
  fetchMaterials,
}) => {
  const [details, setDetails] = useState<Detail[]>([]);
  const [editingDetailId, setEditingDetailId] = useState<number | null>(null);
  const [editingDetailData, setEditingDetailData] = useState<{
    material_id: number;
    layer_thickness: number;
  }>({
    material_id: 0,
    layer_thickness: 0,
  });

  // Estado para el Modal "Crear nuevo detalle"
  const [isNewDetailModalOpen, setIsNewDetailModalOpen] = useState(false);
  const [newDetailData, setNewDetailData] = useState<{
    scantilon_location: string;
    name_detail: string;
    material_id: number;
    layer_thickness: number;
  }>({
    scantilon_location: "",
    name_detail: "",
    material_id: 0,
    layer_thickness: 0,
  });

  // ======================================================
  // =            OBTENER LISTA DE DETALLES              =
  // ======================================================
  const fetchDetails = useCallback(async () => {
    if (!selectedItem?.id) return;
    const token = localStorage.getItem("token");
    if (!token) {
      notify("Token no encontrado, por favor inicia sesión");
      return;
    }
    try {
      const headers = { Authorization: `Bearer ${token}` };
      const response = await axios.get(
        `${constantUrlApiEndpoint}/detail-part/${selectedItem.id}`,
        { headers }
      );
      setDetails(response.data);
    } catch (error) {
      console.error("Error fetching details:", error);
      notify("Error al obtener detalles");
    }
  }, [selectedItem]);

  useEffect(() => {
    if (isOpen) {
      fetchDetails();
    }
  }, [isOpen, fetchDetails]);

  // ======================================================
  // =            OBTENER INFORMACIÓN DE DETALLE          =
  // ======================================================
  const fetchDetailInfo = async (detailId: number) => {
    const token = localStorage.getItem("token");
    if (!token) {
      notify("Token no encontrado, por favor inicia sesión");
      return null;
    }
    try {
      const headers = { Authorization: `Bearer ${token}` };
      const response = await axios.get(
        `${constantUrlApiEndpoint}/admin/detail-part/${detailId}`,
        { headers }
      );
      return response.data;
    } catch (error) {
      console.error("Error fetching detail info:", error);
      notify("Error al obtener información del detalle");
      return null;
    }
  };

  // ======================================================
  // =   ABRIR EL MODAL Y PRELLENAR CON DATOS DE TABLA    =
  // ======================================================
  const handleOpenNewDetailModal = async () => {
    if (!selectedItem?.id) return;

    const detailInfo = await fetchDetailInfo(selectedItem.id);
    if (!detailInfo) return;

    setNewDetailData({
      scantilon_location: detailInfo.type || "",
      name_detail: detailInfo.name_detail || "",
      material_id: 0,
      layer_thickness: 0,
    });

    setIsNewDetailModalOpen(true);
  };

  // ======================================================
  // =            CREAR NUEVO DETALLE (MODAL)             =
  // ======================================================
  const handleCreateDetail = async () => {
    if (!selectedItem?.id) return;
    const token = localStorage.getItem("token");
    if (!token) {
      notify("Token no encontrado, por favor inicia sesión");
      return;
    }

    // Validaciones simples
    if (!newDetailData.scantilon_location) {
      notify("Por favor, indica la ubicación del detalle.");
      return;
    }
    if (!newDetailData.name_detail) {
      notify("Por favor, indica el nombre del detalle.");
      return;
    }
    if (newDetailData.material_id <= 0) {
      notify("Por favor, selecciona un material.");
      return;
    }
    if (newDetailData.layer_thickness <= 0) {
      notify("El espesor de capa debe ser mayor a 0.");
      return;
    }

    try {
      const headers = { Authorization: `Bearer ${token}` };
      await axios.post(
        `${constantUrlApiEndpoint}/admin/detail-create/${selectedItem.id}`,
        {
          scantilon_location: newDetailData.scantilon_location,
          name_detail: newDetailData.name_detail,
          material_id: newDetailData.material_id,
          layer_thickness: newDetailData.layer_thickness,
        },
        { headers }
      );
      notify("Detalle creado exitosamente");
      setIsNewDetailModalOpen(false);

      // Limpia los campos del modal
      setNewDetailData({
        scantilon_location: "",
        name_detail: "",
        material_id: 0,
        layer_thickness: 0,
      });

      // Recarga lista de detalles
      fetchDetails();
      if (refreshParent) {
        refreshParent();
      }
    } catch (error) {
      console.error("Error creating new detail:", error);
      notify("Error al crear detalle");
    }
  };

  // ======================================================
  // =         EDICIÓN EN LÍNEA DE DETALLES EXISTENTES    =
  // ======================================================
  const handleInlineEdit = (detail: Detail) => {
    const idDetail = detail.id_detail ?? detail.id;
    setEditingDetailId(idDetail || null);
    setEditingDetailData({
      material_id: detail.material_id,
      layer_thickness: detail.layer_thickness,
    });
  };

  const handleConfirmInlineEdit = async (detail: Detail) => {
    const idDetail = detail.id_detail ?? detail.id;
    if (!idDetail) {
      notify("ID de detalle inválido: undefined");
      return;
    }
    if (editingDetailData.material_id <= 0) {
      notify("Por favor, seleccione un material válido.");
      return;
    }
    if (editingDetailData.layer_thickness <= 0) {
      notify("El 'Espesor de capa' debe ser un valor mayor a 0.");
      return;
    }
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        notify("Token no encontrado");
        return;
      }
      const url = `${constantUrlApiEndpoint}/admin/detail-update/${idDetail}`;
      const headers = {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      };
      const payload = {
        scantilon_location: detail.scantilon_location,
        name_detail: detail.name_detail,
        material_id: editingDetailData.material_id,
        layer_thickness: editingDetailData.layer_thickness,
      };
      await axios.patch(url, payload, { headers });
      notify("Detalle actualizado exitosamente");
      fetchDetails();
      if (refreshParent) {
        refreshParent();
      }
    } catch (error) {
      console.error("Error updating detail:", error);
      notify("Error al actualizar el detalle.");
    }
    setEditingDetailId(null);
  };

  const handleCancelInlineEdit = () => {
    setEditingDetailId(null);
  };

  // ======================================================
  // =         COLUMNAS Y DATOS PARA TABLA DETALLES       =
  // ======================================================
  const columnsDetails = [
    { headerName: "Nombre Detalle", field: "name_detail" },
    { headerName: "Material", field: "material" },
    { headerName: "Espesor capa (cm)", field: "layer_thickness" },
    { headerName: "Acción", field: "accion" },
  ];

  const data = details.map((det: Detail) => {
    const idDetail = det.id_detail ?? det.id;
    const isEditing = editingDetailId === idDetail;
    const textStyle =
      det.created_status === "created" || det.created_status === "global"
        ? { color: "var(--primary-color)", fontWeight: "bold" }
        : {};

    return {
      scantilon_location: (
        <span style={textStyle}>{det.scantilon_location}</span>
      ),
      name_detail: <span style={textStyle}>{det.name_detail}</span>,
      material: isEditing ? (
        <select
          className="form-control"
          value={editingDetailData.material_id}
          onChange={(e) =>
            setEditingDetailData((prev) => ({
              ...prev,
              material_id: Number(e.target.value),
            }))
          }
          onClick={fetchMaterials}
        >
          <option value={0}>Seleccione un material</option>
          {materials.map((mat) => (
            <option key={mat.id} value={mat.id}>
              {mat.name}
            </option>
          ))}
        </select>
      ) : (
        <span style={textStyle}>
          {det.material &&
            det.material !== "0" &&
            det.material.toUpperCase() !== "N/A"
            ? det.material
            : "-"}
        </span>
      ),
      layer_thickness: isEditing ? (
        <input
          type="number"
          className="form-control"
          min="0"
          step="any"
          value={editingDetailData.layer_thickness}
          onKeyDown={(e) => {
            if (e.key === "-") e.preventDefault();
          }}
          onChange={(e) =>
            setEditingDetailData((prev) => ({
              ...prev,
              layer_thickness: Number(e.target.value),
            }))
          }
        />
      ) : (
        <span style={textStyle}>
          {det.layer_thickness && det.layer_thickness > 0
            ? det.layer_thickness
            : "-"}
        </span>
      ),
      accion: isEditing ? (
        <ActionButtonsConfirm
          onAccept={() => handleConfirmInlineEdit(det)}
          onCancel={handleCancelInlineEdit}
        />
      ) : (
        <>
          <CustomButton
            className="btn-table"
            variant="editIcon"
            onClick={() => handleInlineEdit(det)}
          >
            Editar
          </CustomButton>
          {/* Se reemplaza la eliminación manual por el componente DeleteDetailButton */}
          <DeleteDetailButton
            detailId={idDetail!}
            onDelete={() => {
              fetchDetails();
              if (refreshParent) {
                refreshParent();
              }
            }}
          />
        </>
      ),
    };
  });

  // ======================================================
  // =                  RENDER DEL MODAL                  =
  // ======================================================
  return (
    <ModalCreate
      isOpen={isOpen}
      title={`Detalles ${selectedItem?.name_detail || ""}`}
      onSave={() => { }}
      onClose={onClose}
      modalStyle={{ maxWidth: "70%", width: "70%", padding: "32px" }}
      showSaveButton={false}
    >
      {/* Botón que abre el Modal "Crear nuevo detalle" con valores prellenados */}
      <div
        style={{
          display: "flex",
          justifyContent: "flex-end",
          marginBottom: "1rem",
        }}
      >
        <CustomButton variant="save" onClick={handleOpenNewDetailModal}>
          + Nuevo
        </CustomButton>
      </div>

      <TablesParameters columns={columnsDetails} data={data} />

      {/* Modal interno para CREAR un nuevo Detalle */}
      <ModalCreate
        isOpen={isNewDetailModalOpen}
        title="Crear capas (de Interior a Exterior)"
        onSave={handleCreateDetail}
        onClose={() => setIsNewDetailModalOpen(false)}
        modalStyle={{ maxWidth: "40%", width: "40%", padding: "16px" }}
        saveLabel="Crear Capa"
      >
        <div style={{ marginBottom: "1rem" }}>
          <label>Ubicación del Detalle:</label>
          <input
            type="text"
            className="form-control"
            value={newDetailData.scantilon_location}
            readOnly
          />
        </div>

        <div style={{ marginBottom: "1rem" }}>
          <label>Nombre del muro:</label>
          <input
            type="text"
            className="form-control"
            value={newDetailData.name_detail}
            readOnly
          />
        </div>

        <div style={{ marginBottom: "1rem" }}>
          <label>Material:</label>
          <select
            className="form-control"
            value={newDetailData.material_id}
            onChange={(e) =>
              setNewDetailData((prev) => ({
                ...prev,
                material_id: Number(e.target.value),
              }))
            }
            onClick={fetchMaterials}
          >
            <option value={0}>Seleccione un material</option>
            {materials.map((mat) => (
              <option key={mat.id} value={mat.id}>
                {mat.name}
              </option>
            ))}
          </select>
        </div>

        <div style={{ marginBottom: "1rem" }}>
          <label>Espesor de Capa (cm):</label>
          <input
            type="number"
            className="form-control"
            min="0"
            step="any"
            placeholder="cm"
            value={
              newDetailData.layer_thickness > 0
                ? newDetailData.layer_thickness
                : ""
            }
            onKeyDown={(e) => {
              // Evitar que ingrese valores negativos
              if (e.key === "-") e.preventDefault();
            }}
            onChange={(e) =>
              setNewDetailData((prev) => ({
                ...prev,
                layer_thickness: Number(e.target.value),
              }))
            }
          />
        </div>
      </ModalCreate>
    </ModalCreate>
  );
};

export default DetailModal;
