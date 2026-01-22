import ChartComponent from "@/components/chart/ChartComponent";
import { ChartLoader } from "./ChartLoader";

interface TotalSurfaceByCountryReport {
    country: string[];
    total_surface: number[];
}

interface TotalSurfaceReportProps {
    loading: boolean;
    data: TotalSurfaceByCountryReport | null;
    generateColorPalette: (numColors: number) => string[];
}

export const TotalSurfaceReport = ({ loading, data, generateColorPalette }: TotalSurfaceReportProps) => {
    const chartData = data ? {
        labels: Array.isArray(data?.country) ? data?.country : [],
        datasets: [
            {
                label: "Superficie Total (m²)",
                data: Array.isArray(data?.total_surface) ? data?.total_surface : [],
                backgroundColor: generateColorPalette(
                    Array.isArray(data?.country) ? data?.country.length : 5
                ),
                borderWidth: 1,
            },
        ],
    } : {
        labels: ["Chile", "Argentina", "Brasil", "Colombia", "Perú"],
        datasets: [
            {
                label: "Superficie Total (m²)",
                data: [15000, 12000, 18000, 9000, 11000],
                backgroundColor: generateColorPalette(5),
                borderWidth: 1,
            },
        ],
    };

    if (loading) {
        return <ChartLoader title="Superficie Total por País" />;
    }

    return (
        <ChartComponent
            title="Superficie Total por País"
            chartData={chartData}
            chartType="Bar"
            options={{
                maintainAspectRatio: false,
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Superficie (m²)'
                        }
                    }
                }
            }}
        />
    );
};
