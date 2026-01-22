import ChartComponent from "@/components/chart/ChartComponent";
import { ChartLoader } from "./ChartLoader";

interface BuildingLevelsReport {
    number_levels: number[];
    total: number[];
}

interface BuildingLevelsReportProps {
    loading: boolean;
    data: BuildingLevelsReport | null;
    primaryColor: string;
    primaryColorAlpha: string;
}

export const BuildingLevelsReport = ({ loading, data, primaryColor, primaryColorAlpha }: BuildingLevelsReportProps) => {
    const chartData = data ? {
        labels: Array.isArray(data?.number_levels)
            ? data?.number_levels?.map(level => `${level} Niveles`)
            : [],
        datasets: [
            {
                label: "Distribución de Niveles",
                data: data?.total || [],
                borderColor: primaryColor,
                backgroundColor: primaryColorAlpha,
                tension: 0.4,
                fill: true,
            },
        ],
    } : {
        labels: ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio"],
        datasets: [
            {
                label: "Proyectos Nuevos",
                data: [12, 19, 3, 5, 2, 3],
                borderColor: primaryColor,
                backgroundColor: primaryColorAlpha,
                tension: 0.4,
                fill: true,
            },
        ],
    };

    if (loading) {
        return <ChartLoader title="Distribución de Niveles de Edificios" />;
    }

    return (
        <ChartComponent
            title="Distribución de Niveles de Edificios"
            chartData={chartData}
            chartType="Line"
            options={{
                maintainAspectRatio: false,
                responsive: true,
                aspectRatio: 1.5
            }}
        />
    );
};
