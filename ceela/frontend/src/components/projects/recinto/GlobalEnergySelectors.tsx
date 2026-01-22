import React, { useEffect, useState } from 'react';
import { Card, Col, Form, Row } from 'react-bootstrap';

interface SystemOption {
    code: string;
    description: string;
}

interface GlobalEnergySelectorsProps {
    energySystems: SystemOption[];
    rendimientoCalef: SystemOption[];
    distribucionHvac: SystemOption[];
    controlHvac: SystemOption[];
    rendimientoRef: SystemOption[];
    onEnergySystemChange: (value: string) => void;
    onEnergySystemRefChange: (value: string) => void;
    onRendimientoCalefChange: (value: string) => void;
    onDistribucionHvacChange: (value: string) => void;
    onControlHvacChange: (value: string) => void;
    onRendimientoRefChange: (value: string) => void;
    onDistribucionHvacRefChange: (value: string) => void;
    onControlHvacRefChange: (value: string) => void;
    initialValues?: {
        combustibleCalef?: string;
        combustibleRef?: string;
        rendimientoCalef?: string;
        distribucionHvac?: string;
        controlHvac?: string;
        rendimientoRef?: string;
        distribucionHvacRef?: string;
        controlHvacRef?: string;
    };
}

/**
 * Global energy system selectors component that applies changes to all recintos
 */
const GlobalEnergySelectors: React.FC<GlobalEnergySelectorsProps> = ({
    energySystems,
    rendimientoCalef,
    distribucionHvac,
    controlHvac,
    rendimientoRef,
    onEnergySystemChange,
    onEnergySystemRefChange,
    onRendimientoCalefChange,
    onDistribucionHvacChange,
    onControlHvacChange,
    onRendimientoRefChange,
    onDistribucionHvacRefChange,
    onControlHvacRefChange,
    initialValues = {}
}) => {
    // Local states for the selectors
    const [combustibleCalef, setCombustibleCalef] = useState<string>(initialValues.combustibleCalef || '');
    const [combustibleRef, setCombustibleRef] = useState<string>(initialValues.combustibleRef || '');
    const [rendimiento, setRendimiento] = useState<string>(initialValues.rendimientoCalef || '');
    const [distribucion, setDistribucion] = useState<string>(initialValues.distribucionHvac || '');
    const [control, setControl] = useState<string>(initialValues.controlHvac || '');
    const [rendimientoR, setRendimientoR] = useState<string>(initialValues.rendimientoRef || '');
    const [distribucionRef, setDistribucionRef] = useState<string>(initialValues.distribucionHvacRef || '');
    const [controlRef, setControlRef] = useState<string>(initialValues.controlHvacRef || '');

    // Initialize selectors when initialValues change
    useEffect(() => {
        if (initialValues.combustibleCalef) setCombustibleCalef(initialValues.combustibleCalef);
        if (initialValues.combustibleRef) setCombustibleRef(initialValues.combustibleRef);
        if (initialValues.rendimientoCalef) setRendimiento(initialValues.rendimientoCalef);
        if (initialValues.distribucionHvac) setDistribucion(initialValues.distribucionHvac);
        if (initialValues.controlHvac) setControl(initialValues.controlHvac);
        if (initialValues.rendimientoRef) setRendimientoR(initialValues.rendimientoRef);
        if (initialValues.distribucionHvacRef) setDistribucionRef(initialValues.distribucionHvacRef);
        if (initialValues.controlHvacRef) setControlRef(initialValues.controlHvacRef);
    }, [initialValues]);

    // Event handlers
    const handleCombustibleCalefChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const value = e.target.value;
        setCombustibleCalef(value);
        onEnergySystemChange(value);
        console.log('Global energy system changed to:', value);
    };

    const handleCombustibleRefChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const value = e.target.value;
        setCombustibleRef(value);
        onEnergySystemRefChange(value);
        console.log('Global refrigeration system changed to:', value);
    };

    const handleRendimientoChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const value = e.target.value;
        setRendimiento(value);
        onRendimientoCalefChange(value);
        console.log('Global rendimiento calefacción changed to:', value);
    };

    const handleDistribucionChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const value = e.target.value;
        setDistribucion(value);
        onDistribucionHvacChange(value);
        console.log('Global distribución HVAC changed to:', value);
    };

    const handleControlChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const value = e.target.value;
        setControl(value);
        onControlHvacChange(value);
        console.log('Global control HVAC changed to:', value);
    };

    const handleRendimientoRefChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const value = e.target.value;
        setRendimientoR(value);
        onRendimientoRefChange(value);
        console.log('Global rendimiento refrigeración changed to:', value);
    };

    const handleDistribucionRefChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const value = e.target.value;
        setDistribucionRef(value);
        onDistribucionHvacRefChange(value);
        console.log('Global distribución HVAC refrigeración changed to:', value);
    };

    const handleControlRefChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const value = e.target.value;
        setControlRef(value);
        onControlHvacRefChange(value);
        console.log('Global control HVAC refrigeración changed to:', value);
    };

    return (
        <Card className="mb-4">
            <Card.Header>
                <h4 className="mb-0">Configuración Global de Sistemas Energéticos</h4>
            </Card.Header>
            <Card.Body>
                <Row>
                    {/* Calefacción */}
                    <Col md={6}>
                        <h5 className="mb-3">Calefacción</h5>

                        {/* Combustible Calefacción */}
                        <Form.Group className="mb-3">
                            <Form.Label>Combustible</Form.Label>
                            <Form.Select
                                value={combustibleCalef}
                                onChange={handleCombustibleCalefChange}
                            >
                                <option value="">Seleccionar combustible</option>
                                {energySystems.map((system) => (
                                    <option key={`calef-${system.code}`} value={system.code}>
                                        {system.description}
                                    </option>
                                ))}
                            </Form.Select>
                        </Form.Group>

                        {/* Rendimiento Calefacción */}
                        <Form.Group className="mb-3">
                            <Form.Label>Rendimiento</Form.Label>
                            <Form.Select
                                value={rendimiento}
                                onChange={handleRendimientoChange}
                            >
                                <option value="">Seleccionar rendimiento</option>
                                {rendimientoCalef.map((option) => (
                                    <option key={`rendCalef-${option.code}`} value={option.code}>
                                        {option.description}
                                    </option>
                                ))}
                            </Form.Select>
                        </Form.Group>

                        {/* Distribución HVAC */}
                        <Form.Group className="mb-3">
                            <Form.Label>Distribución HVAC</Form.Label>
                            <Form.Select
                                value={distribucion}
                                onChange={handleDistribucionChange}
                            >
                                <option value="">Seleccionar distribución</option>
                                {distribucionHvac.map((option) => (
                                    <option key={`distHvac-${option.code}`} value={option.code}>
                                        {option.description}
                                    </option>
                                ))}
                            </Form.Select>
                        </Form.Group>

                        {/* Control HVAC */}
                        <Form.Group className="mb-3">
                            <Form.Label>Control HVAC</Form.Label>
                            <Form.Select
                                value={control}
                                onChange={handleControlChange}
                            >
                                <option value="">Seleccionar control</option>
                                {controlHvac.map((option) => (
                                    <option key={`controlHvac-${option.code}`} value={option.code}>
                                        {option.description}
                                    </option>
                                ))}
                            </Form.Select>
                        </Form.Group>
                    </Col>

                    {/* Refrigeración */}
                    <Col md={6}>
                        <h5 className="mb-3">Refrigeración</h5>

                        {/* Combustible Refrigeración */}
                        <Form.Group className="mb-3">
                            <Form.Label>Combustible</Form.Label>
                            <Form.Select
                                value={combustibleRef}
                                onChange={handleCombustibleRefChange}
                            >
                                <option value="">Seleccionar combustible</option>
                                {energySystems.map((system) => (
                                    <option key={`ref-${system.code}`} value={system.code}>
                                        {system.description}
                                    </option>
                                ))}
                            </Form.Select>
                        </Form.Group>

                        {/* Rendimiento Refrigeración */}
                        <Form.Group className="mb-3">
                            <Form.Label>Rendimiento</Form.Label>
                            <Form.Select
                                value={rendimientoR}
                                onChange={handleRendimientoRefChange}
                            >
                                <option value="">Seleccionar rendimiento</option>
                                {rendimientoRef.map((option) => (
                                    <option key={`rendRef-${option.code}`} value={option.code}>
                                        {option.description}
                                    </option>
                                ))}
                            </Form.Select>
                        </Form.Group>

                        {/* Distribución HVAC Refrigeración */}
                        <Form.Group className="mb-3">
                            <Form.Label>Distribución HVAC</Form.Label>
                            <Form.Select
                                value={distribucionRef}
                                onChange={handleDistribucionRefChange}
                            >
                                <option value="">Seleccionar distribución</option>
                                {distribucionHvac.map((option) => (
                                    <option key={`distHvacRef-${option.code}`} value={option.code}>
                                        {option.description}
                                    </option>
                                ))}
                            </Form.Select>
                        </Form.Group>

                        {/* Control HVAC Refrigeración */}
                        <Form.Group className="mb-3">
                            <Form.Label>Control HVAC</Form.Label>
                            <Form.Select
                                value={controlRef}
                                onChange={handleControlRefChange}
                            >
                                <option value="">Seleccionar control</option>
                                {controlHvac.map((option) => (
                                    <option key={`controlHvacRef-${option.code}`} value={option.code}>
                                        {option.description}
                                    </option>
                                ))}
                            </Form.Select>
                        </Form.Group>
                    </Col>
                </Row>
            </Card.Body>
        </Card>
    );
};

export default GlobalEnergySelectors;
