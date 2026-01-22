import React from 'react';
import { Table } from 'react-bootstrap';
import { Recinto } from '../../../types/recinto';

interface RecintoListTableProps {
    recintos: Recinto[];
}

/**
 * Component for displaying the list of recintos
 */
const RecintoListTable: React.FC<RecintoListTableProps> = ({ recintos }) => {
    return (
        <Table className="tables-recints">
            <thead style={{ height: "100px" }}>
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
                </tr>
            </thead>
            <tbody>
                {recintos.map((recinto, index) => (
                    <tr key={`recinto-${recinto.id || index}`}>
                        <td>{recinto.name_enclosure || `Recinto ${index + 1}`}</td>
                        <td>{recinto.perfil_uso || 'N/A'}</td>
                        <td className="text-end">{recinto.superficie?.toFixed(2) || '0.00'}</td>
                    </tr>
                ))}
            </tbody>
        </Table>
    );
};

export default RecintoListTable;
