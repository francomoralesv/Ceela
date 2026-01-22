import React, { FC, useEffect, useState } from 'react';
import { Tooltip } from 'react-tooltip';
import CustomButton from '../common/CustomButton';
import Modal from '../common/Modal';

interface NewDetailFormData {
    scantilon_location: string;
    name_detail: string;
    material_id: number;
    layer_thickness: number | null;
}

interface NewDetailModalProps {
    showNewDetailRow: boolean;
    setShowNewDetailRow: (show: boolean) => void;
    newDetailForm: NewDetailFormData;
    setNewDetailForm: React.Dispatch<React.SetStateAction<NewDetailFormData>>;
    materials: Array<{ id: number; name: string }>;
    isViewMode?: boolean;
    handleCreateNewDetail: () => Promise<void>;
    onClose?: () => void;
}

export const NewDetailModal: FC<NewDetailModalProps> = ({
    showNewDetailRow,
    setShowNewDetailRow,
    newDetailForm,
    setNewDetailForm,
    materials,
    isViewMode=false,
    handleCreateNewDetail,
    onClose: customOnClose,
}) => {
    const [saveState, SetSaveState] = useState(false);
    useEffect(() => {
        SetSaveState(false);
    }, [showNewDetailRow]);
    if (!showNewDetailRow) return null;

    const onCreate = async () => {
        SetSaveState(true);
        await handleCreateNewDetail();
        setShowNewDetailRow(false);
        setNewDetailForm({
            scantilon_location: "",
            name_detail: "",
            material_id: 0,
            layer_thickness: null,
        });
        customOnClose?.();
    }
    const handleClose = () => {
        setShowNewDetailRow(false);
        setNewDetailForm({
            scantilon_location: "",
            name_detail: "",
            material_id: 0,
            layer_thickness: null,
        });
        customOnClose?.();
    };

    return (
        <Modal
            isOpen={showNewDetailRow}
            onClose={handleClose}
            title="Agregar Nuevo Detalle Constructivo"
        >
            <div
                style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "15px",
                    padding: "10px",
                }}
            >
                <div style={{ display: "flex", flexDirection: "column" }}>
                    <label
                    >
                        Ubicación del Detalle
                    </label>
                    <select
                        className="form-control"
                        value={newDetailForm.scantilon_location}
                        onChange={(e) =>
                            setNewDetailForm((prev) => ({
                                ...prev,
                                scantilon_location: e.target.value,
                            }))
                        }
                        disabled={isViewMode}
                    >
                        <option value="">Seleccione</option>
                        <option value="Muro">Muro</option>
                        <option value="Techo">Techo</option>
                        <option value="Piso">Piso</option>
                    </select>
                </div>

                <div style={{ display: "flex", flexDirection: "column" }}>
                    <label
                    >
                        Nombre del Detalle
                    </label>
                    <input
                        type="text"
                        className="form-control"
                        placeholder="Nombre Detalle"
                        value={newDetailForm.name_detail}
                        onChange={(e) =>
                            setNewDetailForm((prev) => ({
                                ...prev,
                                name_detail: e.target.value,
                            }))
                        }
                        disabled={isViewMode}
                    />
                </div>

                <div style={{ display: "flex", flexDirection: "column" }}>
                    <label
                    >
                        Material
                    </label>
                    <select
                        className="form-control"
                        value={newDetailForm.material_id}
                        onChange={(e) =>
                            setNewDetailForm((prev) => ({
                                ...prev,
                                material_id: parseInt(e.target.value),
                            }))
                        }
                        disabled={isViewMode}
                    >
                        <option value={0}>Seleccione un material</option>
                        {materials.map((mat) => (
                            <option key={mat.id} value={mat.id}>
                                {mat.name}
                            </option>
                        ))}
                    </select>
                </div>

                <div >
                    <label
                    >
                        Espesor de la Capa (cm)
                    </label>
                    <input
                        type="number"
                        inputMode="decimal"
                        className="form-control"
                        placeholder="Espesor (cm)"
                        value={newDetailForm.layer_thickness === null ? "" : newDetailForm.layer_thickness}
                        onKeyDown={(e) => {
                            if (e.key === "-" || e.key === "e") {
                                e.preventDefault();
                            }
                        }}
                        onChange={(e) => {
                            const inputValue = e.target.value.replace(/[^0-9.]/g, "");
                            const value = inputValue ? parseFloat(inputValue) : null;
                            if (value === null || value >= 0) {
                                setNewDetailForm((prev) => ({
                                    ...prev,
                                    layer_thickness: value,
                                }));
                            }
                        }}
                        min="0"
                        disabled={isViewMode}
                    />
                </div>
            </div>

            {!isViewMode && (
                <div
                    style={{
                        display: "flex",
                        justifyContent: "flex-end",
                        marginTop: "15px",
                        paddingRight: "15px",
                    }}
                >
                    <CustomButton
                        variant="closed"
                        onClick={handleClose}
                        id="cerrar"
                        disabled={false}
                    >
                        Cancelar
                    </CustomButton>
                    <CustomButton
                        variant="save"
                        onClick={onCreate}
                        id="grabar-datos-btn"
                        disabled={saveState}
                    >
                        Crear Detalles
                    </CustomButton>
                </div>
            )}

            <Tooltip anchorSelect="#grabar-datos-btn" place="top">
                Guardar cambios tras agregar un detalle
            </Tooltip>
        </Modal>
    );
};
