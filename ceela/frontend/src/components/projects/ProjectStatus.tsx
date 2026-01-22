import Card from '@/components/common/Card';
import CustomButton from '@/components/common/CustomButton';
import Modal from '@/components/common/Modal';
import { validateProject } from "@/service/validate-project";
import { notify } from "@/utils/notify";
import { useRouter } from 'next/router';
import React, { useEffect, useState } from 'react';
import CancelButton from '../common/CancelButton';

interface ProjectStatusProps {
    status: string;
    projectId: string;
}

const ProjectStatus: React.FC<ProjectStatusProps> = ({ status, projectId }) => {
    const router = useRouter();
    const [showModal, setShowModal] = useState(false);
    const [isProjectValid, setIsProjectValid] = useState<boolean>(true);
    const [validationErrorMessage, setValidationErrorMessage] = useState<string>("");
    const [isValidating, setIsValidating] = useState<boolean>(false);

    useEffect(() => {
        // Validate project when component mounts
        if (status.toLowerCase() === 'en proceso') {
            console.log("ProjectStatus - Project id ", projectId);
            validateProjectStatus(projectId);
        }
    }, [projectId]);

    const getValidationMessages = (validationResult: any): string[] => {
        const messages: string[] = [];
        messages.push("El proyecto no cumple con todos los requisitos necesarios para el cálculo:");
        console.log(validationResult)
        if (validationResult?.additional_validations?.climate_file?.valid === false) {
            const climateError = validationResult.additional_validations.climate_file.info?.error || "El archivo climático no es válido o falta.";
            messages.push(`- ${climateError}`);
        }
        const enclosureNames: any = validationResult?.enclosures || {};
        if (validationResult?.failed_enclosures && validationResult?.failed_enclosures?.length > 0) {
            validationResult?.failed_enclosures.forEach((enclosure: any) => {
                const recintoErrores: string[] = [];
                if (enclosure.requirements) {
                    if (enclosure.walls < 3) recintoErrores.push(enclosure.requirements.walls);
                    if (enclosure.windows < 1) recintoErrores.push(enclosure.requirements.windows);
                    if (enclosure.floors < 1) recintoErrores.push(enclosure.requirements.floors);
                }
                // Buscar nombre del recinto por id si no viene en el objeto enclosure
                let nombreRecinto = enclosure.name;
                if (!nombreRecinto && enclosure.enclosure_id && enclosureNames[enclosure.enclosure_id]) {
                    nombreRecinto = enclosureNames[enclosure.enclosure_id].name;
                }
                if (!nombreRecinto) nombreRecinto = 'Sin nombre';
                if (recintoErrores.length > 0) {
                    messages.push(`Recinto "${nombreRecinto}": ${recintoErrores.join(', ')}`);
                }
            });
        }
        return messages;
    };

    const validateProjectStatus = async (projectId:string) => {
        try {
            console.log("Validations",projectId)
            setIsValidating(true);
            const validationResult = await validateProject(projectId, true);
            setIsProjectValid(validationResult?.valid || false);
            if (!validationResult?.valid) {
                const messages = getValidationMessages(validationResult);
                setValidationErrorMessage(messages.join('\n'));
            }
        } catch (error) {
            console.error("Error validating project:", error);
            setIsProjectValid(false);
            setValidationErrorMessage("Error al validar el proyecto. Inténtelo nuevamente.");
        } finally {
            setIsValidating(false);
        }
    };

    const getStatusWithEmoji = (status: string) => {
        const lowerStatus = status.toLowerCase();
        if (lowerStatus === 'en proceso') return '🔄';
        if (lowerStatus === 'finalizado') return '✅';
        if (lowerStatus === 'registrado') return '📝';
        return '';
    };
    const handleCalculateResults = async () => {
        setIsValidating(true);
        try {
            if (!projectId) return
            const validationResult = await validateProject(projectId, true);
            setIsProjectValid(validationResult?.valid || false);

            if (!validationResult?.valid) {
                const messages = getValidationMessages(validationResult);
                setValidationErrorMessage(messages.join('\n'));
                messages.forEach((msg, idx) => {
                    notify(msg, "error", 9000 + idx * 2000);
                });
                return;
            }
            // Si es válido, mostrar el modal
            setShowModal(true);
        } catch (error) {
            setIsProjectValid(false);
            setValidationErrorMessage("Error al validar el proyecto. Inténtelo nuevamente.");
            notify("Error al validar el proyecto. Inténtelo nuevamente.", "error", 9000);
        } finally {
            setIsValidating(false);
        }
    };

    const handleConfirm = () => {
        setShowModal(false);
        router.push(`/calculation-result2?id=${projectId}`);
    };

    const handleCancel = () => {
        setShowModal(false);
    };

    return (
        <>
            <Card>
                <div className="d-flex justify-content-between align-items-center w-100">
                    <div className="d-flex align-items-center gap-2 mx-0">
                        Estado: <span><strong>{getStatusWithEmoji(status)} {status.toUpperCase()}</strong></span>
                    </div>
                    {status.toLowerCase() === 'en proceso' && (<div className={!isProjectValid ? "disabled-button-wrapper" : ""}>
                        <CustomButton
                            onClick={handleCalculateResults}
                            disabled={isValidating}
                            className={isValidating ? "btn-gray" : "btn-orange"}
                        >
                            <span className="material-icons">calculate</span>
                            {isValidating ? "Validando..." : "Calcular resultados"}
                        </CustomButton>
                    </div>
                    )}
                </div>
            </Card>
            <Modal
                isOpen={showModal}
                onClose={handleCancel}
                title="Confirmación"
            >
                <p>Para realizar el cálculo, asegúrese de que todos los datos del proyecto estén correctamente llenos.</p>
                <div className="modal-actions d-flex justify-content-between gap-2 mt-3">
                    <CancelButton onClick={handleCancel} />
                    <CustomButton onClick={handleConfirm} className="btn btn-primary">Realizar cálculo</CustomButton>
                </div>
            </Modal>
        </>
    );
};

export default ProjectStatus;