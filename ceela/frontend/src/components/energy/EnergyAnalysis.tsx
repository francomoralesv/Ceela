import { Flame } from 'lucide-react';
import { useState, useMemo } from 'react';
import ChartComponent from '../chart/ChartComponent';

interface ChartDataItem {
    concepto: string;
    kwh_m2_ano: string | number;
    kwh_ano?: string | number;
    vsCasoBase?: string;
    nota?: string;
}

interface EnergyAnalysisProps {
    demandaData: ChartDataItem[];
    consumoPrimario: ChartDataItem[];
    demandaDataBase?: ChartDataItem[];
    consumoPrimarioBase?: ChartDataItem[];
    showPercentage: boolean;
}

export default function EnergyAnalysis({ demandaData, consumoPrimario, demandaDataBase, consumoPrimarioBase, showPercentage }: EnergyAnalysisProps) {
    const [showEnergyAnalysis, setShowEnergyAnalysis] = useState<boolean>(false);

    // Calculate chart data based on current view and percentage mode
    const chartData = useMemo(() => {
        const categories = ['Calefacción', 'Refrigeración', 'Iluminación', 'ACS'];
        
        const labels = ['Demanda\nBASE', 'Demanda', 'Consumo\nBASE', 'Consumo'];
        const demandaByCategory: Record<string, number> = {};
        const consumoByCategory: Record<string, number> = {};
        const demandaBaseByCategory: Record<string, number> = {};
        const consumoBaseByCategory: Record<string, number> = {};
        
        categories.forEach(category => {
            const demandaItem = demandaData.find(item => item.concepto === category);
            const consumoItem = consumoPrimario.find(item => item.concepto === category);
            const demandaBaseItem = demandaDataBase?.find(item => item.concepto === category);
            const consumoBaseItem = consumoPrimarioBase?.find(item => item.concepto === category);
            
            demandaByCategory[category] = demandaItem ? parseFloat(demandaItem.kwh_m2_ano?.toString() || '0') : 0;
            consumoByCategory[category] = consumoItem ? parseFloat(consumoItem.kwh_m2_ano?.toString() || '0') : 0;
            
            // Para los datos base, usamos la columna Base kWh/m²·año
            const baseKwhM2Key = 'Base kWh/m²·año';
            
            if (demandaDataBase && demandaBaseItem) {
                if ((demandaBaseItem as any)[baseKwhM2Key] !== undefined) {
                    demandaBaseByCategory[category] = parseFloat((demandaBaseItem as any)[baseKwhM2Key]?.toString() || '0');
                } else {
                    demandaBaseByCategory[category] = parseFloat(demandaBaseItem.kwh_m2_ano?.toString() || '0');
                }
            } else if (demandaItem && (demandaItem as any)[baseKwhM2Key]) {
demandaBaseByCategory[category] = parseFloat((demandaItem as any)[baseKwhM2Key]?.toString() || '0');
            } else if (demandaItem) {
                demandaBaseByCategory[category] = parseFloat(demandaItem.kwh_m2_ano?.toString() || '0') / 
                    (1 + parseFloat(demandaItem.vsCasoBase?.toString().replace('%', '') || '0') / 100);
            } else {
                demandaBaseByCategory[category] = 0;
            }
            
            if (consumoPrimarioBase && consumoBaseItem) {
                if ((consumoBaseItem as any)[baseKwhM2Key] !== undefined) {
                    consumoBaseByCategory[category] = parseFloat((consumoBaseItem as any)[baseKwhM2Key]?.toString() || '0');
                } else {
                    consumoBaseByCategory[category] = parseFloat(consumoBaseItem.kwh_m2_ano?.toString() || '0');
                }
            } else if (consumoItem && (consumoItem as any)[baseKwhM2Key]) {
                consumoBaseByCategory[category] = parseFloat(((consumoItem as any)[baseKwhM2Key])?.toString() || '0');
            } else if (consumoItem) {
                consumoBaseByCategory[category] = parseFloat(consumoItem.kwh_m2_ano?.toString() || '0') / 
                    (1 + parseFloat(consumoItem.vsCasoBase?.toString().replace('%', '') || '0') / 100);
            } else {
                consumoBaseByCategory[category] = 0;
            }
        });
        
        // Preparamos los datos para el gráfico con valores base y actuales
        const calefaccionData = [demandaBaseByCategory['Calefacción'], demandaByCategory['Calefacción'], consumoBaseByCategory['Calefacción'], consumoByCategory['Calefacción']];
        const refrigeracionData = [demandaBaseByCategory['Refrigeración'], demandaByCategory['Refrigeración'], consumoBaseByCategory['Refrigeración'], consumoByCategory['Refrigeración']];
        const iluminacionData = [demandaBaseByCategory['Iluminación'], demandaByCategory['Iluminación'], consumoBaseByCategory['Iluminación'], consumoByCategory['Iluminación']];
        const acsData = [demandaBaseByCategory['ACS'], demandaByCategory['ACS'], consumoBaseByCategory['ACS'], consumoByCategory['ACS']];
        
        if (showPercentage) {
            const totalDemandaBase = categories.reduce((sum, cat) => sum + demandaBaseByCategory[cat], 0);
            const totalDemandaActual = categories.reduce((sum, cat) => sum + demandaByCategory[cat], 0);
            const totalConsumoBase = categories.reduce((sum, cat) => sum + consumoBaseByCategory[cat], 0);
            const totalConsumoActual = categories.reduce((sum, cat) => sum + consumoByCategory[cat], 0);
            const convertToPercentage = (value: number, total: number): number => total > 0 ? (value / total) * 100 : 0;
            
            return {
                labels,
                calefaccionData: [
                    convertToPercentage(calefaccionData[0], totalDemandaBase),
                    convertToPercentage(calefaccionData[1], totalDemandaActual),
                    convertToPercentage(calefaccionData[2], totalConsumoBase),
                    convertToPercentage(calefaccionData[3], totalConsumoActual)
                ],
                refrigeracionData: [
                    convertToPercentage(refrigeracionData[0], totalDemandaBase),
                    convertToPercentage(refrigeracionData[1], totalDemandaActual),
                    convertToPercentage(refrigeracionData[2], totalConsumoBase),
                    convertToPercentage(refrigeracionData[3], totalConsumoActual)
                ],
                iluminacionData: [
                    convertToPercentage(iluminacionData[0], totalDemandaBase),
                    convertToPercentage(iluminacionData[1], totalDemandaActual),
                    convertToPercentage(iluminacionData[2], totalConsumoBase),
                    convertToPercentage(iluminacionData[3], totalConsumoActual)
                ],
                acsData: [
                    convertToPercentage(acsData[0], totalDemandaBase),
                    convertToPercentage(acsData[1], totalDemandaActual),
                    convertToPercentage(acsData[2], totalConsumoBase),
                    convertToPercentage(acsData[3], totalConsumoActual)
                ],
                yAxisSuffix: '%',
                tooltipSuffix: '%',
                isPercentage: true
            };
        }
        
        return {
            labels,
            calefaccionData,
            refrigeracionData,
            iluminacionData,
            acsData,
            yAxisSuffix: ' kWh/m²·año',
            tooltipSuffix: ' kWh/m²·año',
            isPercentage: false
        };
    }, [demandaData, consumoPrimario, demandaDataBase, consumoPrimarioBase, showPercentage]);

    return (
        <div className="card mb-4 border shadow-sm">
            <div 
                className="card-header bg-white border-bottom py-3" 
                style={{ cursor: 'pointer' }}
                onClick={() => setShowEnergyAnalysis(!showEnergyAnalysis)}
                aria-expanded={showEnergyAnalysis}
                aria-controls="energyAnalysisCollapse"
            >
                <div className="d-flex align-items-center justify-content-between">
                    <div className="d-flex align-items-center">
                        <Flame className="me-2 text-primary" size={20} />
                        <h5 className="mb-0 fw-semibold text-dark">Análisis Comparativo de Demanda y Consumo Energético</h5>
                    </div>
                    <div>
                        {showEnergyAnalysis ? (
                            <i className="bi bi-chevron-up"></i>
                        ) : (
                            <i className="bi bi-chevron-down"></i>
                        )}
                    </div>
                </div>
            </div>
            <div 
                className={`collapse ${showEnergyAnalysis ? 'show' : ''}`} 
                id="energyAnalysisCollapse"
            >
                <div className="card-body p-4">
                    <div className="row align-items-center mb-3">
                        <div className="col-md-8">
                            <div className="d-flex flex-wrap">
                                <div className="d-flex align-items-center me-4 mb-2">
                                    <div className="me-2" style={{ width: '16px', height: '16px', backgroundColor: '#1e4dd8' }}></div>
                                    <span className="small">Calefacción</span>
                                </div>
                                <div className="d-flex align-items-center me-4 mb-2">
                                    <div className="me-2" style={{ width: '16px', height: '16px', backgroundColor: '#ff9642' }}></div>
                                    <span className="small">Refrigeración</span>
                                </div>
                                <div className="d-flex align-items-center me-4 mb-2">
                                    <div className="me-2" style={{ width: '16px', height: '16px', backgroundColor: '#4caf50' }}></div>
                                    <span className="small">Iluminación</span>
                                </div>
                                <div className="d-flex align-items-center me-4 mb-2">
                                    <div className="me-2" style={{ width: '16px', height: '16px', backgroundColor: '#03a9f4' }}></div>
                                    <span className="small">ACS</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div style={{ height: '450px', position: 'relative' }}>
                        {demandaData.length > 0 && consumoPrimario.length > 0 && (
                            <ChartComponent
                                title="Demanda vs Consumo Energético"
                                chartType="Bar"
                                chartData={{
                                    labels: chartData.labels,
                                    datasets: [
                                        {
                                            label: 'Calefacción',
                                            data: chartData.calefaccionData,
                                            backgroundColor: '#1e4dd8',
                                            borderColor: '#1e4dd8',
                                            borderWidth: 1,
                                            stack: 'Stack 0',
                                            borderRadius: 0,
                                            barPercentage: 0.8,
                                            categoryPercentage: 0.9
                                        },
                                        {
                                            label: 'Refrigeración',
                                            data: chartData.refrigeracionData,
                                            backgroundColor: '#ff9642',
                                            borderColor: '#ff9642',
                                            borderWidth: 1,
                                            stack: 'Stack 0',
                                            borderRadius: 0,
                                            barPercentage: 0.8,
                                            categoryPercentage: 0.9
                                        },
                                        {
                                            label: 'Iluminación',
                                            data: chartData.iluminacionData,
                                            backgroundColor: '#4caf50',
                                            borderColor: '#4caf50',
                                            borderWidth: 1,
                                            stack: 'Stack 0',
                                            borderRadius: 0,
                                            barPercentage: 0.8,
                                            categoryPercentage: 0.9
                                        },
                                        {
                                            label: 'ACS',
                                            data: chartData.acsData,
                                            backgroundColor: '#03a9f4',
                                            borderColor: '#03a9f4',
                                            borderWidth: 1,
                                            stack: 'Stack 0',
                                            borderRadius: 0,
                                            barPercentage: 0.8,
                                            categoryPercentage: 0.9
                                        }
                                    ]
                                }}
                                options={{
                                    responsive: true,
                                    maintainAspectRatio: false,
                                    interaction: {
                                        mode: 'index',
                                        intersect: false,
                                    },
                                    plugins: {
                                        legend: {
                                            display: false
                                        },
                                        tooltip: {
                                            backgroundColor: 'rgba(255, 255, 255, 0.96)',
                                            titleColor: '#1a1a1a',
                                            bodyColor: '#333',
                                            borderColor: 'rgba(0, 0, 0, 0.1)',
                                            borderWidth: 1,
                                            padding: 12,
                                            usePointStyle: true,
                                            callbacks: {
                                                label: function(context: any) {
                                                    const label = context.dataset.label || '';
                                                    const value = context.parsed.y;
                                                    
                                                    return `${label}: ${value.toLocaleString('es-CL', { 
                                                        minimumFractionDigits: 2, 
                                                        maximumFractionDigits: 2 
                                                    })} ${chartData.tooltipSuffix}`;
                                                },
                                            }
                                        },
                                        datalabels: {
                                            display: false
                                        },
                                        annotation: {
                                            annotations: []
                                        }
                                    },
                                    scales: {
                                        y: {
                                            stacked: true,
                                            type: 'linear',
                                            display: true,
                                            position: 'left',
                                            title: {
                                                display: true,
                                                text: chartData.yAxisSuffix,
                                                color: '#333',
                                                font: {
                                                    weight: 'bold'
                                                }
                                            },
                                            grid: {
                                                color: 'rgba(0, 0, 0, 0.05)',
                                                drawBorder: false
                                            },
                                            ticks: {
                                                color: '#333',
                                                callback: function(value: number) {
                                                    const formatted = value.toLocaleString('es-CL', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
                                                    return formatted + (chartData.isPercentage ? ' %' : '');
                                                }
                                            },
                                            beginAtZero: true
                                        },
                                        x: {
                                            grid: {
                                                display: false,
                                                drawBorder: false
                                            }
                                        }
                                    },
                                    animation: {
                                        duration: 1000,
                                        easing: 'easeInOutQuart'
                                    }
                                }}
                            />
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
