import CustomButton from "@/components/common/CustomButton";
import TablesParameters from "@/components/tables/TablesParameters";
import AddDetailOnLayer from "../AddDetailOnLayer";
import { useState } from "react";
import ActionButtonsConfirm from "@/components/common/ActionButtonsConfirm";
import ModalCreate from "@/components/common/ModalCreate";

interface MuroItem {
    id?: number;
    id_detail?: number;
    name_detail: string;
    value_u?: number;
    info?: {
        surface_color?: {
            exterior?: { name: string };
            interior?: { name: string };
        };
    };
}

interface MurosTableProps {
    murosTabList: MuroItem[];
    handleConfirmEdit: (item: MuroItem) => void;
    handleCancelEdit: (item: MuroItem) => void;
    handleEditClick: (item: MuroItem) => void;
    fetchDetailModal?: (id: number) => void;
    confirmDeleteDetail?: (id: number) => void;
}

const DetailModalContent = ({detailsList}:{detailsList:any}) => {

    const columnsDetails = [
        { headerName: "Nombre Detalle", field: "name_detail" },
        { headerName: "Material", field: "material" },
        { headerName: "Espesor capa (cm)", field: "layer_thickness" },
        { headerName: "Acción", field: "accion" },
    ];

    const data = detailsList?.map((det: any) => {
        const textStyle =
            det.created_status === "created"
                ? { color: "var(--primary-color)", fontWeight: "bold" }
                : {};
        return {
            scantilon_location: (
                <span style={textStyle}>{det.scantilon_location}</span>
            ),
            name_detail: <span style={textStyle}>{det.name_detail}</span>,
            material: <span style={textStyle}>{det.material}</span>,
            layer_thickness: <span style={textStyle}>{det.layer_thickness}</span>,
            accion: (
                <>
                    <CustomButton
                        className="btn-table"
                        variant="editIcon"
                        disabled={
                            det.created_status === "default" || det.created_status === "global"
                        }
                    >
                        Editar
                    </CustomButton>
                    <CustomButton
                        className="btn-table"
                        variant="deleteIcon"
                        disabled={
                            det.created_status === "default" || det.created_status === "global"
                        }
                    >
                        <span className="material-icons">delete</span>
                    </CustomButton>
                </>
            ),
        };
    });

    return (
        <>
            <div
                style={{
                    display: "flex",
                    justifyContent: "flex-end",
                    marginBottom: "1rem",
                }}
            >
                <CustomButton variant="save" onClick={async () => {
     

                }}>
                    + Nuevo
                </CustomButton>
            </div>
            <TablesParameters columns={columnsDetails} data={data} />
            <div
                style={{
                    display: "flex",
                    justifyContent: "flex-end",
                    marginTop: "1rem",
                }}
            ></div>
        </>
    );
};

export const MurosTable = ({
    murosTabList,
    handleConfirmEdit,
    handleCancelEdit,
    handleEditClick,
    fetchDetailModal,
    confirmDeleteDetail
}: MurosTableProps) => {
    const [showDetallesModal, setShowDetallesModal] = useState(false);
    const [selectedItem, setSelectedItem] = useState<MuroItem | null>(null);
    const [editingRowId, setEditingRowId] = useState<number | null>(null);
    const [editingColors, setEditingColors] = useState({
        interior: "Intermedio",
        exterior: "Intermedio"
    });

    const columnsMuros = [
        { headerName: "Nombre Abreviado", field: "nombreAbreviado" },
        { headerName: "Valor U (W/m²K)", field: "valorU" },
        { headerName: "Color Exterior", field: "colorExterior" },
        { headerName: "Color Interior", field: "colorInterior" },
        { headerName: "Acciones", field: "acciones" },
    ];

    const OnDetailOpened = (item: MuroItem) => {
        setSelectedItem(item);
        setShowDetallesModal(true);
        if (fetchDetailModal && item.id) {
            fetchDetailModal(item.id);
        }
    };

    const murosData = murosTabList.map((item) => {
        const isEditing = editingRowId === item.id;
        return {
            nombreAbreviado: item.name_detail,
            valorU: item.value_u?.toFixed(3) ?? "--",
            colorExterior: isEditing ? (
                <select
                    value={editingColors.exterior}
                    onChange={(e) =>
                        setEditingColors((prev) => ({
                            ...prev,
                            exterior: e.target.value,
                        }))
                    }
                >
                    <option value="Claro">Claro</option>
                    <option value="Oscuro">Oscuro</option>
                    <option value="Intermedio">Intermedio</option>
                </select>
            ) : (
                item.info?.surface_color?.exterior?.name || "Desconocido"
            ),
            colorInterior: isEditing ? (
                <select
                    value={editingColors.interior}
                    onChange={(e) =>
                        setEditingColors((prev) => ({
                            ...prev,
                            interior: e.target.value,
                        }))
                    }
                >
                    <option value="Claro">Claro</option>
                    <option value="Oscuro">Oscuro</option>
                    <option value="Intermedio">Intermedio</option>
                </select>
            ) : (
                item.info?.surface_color?.interior?.name || "Desconocido"
            ),
            acciones: isEditing ? (
                <div onClick={(e) => e.stopPropagation()}>
                    <ActionButtonsConfirm
                        onAccept={() => handleConfirmEdit(item)}
                        onCancel={() => handleCancelEdit(item)}
                    />
                </div>
            ) : (
                <div>
                    <AddDetailOnLayer item={item} OnDetailOpened={() => OnDetailOpened(item)} />
                    <CustomButton
                        className="btn-table"
                        variant="editIcon"
                        onClick={(e) => {
                            e.stopPropagation();
                            handleEditClick(item);
                            setEditingRowId(item.id || null);
                            setEditingColors({
                                interior: item.info?.surface_color?.interior?.name || "Intermedio",
                                exterior: item.info?.surface_color?.exterior?.name || "Intermedio",
                            });
                        }}
                    >
                        Editar
                    </CustomButton>
                    <CustomButton
                        variant="deleteIcon"
                        onClick={(e: React.MouseEvent) => {
                            e.stopPropagation();
                            const detailId = item.id_detail || item.id;
                            if (detailId && confirmDeleteDetail) {
                                confirmDeleteDetail(detailId);
                            }
                        }}
                    >
                        <span className="material-icons">delete</span>
                    </CustomButton>
                </div>
            ),
        };
    });

    return (
        <div style={{ overflowX: "auto" }} >
            {murosTabList.length > 0 ? (
                <TablesParameters columns={columnsMuros} data={murosData} />
            ) : (
                <p>No hay datos</p>
            )}
            {showDetallesModal && (
                <ModalCreate
                    onSave={() => { }}
                    isOpen={true}
                    title="Detalles Generales"
                    onClose={() => setShowDetallesModal(false)}
                    modalStyle={{ maxWidth: "70%", width: "70%", padding: "32px" }}
                >
                    <DetailModalContent detailsList={undefined} />
                </ModalCreate>
            )}
        </div>
    );
};
