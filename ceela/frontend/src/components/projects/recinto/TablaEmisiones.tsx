import React, { useEffect } from 'react';
import { Table } from 'react-bootstrap';
import { SystemOption } from '../../../types/energySystem';
import { Recinto } from '../../../types/recinto';

interface TablaEmisionesProps {
    recintos: Recinto[];
    combustibleCalef: SystemOption | null;
    consumosEnergia: SystemOption[];
    onUpdate?: (recintos: Recinto[]) => void;
}

/**
 * Component for displaying CO2 emissions data
 */
const TablaEmisiones: React.FC<TablaEmisionesProps> = ({ recintos, combustibleCalef, consumosEnergia, onUpdate }) => {

    return (
        <Table className="tables-results">
            <thead>
                <tr>
                    <th className="text-center" colSpan={1} rowSpan={3}>
                        Recinto
                    </th>
                    <th className="text-center" colSpan={1} rowSpan={3}>
                        Perfil de uso
                    </th>
                    <th className="text-center" colSpan={1} rowSpan={3}>
                        Superficie (m²)
                    </th>
                    <th className="text-center">Calefacción</th>
                    <th className="text-center">Refrigeración</th>
                    <th className="text-center">Iluminación</th>
                    <th className="text-center">Total</th>
                </tr>
            </thead>
            <tbody>
                {recintos.map((recinto, index) => {
                    // Actual
                    const emisionesCalef = recinto.co2_eq_calefaccion ?? 0;
                    const emisionesRef = recinto.co2_eq_refrigeracion ?? 0;
                    const emisionesIlum = recinto.co2_eq_iluminacion ?? recinto.co2_eq_ilum ?? 0;
                    const emisionesTotal = recinto.co2_eq_total ?? (emisionesCalef + emisionesRef + emisionesIlum);

                    // Caso base
                    const cbEmisionesCalef = recinto.caso_base_co2_eq_calefaccion ?? '-';
                    const cbEmisionesRef = recinto.caso_base_co2_eq_refrigeracion ?? '-';
                    const cbEmisionesIlum = recinto.caso_base_co2_eq_iluminacion ?? '-';
                    const cbEmisionesTotal = recinto.caso_base_co2_eq_total ?? '-';

                    return (
                        <tr key={`emisiones-${recinto.enclosure_id || recinto.id || index}`}>
                            <td>{recinto.nombre_recinto || recinto.name_enclosure || `Recinto ${index + 1}`}</td>
                            <td>{recinto.perfil_uso || 'N/A'}</td>
                            <td className="text-center">{recinto.superficie?.toFixed(2) || '0.00'}</td>
                            <td className="text-center">
                                {emisionesCalef?.toFixed(2)}
                                <br />
                                <small className="text-muted">CB: {cbEmisionesCalef !== '-' ? Number(cbEmisionesCalef).toFixed(2) : '-'}</small>
                            </td>
                            <td className="text-center">
                                {emisionesRef?.toFixed(2)}
                                <br />
                                <small className="text-muted">CB: {cbEmisionesRef !== '-' ? Number(cbEmisionesRef).toFixed(2) : '-'}</small>
                            </td>
                            <td className="text-center">
                                {emisionesIlum?.toFixed(2)}
                                <br />
                                <small className="text-muted">CB: {cbEmisionesIlum !== '-' ? Number(cbEmisionesIlum).toFixed(2) : '-'}</small>
                            </td>
                            <td className="text-center">
                                {emisionesTotal?.toFixed(2)}
                                <br />
                                <small className="text-muted">CB: {cbEmisionesTotal !== '-' ? Number(cbEmisionesTotal).toFixed(2) : '-'}</small>
                            </td>
                        </tr>
                    );
                })}
            </tbody>
        </Table>
    );
};

export default TablaEmisiones;
