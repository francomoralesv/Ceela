import ChartComponent from "@/components/chart/ChartComponent";
import { ChartLoader } from "./ChartLoader";

interface BuildingTypeReport {
    building_type: string[];
    total_proyectos: number[];
}

interface BuildingTypesReportProps {
    loading: boolean;
    data: BuildingTypeReport | null;
    generateColorPalette: (numColors: number) => string[];
}

export const BuildingTypesReport = ({ loading, data, generateColorPalette }: BuildingTypesReportProps) => {
    const chartData = data ? {
        labels: Array.isArray(data?.building_type) ? data?.building_type : [],
        datasets: [
            {
                label: "Tipos de Edificios",
                data: Array.isArray(data?.total_proyectos) ? data?.total_proyectos : [],
                backgroundColor: generateColorPalette(
                    Array.isArray(data?.building_type) ? data?.building_type.length : 5
                ),
            },
        ],
    } : {
        labels: ["Proyecto 1", "Proyecto 2", "Proyecto 3"],
        datasets: [
            {
                label: "Proyectos",
                data: [10, 20, 30],
                backgroundColor: generateColorPalette(3),
            },
        ],
    };

    if (loading) {
        return <ChartLoader title="Distribución de Tipos de Edificios" />;
    }

    return (
        <ChartComponent
            title="Distribución de Tipos de Edificios"
            chartData={chartData}
            chartType="Bar"
            options={{
                maintainAspectRatio: false,
                responsive: true
            }}
        />
    );
};
