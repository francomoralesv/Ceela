import { Cloud, Droplet, Flame, Snowflake } from "lucide-react";

// Interface for final indicators from API
interface FinalIndicators {
  co2_eq_total: number;
  co2_eq_vs_caso_base: number;
  consumo_calef_vs: number;
  consumo_calefaccion_final: number;
  consumo_calefaccion_final2: number;
  consumo_iluminacion_final: number;
  consumo_iluminacion_final2: number;
  consumo_iluminacion_vs: number;
  consumo_ref_vs: number;
  consumo_refrigeracion_final: number;
  consumo_refrigeracion_final2: number;
  consumo_vs_caso_base: number;
  demanda_calef_vs: number;
  demanda_calefaccion_final: number;
  demanda_calefaccion_final2: number;
  demanda_iluminacion_final: number;
  demanda_iluminacion_final2: number;
  demanda_iluminacion_vs: number;
  demanda_ref_final: number;
  demanda_ref_final2: number;
  demanda_ref_vs: number;
  disconfort_calef: number;
  disconfort_ref: number;
  disconfort_total: number;
  disconfort_vs: number;
}

// Default data in case no indicators are provided
const defaultIndicators: FinalIndicators = {
  co2_eq_total: 0,
  co2_eq_vs_caso_base: 0,
  consumo_calef_vs: 0,
  consumo_calefaccion_final: 0,
  consumo_calefaccion_final2: 0,
  consumo_iluminacion_final: 0,
  consumo_iluminacion_final2: 0,
  consumo_iluminacion_vs: 0,
  consumo_ref_vs: 0,
  consumo_refrigeracion_final: 0,
  consumo_refrigeracion_final2: 0,
  consumo_vs_caso_base: 0,
  demanda_calef_vs: 0,
  demanda_calefaccion_final: 0,
  demanda_calefaccion_final2: 0,
  demanda_iluminacion_final: 0,
  demanda_iluminacion_final2: 0,
  demanda_iluminacion_vs: 0,
  demanda_ref_final: 0,
  demanda_ref_final2: 0,
  demanda_ref_vs: 0,
  disconfort_calef: 0,
  disconfort_ref: 0,
  disconfort_total: 0,
  disconfort_vs: 0
};

export default function IndicadoresFinales({ finalIndicators }: { finalIndicators?: FinalIndicators }) {
  // Use provided data or default values
  const data = finalIndicators || defaultIndicators;

  // Format a percentage value for display
  const formatPercent = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  return (
    <div className="container my-4">
      <div className="row">
        {/* Sección Demanda */}
        <div className="col-12 col-md-6 mb-4">
          <div className="card">
            <div className="card-header">
              <Flame className="me-2" />
              <strong>Demanda</strong>
            </div>
            <div className="card-body p-2">
              <table className="table table-sm mb-0">
                <thead>
                  <tr>
                    <th className="text-center" rowSpan={2}>Concepto</th>
                    <th colSpan={3} className="text-center">Demanda</th>
                  </tr>
                  <tr className="text-center">
                    <th>[kWh/m2-año]</th>
                    <th>[kWh-año]</th>
                    <th>
                      % Versus caso base
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Calefacción</td>
                    <td className="text-center">{data.demanda_calefaccion_final?.toFixed(1)}</td>
                    <td className="text-center">{data.demanda_calefaccion_final2?.toFixed(1)}</td>
                    <td className="text-center">
                      <span className="text-center">{formatPercent(data.demanda_calef_vs ?? 0)}</span>
                    </td>
                  </tr>
                  <tr>
                    <td>Refrigeración</td>
                    <td className="text-center">{data.demanda_ref_final?.toFixed(1)}</td>
                    <td className="text-center">{data.demanda_ref_final2?.toFixed(1)}</td>
                    <td className="text-center">
                      <span className="text-center">{formatPercent(data.demanda_ref_vs ?? 0)}</span>
                    </td>
                  </tr>
                  <tr>
                    <td>Iluminación</td>
                    <td className="text-center">{data.demanda_iluminacion_final?.toFixed(1)}</td>
                    <td className="text-center">{data.demanda_iluminacion_final2?.toFixed(1)}</td>
                    <td className="text-center">
                      <span className="text-center">{formatPercent(data.demanda_iluminacion_vs ?? 0)}</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Sección Consumo Energía Primaria */}
        <div className="col-12 col-md-6 mb-4">
          <div className="card">
            <div className="card-header">
              <Droplet className="me-2" />
              <strong>Consumo Energía Primaria</strong>
            </div>
            <div className="card-body p-2">
              <table className="table table-sm mb-0">
                <thead>
                  <tr>
                    <th className="text-center" rowSpan={2}>Concepto</th>
                    <th colSpan={3} className="text-center">Consumo Energía Primaria</th>
                  </tr>
                  <tr className="text-center">
                    <th>[kWh/m2-año]</th>
                    <th>[kWh-año]</th>
                    <th>% Versus caso base</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Calefacción</td>
                    <td className="text-center">{data.consumo_calefaccion_final?.toFixed(1)}</td>
                    <td className="text-center">{data.consumo_calefaccion_final2?.toFixed(1)}</td>
                    <td className="text-center">
                      {formatPercent(data.consumo_calef_vs ?? 0)}
                    </td>
                  </tr>
                  <tr>
                    <td>Refrigeración</td>
                    <td className="text-center">{data.consumo_refrigeracion_final?.toFixed(1)}</td>
                    <td className="text-center">{data.consumo_refrigeracion_final2?.toFixed(1)}</td>
                    <td className="text-center">
                      {formatPercent(data.consumo_ref_vs ?? 0)}
                    </td>
                  </tr>
                  <tr>
                    <td>Iluminación</td>
                    <td className="text-center">{data.consumo_iluminacion_final?.toFixed(1)}</td>
                    <td className="text-center">{data.consumo_iluminacion_final2?.toFixed(1)}</td>
                    <td className="text-center">{formatPercent(data.consumo_iluminacion_vs ?? 0)}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Sección Hrs Disconfort */}
        <div className="col-12 col-md-6 mb-4">
          <div className="card">
            <div className="card-header">
              <Snowflake className="me-2" />
              <strong>Hrs Disconfort T° libre</strong>
            </div>
            <div className="card-body p-2">
              <table className="table table-sm mb-0">
                <thead>
                  <tr>
                    <th>Total</th>
                    <th className="text-end">{data.disconfort_total?.toFixed(1)} hrs/año</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Comparación caso base</td>
                    <td colSpan={2} className="text-center">{formatPercent(data.disconfort_vs ?? 0)}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Sección CO2_eq */}
        <div className="col-12 col-md-6 mb-4">
          <div className="card">
            <div className="card-header">
              <Cloud className="me-2" />
              <strong>CO₂_eq</strong>
            </div>
            <div className="card-body p-2">
              <table className="table table-sm mb-0">
                <thead>
                  <tr>
                    <th>Total</th>
                    <th className="text-end">{data.co2_eq_total?.toFixed(1)} kg CO₂eq/año</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Comparación caso base</td>
                    <td colSpan={2} className="text-center">{formatPercent(data.co2_eq_vs_caso_base ?? 0)}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
