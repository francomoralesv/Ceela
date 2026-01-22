import React from 'react';
import { Col, Form, Row } from 'react-bootstrap';

export interface EnergySystemSelectorProps {
    recintoId: number;
    label: string;
    value: string | undefined;
    options: Array<{ code: string, description: string }>;
    onChange: (recintoId: number, value: string) => void;
    className?: string;
}

/**
 * Reusable selector component for energy systems
 */
const EnergySystemSelector: React.FC<EnergySystemSelectorProps> = ({
    recintoId,
    label,
    value,
    options,
    onChange,
    className = '',
}) => {
    return (
        <Row className={`align-items-center mb-2 ${className}`}>
            <Col xs={4} className="text-end">
                <label className="form-label mb-0">{label}:</label>
            </Col>
            <Col xs={8}>
                <Form.Select
                    size="sm"
                    value={value || ''}
                    onChange={(e) => onChange(recintoId, e.target.value)}
                >
                    <option value="">Seleccionar</option>
                    {options.map((option) => (
                        <option key={option.code} value={option.code}>
                            {option.description}
                        </option>
                    ))}
                </Form.Select>
            </Col>
        </Row>
    );
};

export default EnergySystemSelector;
