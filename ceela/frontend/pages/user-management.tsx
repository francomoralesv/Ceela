import Checkbox from "@/components/common/Checkbox";
import CustomButton from "@/components/common/CustomButton";
import DataTable from "@/components/DataTable";
import { useApi } from "@/hooks/useApi";
import { notify } from "@/utils/notify";
import { useCallback, useEffect, useState } from "react";
import Breadcrumb from "../src/components/common/Breadcrumb";
import Card from "../src/components/common/Card";
import Title from "../src/components/Title";
import useAuth from "../src/hooks/useAuth";
import ModalCreate from "@/components/common/ModalCreate";

interface User {
  id: number;
  name: string;
  lastname: string;
  email: string;
  number_phone: string;
  birthdate: string;
  country: string;
  ubigeo: string;
  role_id: number;
  active: boolean;
  last_activity?: Date;
}

const UserManagement = () => {
  useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [userToDelete, setUserToDelete] = useState<User | null>(null);
  const { put, get, del } = useApi();

  const fetchUsers = useCallback(async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      console.error("[fetchUsers] No se encontró un token en localStorage.");
      return;
    }
    try {
      const params = new URLSearchParams();
      params.append("limit", "500");
      const url = `/users/?${params.toString()}`;
      const response = await get(url);
      const usersArray = (response?.users || []).map((user: User) => ({
        ...user,
        fullname: `${user.name} ${user.lastname}`,
      }));
      setUsers(usersArray);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Error desconocido";
      console.error("[fetchUsers] Error:", message);
    }
  }, [get]);

  useEffect(() => {
    fetchUsers();
  }, []);

  const getRoleText = (role_id: number) => {
    return role_id === 1 ? "Administrador" : role_id === 2 ? "Desarrollador" : "Desconocido";
  };

  const handleRoleChange = async (userId: number, newRoleId: number) => {
    try {
      const response = await put(`/user/${userId}/update`, { role_id: newRoleId });
      if (response) {
        notify(`Usuario actualizado al rol de ${getRoleText(newRoleId)}`, "success");
        fetchUsers();
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Error desconocido";
      notify(message);
    }
  };

  const handleActiveChange = async (userId: number, roleId: number, isActive: boolean) => {
    if (roleId === 1) {
      notify(
        "Acción no permitida, No se puede modificar el estado de un administrador"
      );
      return;
    }
    try {
      const response = await put(`/user/${userId}/update-status`, { active: isActive });
      if (response) {
        fetchUsers();
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Error desconocido";
      console.error("[handleActiveChange] Error:", message);
      notify("Error");
    }
  };

  const handleDeleteClick = (user: User) => {
    setUserToDelete(user);
    setShowDeleteModal(true);
  };

  const handleConfirmDelete = async () => {
    if (!userToDelete) return;
    try {
      await del(`/user/${userToDelete.id}/force-delete`);
      notify("Usuario y proyectos eliminados correctamente", "success");
      fetchUsers();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Error desconocido";
      notify(message);
    } finally {
      setShowDeleteModal(false);
      setUserToDelete(null);
    }
  };

  const handleCancelDelete = () => {
    setShowDeleteModal(false);
    setUserToDelete(null);
  };

  const columns = [
    { id: "id", label: "ID", minWidth: "2em" },
    {
      id: "activity",
      label: "Actividad",
      sortable: true,
      minWidth: "2em",
      cell: ({ row }: { row: User }) => {

        const lastActivity = row.last_activity ? new Date(row.last_activity) : null;
        console.log(lastActivity)
        const now = new Date();
        const isActive = lastActivity &&
          (now.getTime() - lastActivity.getTime()) <= 3 * 60 * 1000; 
        
        return (
          <div className="d-flex align-items-center">
            <div className="position-relative" title={isActive ? 'Usuario en línea' : 'Usuario desconectado'}>
              <span 
                className={`d-inline-block rounded-circle ${
                  isActive ? 'bg-success' : 'bg-secondary'
                }`}
                style={{ 
                  position: 'relative',
                  width: '8px',
                  height: '8px',
                  top: 0,
                  left: 0,
                  ...(isActive && {
                    animation: 'pulse 1.5s infinite',
                    boxShadow: '0 0 0 0 rgba(25, 135, 84, 1)'
                  })
                }}
              ></span>
              {isActive && (
                <span 
                  className="position-absolute rounded-circle bg-success opacity-75"
                  style={{
                  }}
                ></span>
              )}
            </div>
            <style jsx>{`
              @keyframes pulse {
                0% {
                  transform: scale(0.95);
                  box-shadow: 0 0 0 0 rgba(25, 135, 84, 0.7);
                }
                
                70% {
                  transform: scale(1);
                  box-shadow: 0 0 0 10px rgba(25, 135, 84, 0);
                }
                
                100% {
                  transform: scale(0.95);
                  box-shadow: 0 0 0 0 rgba(25, 135, 84, 0);
                }
              }
            `}</style>
          </div>
        );
      }
    },
    {
      id: "fullname",
      label: "Nombre de usuario",
      minWidth: "2em",
      sortable: true,
      cell: ({ row }: { row: User }) => `${row.name} ${row.lastname}`
    },
    { id: "email", label: "Correo Electrónico", minWidth: "2em" },
    {
      id: "birthdate",
      label: "Fecha de Nacimiento",
      minWidth: "2em",
      format: (value: string) =>
        value ? new Date(value).toLocaleDateString("es-ES") : "No disponible"
    },
    {
      id: "ubigeo",
      label: "Codigo Postal",
      minWidth: "2em",
      format: (value: string) => value || "No disponible"
    },
    {
      id: "direccion",
      label: "Dirección",
      minWidth: "2em",
      format: (value: string) => value || "No disponible"
    },
    {
      id: "role_id",
      label: "Rol",
      minWidth: "2em",
      cell: ({ row }: { row: User }) => (
        <select
          value={row.role_id}
          onChange={(e) => handleRoleChange(row.id, parseInt(e.target.value))}
          className="w-full px-4 py-2 text-sm text-muted border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 ease-in-out hover:border-blue-400"
        >
          <option value={1} className="py-2 text-muted">
            Administrador
          </option>
          <option value={2} className="py-2 text-muted">
            Desarrollador
          </option>
        </select>
      )
    },
    {
      id: "active",
      label: "Estado",
      minWidth: "2em",
      cell: ({ row }: { row: User }) => (
        <Checkbox
          checked={row.active}
          onChange={() => handleActiveChange(row.id, row.role_id, !row.active)}
          label={""}
          tooltip="Modificar el estado del usuario"
        />
      )
    },
    {
      id: "actions",
      label: "Acciones",
      minWidth: "2em",
      cell: ({ row }: { row: User }) => (
        <div className="flex gap-2">
          <CustomButton
            variant="deleteIcon"
            aria-label="Borrar usuario"
            title="Borrar usuario"
            onClick={() => handleDeleteClick(row)}
            style={{ padding: '0.5em', borderRadius: '6px' }}
          />
        </div>
      )
    }
  ];

  return (
    <>
      <Card>
        <div className="d-flex align-items-center w-100">
          <Title text="Listado de usuarios" />
          <Breadcrumb items={[
            { title: 'Dashboard', href: '/dashboard', active: false },
            { title: 'Gestión de usuarios', href: '/user-management' }
          ]} />
        </div>
      </Card>
      <DataTable
        columns={columns.map((col) => ({
          ...col,
          minWidth: parseInt(col.minWidth) || undefined
        }))}
        data={users}
        pageSize={10}
        enableSorting
        enableFiltering
        enableColumnVisibility
        showButton={true}
        createUrl="/user-create"
      />
      <ModalCreate
        isOpen={showDeleteModal}
        onClose={handleCancelDelete}
        onSave={handleConfirmDelete}
        saveLabel="Borrar"
        title="Confirmar Eliminación"
      >
        <div className="container">
          <div className="row mb-3">
            <p>
              ¿Está seguro que desea eliminar el usuario <strong>{userToDelete?.name} {userToDelete?.lastname}</strong>?
              <br />Esta acción eliminará el usuario y sus proyectos.
            </p>
          </div>
        </div>
      </ModalCreate>
    </>
  );
};

export default UserManagement;
