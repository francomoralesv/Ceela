import { useState } from "react";
import Image from "next/image";
import Card from "../common/Card";
import Modal from "../common/Modal";

interface DetailedUser {
    id: number;
    name: string;
    email: string;
    last_name: string;
    created_at: string;
    status: boolean;
    project_count: number;
    project_ids: number[];
    profession?: string;
}

interface DetailedUsersReportProps {
    loading: boolean;
    data: DetailedUser[] | null;
}

export const DetailedUsersReport = ({ loading, data }: DetailedUsersReportProps) => {
    const [selectedUser, setSelectedUser] = useState<DetailedUser | null>(null);
    const [showModal, setShowModal] = useState(false);

    if (loading) {
        return (
            <Card className="chart-card p-4 text-center h-100">
                <h5>Usuarios con más proyectos registrados</h5>
                <div className="spinner-border primary-db" role="status">
                    <span className="visually-hidden">Cargando...</span>
                </div>
            </Card>
        );
    }

    const handleViewProjects = (user: DetailedUser) => {
        setSelectedUser(user);
        setShowModal(true);
    };

    return (
        <Card>
            <h5 className="mb-4 mt-4">Usuarios con más proyectos registrados</h5>
            <div className="table-responsive" style={{ maxHeight: '300px', overflowY: 'auto' }}>
                <table className="table table-hover">
                    <thead>
                        <tr>
                            <th>Usuario</th>
                            <th>Correo</th>
                            <th>Fecha de registro</th>
                            <th>Estado</th>
                            <th>N° Proyectos</th>
                        </tr>
                    </thead>
                    <tbody>
                        {data?.map((user) => (
                            <tr key={user.id} onClick={() => user.project_count > 0 && handleViewProjects(user)}
                                style={{ cursor: user.project_count > 0 ? 'pointer' : 'default' }}>
                                <td><Image src="/assets/images/user_icon.png" alt="User icon" width={18} height={18} className="me-2" />{`${user.name} ${user.last_name}`}
                                    <div style={{ fontSize: "0.8rem" }}>
                                        {user.profession || "Profesión no disponible"}
                                    </div>
                                </td>
                                <td>{user.email}</td>
                                <td>{new Date(user.created_at).toLocaleDateString()}</td>
                                <td>
                                    <span className={`badge ${user.status ? 'bg-success' : 'bg-danger'}`}>
                                        {user.status ? 'Activo' : 'Inactivo'}
                                    </span>
                                </td>
                                <td>{user.project_count}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <Modal
                isOpen={showModal}
                onClose={() => setShowModal(false)}
                title={`Información de ${selectedUser?.name} ${selectedUser?.last_name}`}
            >
                <div className="p-3">
                    <div className="row">
                        <div className="col-md-6">
                            <h6>Nombre completo:</h6>
                            <p>{`${selectedUser?.name} ${selectedUser?.last_name}`}</p>
                            <h6>Email:</h6>
                            <p>{selectedUser?.email}</p>
                        </div>
                        <div className="col-md-6">
                            <h6>Fecha de creación:</h6>
                            <p>{new Date(selectedUser?.created_at || '').toLocaleDateString()}</p>
                            <h6>Estado:</h6>
                            <p><span className={`badge ${selectedUser?.status ? 'bg-success' : 'bg-danger'}`}>
                                {selectedUser?.status ? 'Activo' : 'Inactivo'}
                            </span></p>
                        </div>
                    </div>
                </div>
            </Modal>
            <style jsx>{`
                .primary-db {
                    background-color: var(--primary-color) !important;
                }
            `}</style>
        </Card>
    );
};
