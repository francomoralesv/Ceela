import { ChartLoader } from "./ChartLoader";
import Card from "@/components/common/Card";

interface PerformanceData {
    co2_equivalent: {
        total: number;
        baseline: number;
    };
    comfort_hours: {
        heating: number;
        cooling: number;
        baseline: number;
    };
}

interface PerformanceReportProps {
    loading: boolean;
    data: PerformanceData | null;
}

export const PerformanceReport = ({ loading, data }: PerformanceReportProps) => {
    if (loading) {
        return <ChartLoader title="Indicadores de desempeño" />;
    }

    return (
        <Card>
            <div className="container mb-4">
                <div className="row mb-4">
                    <div className="col-12">
                        <h3 className="h6 text-muted mb-3 mt-2">
                            <i className="bi bi-cloud" style={{ color: '#2ab0c5', marginRight: 8 }} title="Emisiones de CO₂" />
                            CO₂ equivalente
                        </h3>
                        <div className="row g-3">
                            <div className="col-md-6">
                                <div className="card text-center shadow-sm border-0" style={{ background: 'linear-gradient(135deg, #e0f7fa 60%, #ffffff 100%)' }}>
                                    <div className="card-body">
                                        <div className="h2 fw-bold mb-1 number-with-icon" style={{ color: '#2ab0c5' }} title="Total de emisiones equivalentes de CO₂">
                                            <i className="bi bi-bar-chart-fill me-1" />
                                            <span className="number-value">{data?.co2_equivalent?.total ?? 0}</span>
                                        </div>
                                        <span className="badge bg-light text-dark border">Total</span>
                                    </div>
                                </div>
                            </div>
                            <div className="col-md-6">
                                <div className="card text-center shadow-sm border-0" style={{ background: 'linear-gradient(135deg, #f0f4c3 60%, #ffffff 100%)' }}>
                                    <div className="card-body">
                                        <div className="h2 fw-bold mb-1 number-with-icon" style={{ color: '#b2b200' }} title="Porcentaje respecto a línea base">
                                            <i className="bi bi-percent me-1" />
                                            <span className="number-value">{data?.co2_equivalent?.baseline ?? 0}</span>
                                        </div>
                                        <span className="badge bg-light text-dark border">Línea base</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="row mt-4">
                    <div className="col-12">
                        <h3 className="h6 text-muted mb-3">
                            <i className="bi bi-thermometer-half" style={{ color: '#2ab0c5', marginRight: 8 }} title="Horas de confort anual" />
                            Horas dentro del rango de confort anual
                        </h3>
                        <div className="row comfort-cards g-3">
                            <div className="col-12 col-sm-6 col-md-6 col-lg-4 mb-3">
                                <div className="card text-center shadow-sm border-0 h-100" style={{ background: 'linear-gradient(135deg, #ffe0b2 60%, #ffffff 100%)' }}>
                                    <div className="card-body d-flex flex-column justify-content-center align-items-center">
                                        <div className="h2 fw-bold mb-1 number-with-icon" style={{ color: '#ff9800' }} title="Horas de calefacción en confort">
                                            <i className="bi bi-fire me-1" />
                                            <span className="number-value">{data?.comfort_hours?.heating ?? 0}</span>
                                        </div>
                                        <span className="badge bg-light text-dark border">Calefacción</span>
                                    </div>
                                </div>
                            </div>
                            <div className="col-12 col-sm-6 col-md-6 col-lg-4 mb-3">
                                <div className="card text-center shadow-sm border-0 h-100" style={{ background: 'linear-gradient(135deg, #b3e5fc 60%, #ffffff 100%)' }}>
                                    <div className="card-body d-flex flex-column justify-content-center align-items-center">
                                        <div className="h2 fw-bold mb-1 number-with-icon" style={{ color: '#039be5' }} title="Horas de refrigeración en confort">
                                            <i className="bi bi-snow2 me-1" />
                                            <span className="number-value">{data?.comfort_hours?.cooling ?? 0}</span>
                                        </div>
                                        <span className="badge bg-light text-dark border">Refrigeración</span>
                                    </div>
                                </div>
                            </div>
                            <div className="col-12 col-sm-6 col-md-6 col-lg-4 mb-3">
                                <div className="card text-center shadow-sm border-0 h-100" style={{ background: 'linear-gradient(135deg, #f8bbd0 60%, #ffffff 100%)' }}>
                                    <div className="card-body d-flex flex-column justify-content-center align-items-center">
                                        <div className="h2 fw-bold mb-1 number-with-icon" style={{ color: '#d81b60' }} title="Porcentaje respecto a línea base">
                                            <i className="bi bi-percent me-1" />
                                            <span className="number-value">{data?.comfort_hours?.baseline ?? 0}</span>
                                        </div>
                                        <span className="badge bg-light text-dark border">Línea base</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <style jsx>{`
                /* Responsive font sizing for numbers */
                .number-with-icon {
                    font-size: clamp(1.2rem, 3vw, 2rem);
                    width: 100%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .badge {
                    font-size: min(1rem, 3.5vw);
                    padding: 0.5em 1em;
                    word-break: break-word;
                    white-space: normal;
                    max-width: 100%;
                    display: inline-block;
                    overflow: hidden;
                    text-overflow: ellipsis;
                }
                .comfort-cards .card {
                    transition: all 0.3s ease;
                    margin-bottom: 1rem;
                    overflow: hidden;
                }
                .comfort-cards .card-body {
                    min-height: 120px;
                    overflow: hidden;
                    word-wrap: break-word;
                }
                .number-with-icon {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    flex-wrap: nowrap;
                    max-width: 100%;
                    overflow: hidden;
                }
                .number-value {
                    font-size: min(1em, 16px);
                    max-width: 100%;
                    display: inline-block;
                    white-space: nowrap;
                    transform-origin: left center;
                }
                @media (max-width: 576px) {
                    .badge {
                        font-size: 0.9rem;
                        padding: 0.4em 0.6em;
                        max-width: 90vw;
                    }
                    .card-body {
                        padding-left: 0.3rem;
                        padding-right: 0.3rem;
                        min-height: 100px;
                        overflow: hidden;
                    }
                    .comfort-cards .card {
                        margin-bottom: 1rem;
                    }
                    .comfort-cards .col-sm-6 {
                        width: 100%;
                    }
                    .number-with-icon {
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        flex-wrap: nowrap;
                        font-size: calc(0.8rem + 1vw);
                    }
                    .number-value {
                        font-size: min(1em, 14px);
                        max-width: 100%;
                    }
                }
            `}</style>
        </Card>
    );
};