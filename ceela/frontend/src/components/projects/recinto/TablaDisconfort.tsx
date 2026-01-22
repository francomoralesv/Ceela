import React from 'react';
import { Table } from 'react-bootstrap';
import { Recinto } from '../../../types/recinto';

interface TablaDisconfortProps {
    recintos: Recinto[];
}

/**
 * Component for displaying discomfort hours data
 */
const   TablaDisconfort: React.FC<TablaDisconfortProps> = ({ recintos }) => {


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
                    <th className="text-center">Total</th>
                </tr>
            </thead>
            <tbody>
                {recintos.map((recinto, index) => (
                    <tr key={`disconfort-${recinto.enclosure_id || recinto.id || index}`}>
                        <td>{recinto.nombre_recinto || recinto.name_enclosure || `Recinto ${index + 1}`}</td>
                        <td>{recinto.perfil_uso || 'N/A'}</td>
                        <td className="text-end">{recinto.superficie?.toFixed(2) || '0.00'}</td>
                        <td className="text-end">
                            {recinto.hrs_disconfort_calefaccion?.toFixed(2) || recinto.hrs_disconfort_calef?.toFixed(2) || '0.00'}
                            <br />
                            <small className="text-muted">CB: {recinto.caso_base_hrs_disconfort_calefaccion !== undefined ? Number(recinto.caso_base_hrs_disconfort_calefaccion).toFixed(2) : '-'}</small>
                        </td>
                        <td className="text-end">
                            {recinto.hrs_disconfort_refrigeracion?.toFixed(2) || recinto.hrs_disconfort_ref?.toFixed(2) || '0.00'}
                            <br />
                            <small className="text-muted">CB: {recinto.caso_base_hrs_disconfort_refrigeracion !== undefined ? Number(recinto.caso_base_hrs_disconfort_refrigeracion).toFixed(2) : '-'}</small>
                        </td>
                        <td className="text-end">
                            {recinto.hrs_disconfort_total?.toFixed(2) || '0.00'}
                            <br />
                            <small className="text-muted">CB: {recinto.caso_base_hrs_disconfort_total !== undefined ? Number(recinto.caso_base_hrs_disconfort_total).toFixed(2) : '-'}</small>
                        </td>
                    </tr>
                ))}
            </tbody>
        </Table>
    );
};

export default TablaDisconfort;
