import React, { useEffect } from 'react';
import { Table } from 'react-bootstrap';
import { SystemOption } from '../../../types/energySystem';
import { Recinto } from '../../../types/recinto';

interface CasoBaseTableProps {
    recintos: Recinto[];
    combustibleCalef?: SystemOption | null;
    consumosEnergia?: SystemOption[];
    onUpdate?: (recintos: Recinto[]) => void;
}

/**
 * Component for displaying base case data
 */
const CasoBaseTable: React.FC<CasoBaseTableProps> = ({
    recintos,
    combustibleCalef,
    consumosEnergia,
    onUpdate,
}) => {
    const calculateConsumoCalef = (demandaCalef: number | undefined): number => {
        if (!demandaCalef || !combustibleCalef || typeof combustibleCalef.fep !== 'number') {
            return 0;
        }
        const result = (demandaCalef * combustibleCalef.fep) / 1;
        return result;
    };
    const calculateConsumoRef = (demandaRef: number | undefined): number => {
        if (!demandaRef || !combustibleCalef || typeof combustibleCalef.fep !== 'number') {
            return 0;
        }
        const result = (demandaRef * combustibleCalef.fep) / 1;
        return result;
    };

    const getConsumoEnergia = (code: string): number => {
        return consumosEnergia?.find(c => c.code === code)?.co2_eq || 0;
    };
    const calculateCO2eqTotal = (
        recinto: Recinto,
        consumoCalef: number,
        consumoRef: number,
        demandaIlum: number = 31.3 // TODO: Verify if this fixed value for illumination is correct for all cases
    ): number => {

        const fep = combustibleCalef?.fep || 1;
        const consumoElectricidad = getConsumoEnergia(combustibleCalef?.code || '');
        if(recinto.superficie)
        return (consumoCalef * fep * recinto.superficie) +
            (consumoRef * fep * recinto.superficie) +
            (demandaIlum * recinto.superficie * consumoElectricidad * fep);
        return 0
    };

    useEffect(() => {
        // Actualizar todos los recintos y enviarlos juntos
        const updatedRecintos = recintos.map(recinto => {
            const demandaCalef = recinto.demanda_calef || 0;
            const demandaRef = recinto.demanda_ref || 0;
            const demandaIlum = recinto.demanda_ilum || 0;

            const baseConsumoCalef = calculateConsumoCalef(demandaCalef);
            const baseConsumoRef = calculateConsumoRef(demandaRef);
            const baseConsumoTotal = baseConsumoCalef + baseConsumoRef;

            const co2eqTotal = calculateCO2eqTotal(recinto, baseConsumoCalef, baseConsumoRef, demandaIlum);

            return {
                ...recinto,
                base_demanda_calef: demandaCalef,
                base_demanda_ref: demandaRef,
                base_demanda_ilum: demandaIlum,
                base_demanda_total: demandaCalef + demandaRef,
                base_consumo_calef: baseConsumoCalef,
                base_consumo_ref: baseConsumoRef,
                base_consumo_total: baseConsumoTotal,
                base_co2eq_total: co2eqTotal,
            };
        });

        if (onUpdate) {
            onUpdate(updatedRecintos);
        }
    }, [recintos, combustibleCalef, consumosEnergia]);

    return (
        <Table className="tables-results">
            <thead>
                <tr>
                    <th>Nombre del Recinto</th>
                    <th className="text-center">Demanda Calef.</th>
                    <th className="text-center">Demanda Ref.</th>
                    <th className="text-center">Demanda Total</th>
                    <th className="text-center">Consumo Base Calef.</th>
                    <th className="text-center">Consumo Base Ref.</th>
                    <th className="text-center">Consumo Base Total</th>
                    <th className="text-center">CO2eq Total</th>
                </tr>
            </thead>
            <tbody>
                {recintos.map((recinto, index) => {
                    // Caso base: usar los campos directos si existen, si no calcular como antes
                    const demandaCalef = recinto.caso_base_demanda_calefaccion ?? recinto.demanda_calef ?? 0;
                    const demandaRef = recinto.caso_base_demanda_refrigeracion ?? recinto.demanda_ref ?? 0;
                    const demandaIlum = recinto.caso_base_demanda_iluminacion ?? recinto.demanda_ilum ?? 0;
                    const demandaTotal = recinto.caso_base_demanda_total ?? (demandaCalef + demandaRef + demandaIlum);
                    const baseConsumoCalef = recinto.caso_base_consumo_calefaccion ?? calculateConsumoCalef(demandaCalef);
                    const baseConsumoRef = recinto.caso_base_consumo_refrigeracion ?? calculateConsumoRef(demandaRef);
                    const baseConsumoTotal = recinto.caso_base_consumo_total ?? (baseConsumoCalef + baseConsumoRef);
                    const co2eqTotal = recinto.caso_base_co2_eq_total ?? calculateCO2eqTotal(recinto, baseConsumoCalef, baseConsumoRef, demandaIlum);

                    return (
                        <tr key={`casobase-${recinto.enclosure_id || recinto.id || index}`}>
                            <td>{recinto.nombre_recinto || recinto.name_enclosure || `Recinto ${index + 1}`}</td>
                            <td className="text-center">{demandaCalef?.toFixed(2)}</td>
                            <td className="text-center">{demandaRef?.toFixed(2)}</td>
                            <td className="text-center">{demandaTotal?.toFixed(2)}</td>
                            <td className="text-center">{baseConsumoCalef?.toFixed(2)}</td>
                            <td className="text-center">{baseConsumoRef?.toFixed(2)}</td>
                            <td className="text-center">{baseConsumoTotal?.toFixed(2)}</td>
                            <td className="text-center">{co2eqTotal?.toFixed(2)}</td>
                        </tr>
                    );
                })}
            </tbody>
        </Table>
    );
};

export default CasoBaseTable;
