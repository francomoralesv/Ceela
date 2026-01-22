import ChartComponent from "@/components/chart/ChartComponent";
import { ChartLoader } from "./ChartLoader";

interface ProjectsByCountryReport {
    country: string[];
    total: number[];
}

interface ProjectsByCountryReportProps {
    loading: boolean;
    data: ProjectsByCountryReport | null;
    generateColorPalette: (numColors: number) => string[];
}

export const ProjectsByCountryReport = ({ loading, data, generateColorPalette }: ProjectsByCountryReportProps) => {
    const chartData = data ? {
        labels: Array.isArray(data?.country) ? data?.country : [],
        datasets: [
            {
                label: "Proyectos por País",
                data: Array.isArray(data?.total) ? data?.total : [],
                backgroundColor: generateColorPalette(
                    Array.isArray(data?.country) ? data?.country.length : 5
                ),
            },
        ],
    } : {
        labels: ["Chile", "Argentina", "Brasil", "Colombia", "Perú"],
        datasets: [
            {
                label: "Proyectos por País",
                data: [5, 9, 3, 7, 4],
                backgroundColor: generateColorPalette(5),
            },
        ],
    };

    if (loading) {
        return <ChartLoader title="Proyectos por País" />;
    }

    return (
        <ChartComponent
            title="Proyectos por País"
            chartData={chartData}
            chartType="Pie"
            options={{
                maintainAspectRatio: false,
                responsive: true
            }}
        />
    );
};
