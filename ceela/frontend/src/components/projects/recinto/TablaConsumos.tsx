import React from 'react';
import { Table } from 'react-bootstrap';
import { SystemOption } from '../../../types/energySystem';
import { Recinto } from '../../../types/recinto';

interface TablaConsumosProps {
    combustibleCalef: any;
    config: {
        recintos: Recinto[];
        energySystems?: SystemOption[];
        rendimientoCalef?: any[];
        distribucionHvac?: any[];
        controlHvac?: any[];
        rendimientoRef?: any[];
        consumosEnergia?: any[];
    }
}

/**
 * Component for displaying consumption data
 */
const TablaConsumos: React.FC<TablaConsumosProps> = ({ config, combustibleCalef }) => {
    const { recintos } = config;

    return (
        <div>
            <Table className="tables-results">
                <thead>
                    <tr>
                        <th className="text-center" rowSpan={2}>Recinto</th>
                        <th className="text-center" rowSpan={2}>Perfil de Uso</th>
                        <th className="text-center" rowSpan={2}>Superficie (m²)</th>
                        <th className="text-center">Calefacción</th>
                        <th className="text-center">Refrigeración</th>
                        <th className="text-center">Total</th>
                    </tr>
                </thead>
                <tbody>
                    {recintos.map((recinto, index) => (
                        <tr key={`consumo-${recinto.enclosure_id || recinto.id || index}`}>
                            <td>{recinto.nombre_recinto || recinto.name_enclosure || `Recinto ${index + 1}`}</td>
                            <td>{recinto.perfil_uso || 'No definido'}</td>
                            <td className="text-center">{recinto.superficie?.toFixed(2) || '0.00'}</td>
                            <td className="text-center">
                                {recinto.consumo_calefaccion?.toFixed(2) || '0.00'}
                                <br />
                                <small className="text-muted">CB: {recinto.caso_base_consumo_calefaccion?.toFixed(2) ?? '-'}</small>
                            </td>
                            <td className="text-center">
                                {recinto.consumo_refrigeracion?.toFixed(2) || '0.00'}
                                <br />
                                <small className="text-muted">CB: {recinto.caso_base_consumo_refrigeracion?.toFixed(2) ?? '-'}</small>
                            </td>
                            <td className="text-center">
                                {recinto.consumo_total?.toFixed(2) || '0.00'}
                                <br />
                                <small className="text-muted">CB: {recinto.caso_base_consumo_total?.toFixed(2) ?? '-'}</small>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </Table>
        </div>
    );
};

export default TablaConsumos;
