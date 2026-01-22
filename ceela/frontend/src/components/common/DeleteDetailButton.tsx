import React, { useState } from 'react';
import axios from 'axios';
import { notify } from '@/utils/notify';
import { constantUrlApiEndpoint } from '@/utils/constant-url-endpoint';
import ModalCreate from './ModalCreate';
import CustomButton from './CustomButton'; // Importamos el componente CustomButton

interface DeleteDetailButtonProps {
  detailId: number;
  onDelete?: () => void;
  disabled?: boolean;  // Add this line
}

const DeleteDetailButton: React.FC<DeleteDetailButtonProps> = ({ detailId, onDelete, disabled }) => {
  const [showConfirmModal, setShowConfirmModal] = useState(false);

  const handleDelete = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        notify('Token no encontrado', 'Inicia sesión.');
        return;
      }

      const response = await axios.delete(
        `${constantUrlApiEndpoint}/detail-general/${detailId}/false`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      if (response.data.deleted) {
        notify('Detalle eliminado exitosamente');
        if (onDelete) {
          onDelete();
        }
      }
    } catch (error) {
      console.error('Error al eliminar el detalle:', error);
      notify('Error al eliminar el detalle');
    } finally {
      setShowConfirmModal(false);
    }
  };

  return (
    <>
      {/* Botón principal que dispara el modal de confirmación */}
      <CustomButton
        onClick={() => setShowConfirmModal(true)}
        variant="deleteIcon"                      // Usamos el color rojo (ya definido en CustomButton)
        type="button"
        className="material-icons"                // Puedes mantener o ajustar la clase según necesites
        disabled={disabled}  // Add this line
      >
        Eliminar
      </CustomButton>

      <ModalCreate
        isOpen={showConfirmModal}
        saveLabel="Confirmar"
        onClose={() => setShowConfirmModal(false)}
        onSave={handleDelete}
        title="Confirmar eliminación"
        modalStyle={{ maxWidth: "500px", width: "500px", padding: "24px" }}
      >
        <div className="text-center mb-4">
          <p>¿Está seguro que desea eliminar este detalle?</p>
          <div className="d-flex justify-content-center gap-2">
          </div>
        </div>
      </ModalCreate>
    </>
  );
};

export default DeleteDetailButton;
