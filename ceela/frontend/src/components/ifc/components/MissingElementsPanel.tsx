import React from 'react';
import { Col, Row } from 'react-bootstrap';

interface MissingElement {
    type: string;
    name: string;
}

interface MissingElementsPanelProps {
    elements: MissingElement[];
    onClose?: () => void;
}

export const MissingElementsPanel: React.FC<MissingElementsPanelProps> = ({ elements, onClose }) => {
    // Agrupar elementos por tipo
    const groupedElements = elements.reduce((groups, element) => {
        const type = element.type;
        if (!groups[type]) {
            groups[type] = [];
        }
        groups[type].push(element);
        return groups;
    }, {} as Record<string, MissingElement[]>);

    // Si no hay elementos faltantes, no renderizamos nada
    if (elements.length === 0) {
        return null;
    }

    return (
        <Row className="mt-3">
            <Col>
                <div className="card border-warning">
                    <div className="card-header bg-warning text-dark d-flex justify-content-between align-items-center">
                        <h6 className="card-title mb-0">
                            <i className="fas fa-exclamation-triangle me-2"></i>
                            Elementos Faltantes
                        </h6>
                        {onClose && (
                            <button type="button" className="btn-close" onClick={onClose} aria-label="Close"></button>
                        )}
                    </div>
                    <div className="card-body">
                        <p className="text-muted mb-3">
                            Los siguientes elementos no pudieron ser procesados debido a materiales o referencias faltantes:
                        </p>

                        {Object.entries(groupedElements).map(([type, elements]) => (
                            <div key={type} className="mb-3">
                                <h6 className="border-bottom pb-2">{type}s</h6>
                                <ul className="list-group">
                                    {elements.map((element, index) => (
                                        <li key={index} className="list-group-item d-flex justify-content-between align-items-center">
                                            <span>{element.name}</span>
                                            <span className="badge bg-warning text-dark">{element.type}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        ))}

                        <div className="alert alert-info mt-3">
                            <small>
                                <i className="fas fa-info-circle me-2"></i>
                                Revise los materiales asignados a estos elementos y asegúrese de que estén correctamente definidos en el modelo IFC.
                            </small>
                        </div>
                    </div>
                </div>
            </Col>
        </Row>
    );
};
