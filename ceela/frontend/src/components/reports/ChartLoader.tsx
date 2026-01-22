import Card from "../common/Card";

interface ChartLoaderProps {
    title: string;
}

export const ChartLoader = ({ title }: ChartLoaderProps) => (
    <div className="col-md-6 col-lg-4">
        <Card className="chart-card p-4 text-center h-100">
            <h5>{title}</h5>
            <div className="spinner-border text-primary mt-4" role="status">
                <span className="visually-hidden">Cargando...</span>
            </div>
            <p className="mt-2">Cargando datos...</p>
        </Card>
    </div>
);
