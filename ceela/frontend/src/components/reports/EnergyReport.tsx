'use client';
import ChartComponent from "@/components/chart/ChartComponent";
import { exportToExcel } from "@/components/shared/exportToExcel";

const chartOptions = {
    scales: {
        x: {
            grid: {
                display: true, // Mostrar líneas de fondo
                color: 'rgba(180,180,200,0.2)', // Color claro tipo cuaderno
                lineWidth: 1,
                drawTicks: true,
                borderDash: [2, 4] // Líneas punteadas suaves
            }
        },
        y: {
            grid: {
                display: true,
                color: 'rgba(180,180,200,0.25)', // También líneas de referencia
                lineWidth: 1,
                drawTicks: true
            },
            ticks: {
                minRotation: 90,
                maxRotation: 90
            }
        }
    },
    maintainAspectRatio: false,
    responsive: true
};

interface EnergyChartProps {
    chartData: any;
    loading?: boolean;
    primaryColor?: string;
    filters?: { year?: string | number; country?: string };
}

const EnergyChart = ({ chartData, loading = false, primaryColor = '#3CB6E3', filters }: EnergyChartProps) => {
    const handleDownloadExcel = () => {
        const finalDatasets = [
            ...demandDatasets,
            ...consumptionDatasets
        ];

        if (axisLabels && finalDatasets.length > 0) {
            const reportTitle = ['Reporte de eficiencia energética'];
            const generationDate = ['Fecha de generación:', new Date().toLocaleString('es-CL')];
            const appliedFilters = ['Filtros aplicados:', `Año: ${filters?.year || 'Todos'}, País: ${filters?.country || 'Todos'}`];
            const blankRow: string[] = [];

            const tableHeaders = ['Referencia', ...finalDatasets.map((ds: any) => ds.label)];

            const dataRows = axisLabels.map((label: string, idx: number) => {
                const values = finalDatasets.map((ds: any) => ds.data[idx] ?? '');
                return [label, ...values];
            });

            const excelData = [
                reportTitle,
                generationDate,
                appliedFilters,
                blankRow,
                tableHeaders,
                ...dataRows
            ];

            exportToExcel({
                data: excelData,
                fileName: 'reporte_energia_detallado.xlsx',
                sheetName: 'Reporte de Energia',
            });
        }
    };

    // Estilo celeste igual que Proyectos Registrados, pero para todas las series
    // Paleta de colores pastel agradable para cada serie
    const pastelColors = [
        '#A0C4FF', '#BDB2FF', '#FFC6FF', '#FFD6A5', '#FDFFB6', '#CAFFBF', '#9BF6FF', '#B5EAD7', '#FFDAC1', '#FFB7B2'
    ];
    // --- Lógica para comparación coherente ---
    let comparisonLabel = '';
    let newChartData = chartData;
    if (chartData && chartData.labels && chartData.datasets) {
        if (filters?.year === 'Todos') {
            comparisonLabel = 'País';
            newChartData = {
                ...chartData,
                labels: chartData.labels.map((label: string) => {
                    const parts = label.split(' - ');
                    return parts.length > 1 ? parts[1] : label;
                })
            };
        }
        else if (filters?.country === 'Todos') {
            comparisonLabel = 'Año';
            newChartData = {
                ...chartData,
                labels: chartData.labels.map((label: string) => {
                    const parts = label.split(' - ');
                    return parts.length > 1 ? parts[0] : label;
                })
            };
        }
        else if (filters?.year === 'Todos' && filters?.country === 'Todos') {
            comparisonLabel = 'País y Año';
        }
    }

    const styledChartData = newChartData && newChartData.labels && newChartData.datasets ? {
        ...newChartData,
        datasets: newChartData.datasets.map((ds: any, idx: number) => ({
            ...ds,
            backgroundColor: pastelColors[idx % pastelColors.length] + '99',
            borderColor: pastelColors[idx % pastelColors.length],
            borderWidth: 2,
            pointRadius: 4,
            pointBackgroundColor: pastelColors[idx % pastelColors.length],
            tension: 0.4,
            fill: false
        }))
    } : newChartData;

    // Armado de datasets para barras de demandas y consumos
    const demandLabels = ['Demanda Calefacción', 'Demanda Refrigeración'];
    const consumptionLabels = ['Consumo Calefacción', 'Consumo Refrigeración'];
    const baseCalefaccionColor = 'rgb(72,181,193)';
    const demandColors = [baseCalefaccionColor, 'rgb(185,229,251)']; // Calefacción: fijo, Refrigeración: color específico
    const consumptionColors = ['rgb(247,144,30)', 'rgb(255,224,108)']; // Calefacción: naranja, Refrigeración: amarillo claro

    // Generar datos para Demandas
    const demandDatasets = [
        {
            label: demandLabels[0],
            data: (styledChartData?.datasets?.find((ds: any) => ds.label.includes('Demanda Calefacción'))?.data) || [],
            backgroundColor: demandColors[0],
            borderColor: demandColors[0],
            borderWidth: 1,
            borderRadius: 6,
        },
        {
            label: demandLabels[1],
            data: (styledChartData?.datasets?.find((ds: any) => ds.label.includes('Demanda Refrigeración'))?.data) || [],
            backgroundColor: demandColors[1],
            borderColor: demandColors[1],
            borderWidth: 1,
            borderRadius: 6,
        }
    ];
    // Generar datos para Consumos
    const consumptionDatasets = [
        {
            label: consumptionLabels[0],
            data: (styledChartData?.datasets?.find((ds: any) => ds.label.includes('Consumo Calefacción'))?.data) || [],
            backgroundColor: consumptionColors[0],
            borderColor: consumptionColors[0],
            borderWidth: 1,
            borderRadius: 6,
        },
        {
            label: consumptionLabels[1],
            data: (styledChartData?.datasets?.find((ds: any) => ds.label.includes('Consumo Refrigeración'))?.data) || [],
            backgroundColor: consumptionColors[1],
            borderColor: consumptionColors[1],
            borderWidth: 1,
            borderRadius: 6,
        }
    ];

    // Labels para el eje X (países, años, etc)
    const axisLabels = styledChartData?.labels || [];

    return (

            <div style={{ position: 'relative' }}>
                <button
                    className="btn btn-sm btn-success"
                    style={{ position: 'absolute', top: 0, right: 0, zIndex: 2 }}
                    onClick={handleDownloadExcel}
                >
                    <i className="bi bi-download me-2"></i>
                    Descargar Excel
                </button>
                <ChartComponent
                    title="Reporte de eficiencia energética (kWh)"
                    chartData={{
                        labels: axisLabels,
                        datasets: [
                            ...demandDatasets.map(ds => ({
                                ...ds,
                                barThickness: 20,
                                data: axisLabels.map((_: string, i: number) => ds.data[i] ?? null),
                                categoryPercentage: 0.7,
                                barPercentage: 0.95
                            })),
                            ...consumptionDatasets.map(ds => ({
                                ...ds,
                                barThickness: 20,
                                data: axisLabels.map((_: string, i: number) => ds.data[i] ?? null),
                                categoryPercentage: 0.7,
                                barPercentage: 0.95
                            }))
                        ]
                    }}
                    chartType="Bar"
                    options={{
                        ...chartOptions,
                        indexAxis: 'y', 
                        plugins: {
                            legend: { position: 'bottom', labels: { font: { size: 14 } } },
                            datalabels: {
                                anchor: 'end',
                                align: 'end',
                                color: '#222',
                                font: { weight: 'bold', size: 12 },
                                maxRotation: 0,
                                minRotation: 0
                            },
                            annotation: {
                                annotations: [
                                    {
                                        type: 'line',
                                        mode: 'vertical',
                                        scaleID: 'y', // Cambiar a 'y' para horizontal
                                        value: axisLabels.length > 0 ? axisLabels[Math.floor(axisLabels.length/2)] : undefined,
                                        borderColor: '#888',
                                        borderWidth: 2,
                                        borderDash: [6, 6],
                                        label: {
                                            enabled: true,
                                            content: 'Comparación',
                                            position: 'top',
                                            color: '#888',
                                            font: { weight: 'bold' }
                                        }
                                    }
                                ]
                            }
                        }
                    }}
                />
            </div>
    );
};

export default EnergyChart;
