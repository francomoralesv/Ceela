import ChartComponent from "@/components/chart/ChartComponent";
import { ChartLoader } from "./ChartLoader";

interface UsersReport {
    active: string[];
    total: number[];
}

interface UserReportProps {
    loading: boolean;
    data: UsersReport | null;
}

export const UserReport = ({ loading, data }: UserReportProps) => {
    const chartData = data ? {
        labels: Array.isArray(data?.active) ? data?.active : [],
        datasets: [
            {
                label: "Usuarios",
                data: Array.isArray(data?.total) ? data?.total : [],
                backgroundColor: data?.active?.map((status) =>
                    status === "Activo" || status === "Activos" ? "#1dd1a1" : "#8395a7"
                ),
            },
        ],
    } : {
        labels: ["Activos", "Inactivos"],
        datasets: [
            {
                label: "Usuarios",
                data: [75, 25],
                backgroundColor: ["#1dd1a1", "#8395a7"],
            },
        ],
    };

    if (loading) {
        return <ChartLoader title="Usuarios Activos vs Inactivos" />;
    }

    return (
        <ChartComponent
            title="Usuarios Activos vs Inactivos"
            chartData={chartData}
            chartType="Bar"
            options={{
                maintainAspectRatio: false,
                responsive: true
            }}
        />
    );
};
