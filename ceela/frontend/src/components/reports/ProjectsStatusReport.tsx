import ChartComponent from "@/components/chart/ChartComponent";
import { ChartLoader } from "./ChartLoader";

interface ProjectsStatusReport {
    status: string[];
    total: number[];
}

interface ProjectsStatusReportProps {
    loading: boolean;
    data: ProjectsStatusReport | null;
    generateColorPalette: (numColors: number) => string[];
}

export const ProjectsStatusReport = ({ loading, data, generateColorPalette }: ProjectsStatusReportProps) => {
    const chartData = data ? {
        labels: Array.isArray(data?.status) ? data?.status : [],
        datasets: [
            {
                label: "Estado de Proyectos",
                data: Array.isArray(data?.total) ? data?.total : [],
                backgroundColor: generateColorPalette(
                    Array.isArray(data?.status) ? data?.status.length : 3
                ),
            },
        ],
    } : {
        labels: ["Completados", "En Progreso", "Pendientes"],
        datasets: [
            {
                label: "Estado de Proyectos",
                data: [50, 30, 20],
                backgroundColor: generateColorPalette(3),
            },
        ],
    };

    if (loading) {
        return <ChartLoader title="Estado de Proyectos" />;
    }

    return (
        <ChartComponent
            title="Estado de Proyectos"
            chartData={chartData}
            chartType="Doughnut"
            options={{
                maintainAspectRatio: false,
                responsive: true
            }}
        />
    );
};
