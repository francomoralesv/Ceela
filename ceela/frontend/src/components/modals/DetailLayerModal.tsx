import { Detail } from "@/types/administration";
import CustomButton from "../common/CustomButton";
import TablesParameters from "../tables/TablesParameters";
import { createDetail } from "@/service/details";
import { useApi } from "@/hooks/useApi";
import { useState } from "react";
import { IConstant } from "@/shared/interfaces/constant.interface";
import { IMaterial } from "@/shared/interfaces/material.interface";
import { notify } from "@/utils/notify";
import ModalCreate from "../common/ModalCreate";
import DeleteDetailButton from "../common/DeleteDetailButton";
import ActionButtonsConfirm from "../common/ActionButtonsConfirm";

import GooIcons from "public/GoogleIcons";

export const DetailLayerModal = ({ showDetallesModal, setShowDetallesModal, selectedItem, onDelete, onUpdate, projectId }: { showDetallesModal: boolean, selectedItem: any, projectId: string, onDelete?: (deleteItem: any) => void, onUpdate?: (deleteItem?: any) => void, setShowDetallesModal: (state: boolean) => void }) => {
    const [showDeleteModal, setShowDeleteModal] = useState(false);
    const [deleteItem, setDeleteItem] = useState<{ id: number; type: "window" | "door" | "detail" } | null>(null);
    const handleDeleteDetail = (detail: Detail) => {
        setDeleteItem({ id: detail.id_detail || 0, type: "detail" });
        setShowDeleteModal(true);
    };

    const api = useApi()
    const [detailList, SetDetailsList] = useState<Detail[]>([]);
    const confirmDelete = async () => {
        try {
            if (deleteItem === null) return;
            let url = "";
            if (deleteItem.type === "detail") {
                url = `/user/details/${deleteItem.id}/delete?project_id=${projectId}`;
            } else {
                url = `/user/elements/${deleteItem.id}/delete?type=${deleteItem.type}`;
            }
            await api.del(url);
            if (onDelete)
                onDelete(deleteItem)
        } catch (error) {
            console.error("Error al eliminar:", error);
            notify("Error al eliminar");
        } finally {
            setShowDeleteModal(false);
            setDeleteItem(null);
        }
    };

    const columnsDetails = [
        { headerName: "Nombre Detalle", field: "name_detail" },
        { headerName: "Material", field: "material" },
        { headerName: "Espesor capa (cm)", field: "layer_thickness" },
        { headerName: "Acción", field: "acciones" },
    ];
    const [materials, setMaterials] = useState<IMaterial[]>([]);
    const [editingDetail, setEditingDetail] = useState<Detail | null>(null);
    const fetchMaterials = async () => {
        try {
            const url = `/user/constants/?page=1&per_page=700`;
            const response = await api.get(url);
            const allConstants: IConstant[] = response.constants || [];
            const materialsList: IMaterial[] = allConstants
                .filter(
                    (c: IConstant) =>
                        c.name === "materials" && c.type === "definition materials"
                )
                .map((c: IConstant) => ({
                    id: c.id,
                    name: c.atributs.name,
                }));
            setMaterials(materialsList);
        } catch (error: unknown) {
            console.error("Error al obtener materiales:", error);
        }
    };
    const [editingDetailData, setEditingDetailData] = useState<{ material_id: number; layer_thickness: number; }>({
        material_id: 0,
        layer_thickness: 0,
    });
    const [editingDetailId, setEditingDetailId] = useState<number | null>(null);
    const [isEditing, setIsEditing] = useState(false);
    const handleEditDetail = (detail: Detail) => {
        setEditingDetail(detail);
        if (materials.length === 0) fetchMaterials();
    };
    const handleConfirmEditDetail = async () => {
        if (!editingDetail) return;
        if (!editingDetail.scantilon_location.trim() || !editingDetail.name_detail.trim()) {
            notify("Los campos 'Ubicación Detalle' y 'Nombre Detalle' no pueden estar vacíos.");
            return;
        }
        if (!editingDetail.material_id || editingDetail.material_id <= 0) {
            notify("Por favor, seleccione un material válido.");
            return;
        }
        if (editingDetail.layer_thickness === null || editingDetail.layer_thickness <= 0) {
            notify("El 'Espesor de la capa' debe ser un valor mayor a 0.");
            return;
        }
        try {
            await api.patch(`/user/detail-update/${editingDetail.id_detail || editingDetail?.id}`, {
                scantilon_location: editingDetail.scantilon_location,
                name_detail: editingDetail.name_detail,
                material_id: editingDetail.material_id,
                layer_thickness: editingDetail.layer_thickness,
            });
            notify("Detalle actualizado exitosamente");
            // Se refrescan todas las tablas involucradas
            if (onUpdate)
                onUpdate()
            setEditingDetail(null);
        } catch (error: unknown) {
            console.error("Error al actualizar el detalle:", error);
            notify("Error al actualizar el Detalle.");
        }
    };

    const handleCancelInlineEdit = () => { setEditingDetailId(null); };
    // Funciones de edición inline en el Modal de Detalles
    const handleInlineEdit = (detail: Detail) => {
        const uniqueId = detail.id_detail || Number(detail.id);
        setEditingDetailId(uniqueId);
        setEditingDetailData({ material_id: detail.material_id, layer_thickness: detail.layer_thickness });
    };
    const handleConfirmInlineEdit = async (detail: Detail) => {
        const uniqueId = detail.id_detail || Number(detail.id);
        if (editingDetailData.material_id <= 0) {
            notify("Por favor, seleccione un material válido.");
            return;
        }
        if (editingDetailData.layer_thickness <= 0) {
            notify("El 'Espesor de capa' debe ser un valor mayor a 0.");
            return;
        }
        try {
            const url = `/user/detail-update/${uniqueId}`;
            await api.patch(url, {
                scantilon_location: detail.scantilon_location,
                name_detail: detail.name_detail,
                material_id: editingDetailData.material_id,
                layer_thickness: editingDetailData.layer_thickness,
            });
            notify("Detalle actualizado exitosamente");
            // Se refrescan todos los detalles
            fetchDetailModal(selectedItem?.id);
            if (onUpdate) {
                onUpdate();
            }
        } catch (error) {
            console.error("Error al actualizar el detalle:", error);
            notify("Error al actualizar el detalle.");
        }
        setEditingDetailId(null);
    };
    const data = detailList?.map((det: any) => {
        const uniqueId = det.id_detail || det.id;
        const textStyle = det.created_status === "created" ? { color: "var(--primary-color)", fontWeight: "bold" } : {};
        const isEditing = editingDetailId === uniqueId;
        return {
            scantilon_location: <span style={textStyle}>{det.scantilon_location}</span>,
            name_detail: <span style={textStyle}>{det.name_detail}</span>,
            material: isEditing ? (
                <select
                    className="form-control"
                    value={editingDetailData.material_id}
                    onChange={(e) =>
                        setEditingDetailData((prev) => ({ ...prev, material_id: Number(e.target.value) }))
                    }
                    onClick={fetchMaterials}
                >
                    <option value={0}>Seleccione un material</option>
                    {materials.map((mat) => (
                        <option key={mat.id} value={mat.id}>{mat.name}</option>
                    ))}
                </select>
            ) : (
                <span style={textStyle}>
                    {det.material && det.material !== "0" && det.material.toUpperCase() !== "N/A" ? det.material : "-"}
                </span>
            ),
            layer_thickness: isEditing ? (
                <input
                    type="number"
                    className="form-control"
                    min="0"
                    step="any"
                    value={editingDetailData.layer_thickness}
                    onKeyDown={(e) => { if (e.key === "-") e.preventDefault(); }}
                    onChange={(e) =>
                        setEditingDetailData((prev) => ({ ...prev, layer_thickness: Number(e.target.value) }))
                    }
                />
            ) : (
                <span style={textStyle}>
                    {det.layer_thickness && det.layer_thickness > 0 ? det.layer_thickness : "-"}
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
                    <DeleteDetailButton
                        detailId={det.id}
                        onDelete={() => { fetchDetailModal(selectedItem?.id); }}
                    />
                </>
            ),
        };
    });

    console.log("data",data)
    const fetchDetailModal = (detail_id: any) => {
        api.get(`detail-part/${detail_id}`).then((data) => {
            SetDetailsList(data);
        });
    };
    return (
        <>
        
      <GooIcons />
            <ModalCreate
                detail={null}
                isOpen={showDetallesModal}
                title="Detalles Generales"
                onClose={() => setShowDetallesModal(false)}
                onSave={() => { }}
                hideFooter={true}
                modalStyle={{ maxWidth: "70%", width: "70%", padding: "32px" }}
            >
                <div>
                    <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: "1rem" }}>
                        <CustomButton
                            variant="save"
                            onClick={() => {
                                createDetail(selectedItem?.id).then(() => {
                                    fetchDetailModal(selectedItem?.id);
                                });
                            }}
                        >
                            + Nuevo
                        </CustomButton>
                    </div>
                    <TablesParameters columns={columnsDetails} data={data} />
                </div>
            </ModalCreate>

            {showDeleteModal && deleteItem && (
                <ModalCreate
                    isOpen={showDeleteModal}
                    title="Confirmar Eliminación"
                    onClose={() => setShowDeleteModal(false)}
                    onSave={confirmDelete}
                    detail={null}
                    hideFooter={false}
                    modalStyle={{ maxWidth: "500px", width: "500px", padding: "24px" }}
                    saveLabel="Confirmar"
                >
                    <p>
                        {deleteItem.type === "detail"
                            ? "¿Estás seguro de que deseas eliminar este detalle?"
                            : deleteItem.type === "window"
                                ? "¿Estás seguro de que deseas eliminar esta ventana?"
                                : "¿Estás seguro de que deseas eliminar esta puerta?"}
                    </p>
                </ModalCreate>
            )}
        </>
    );
};
