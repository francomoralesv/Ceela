'use client'
import { DetailedUsersReport } from "@/components/reports/DetailedUsersReport";
import EnergyChart from "@/components/reports/EnergyReport";
import { PerformanceReport } from "@/components/reports/PerformanceReport";
import { ProjectsByMonthReport } from "@/components/reports/ProjectsByMonthReport";
import {
    ArcElement,
    BarElement,
    CategoryScale,
    Chart as ChartJS,
    Title as ChartTitle,
    Legend,
    LinearScale,
    LineElement,
    PointElement,
    RadialLinearScale,
    Tooltip,
} from "chart.js";
import { useEffect, useState } from "react";
import Breadcrumb from "../src/components/common/Breadcrumb";
import Card from "../src/components/common/Card";
import Title from "../src/components/Title";
import { useApi } from "../src/hooks/useApi";
import useAuth from "../src/hooks/useAuth";
import { notify } from "@/utils/notify";

ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    LineElement,
    PointElement,
    ArcElement,
    RadialLinearScale,
    ChartTitle,
    Tooltip,
    Legend
)



interface ProjectsByMonthReport {
    month: string[];
    total_projects: number[];
}

interface DetailedUser {
    id: number;
    name: string;
    email: string;
    last_name: string;
    created_at: string;
    status: boolean;
    project_count: number;
    project_ids: number[];
}

// Función para convertir datos de objeto a array
function convertObjectToArrays(data: any): any {
    if (!data) return null;

    // Crear un objeto con la misma estructura pero con arrays
    const result: any = {};

    // Para cada propiedad del objeto
    Object.keys(data).forEach(key => {
        // Si la propiedad es un objeto (como los que vienen de pandas.to_dict())
        if (data[key] && typeof data[key] === 'object' && !Array.isArray(data[key])) {
            // Convertir de {0: valor, 1: valor} a [valor, valor]
            result[key] = Object.values(data[key]);
        } else {
            // Si ya es un array, mantenerlo igual
            result[key] = data[key];
        }
    });

    return result;
}
function getCssVarValue(varName: string, fallback: string) {
    if (typeof window === "undefined") return fallback
    const value = getComputedStyle(document.documentElement)
        .getPropertyValue(varName)
        .trim()
    return value || fallback
}

const DashboardPage: React.FC = () => {
    // --- EnergyChart State and Effect ---
    interface EnergyChartDataset {
        label: string;
        data: number[];
    }
    
    interface EnergyChartData {
        labels: string[];
        datasets: EnergyChartDataset[];
    }
    
    const [energyChartData, setEnergyChartData] = useState<EnergyChartData>({
        labels: [],
        datasets: [],
    });
    const [loadingEnergyChart, setLoadingEnergyChart] = useState(false);

    useAuth()
    const [primaryColor, setPrimaryColor] = useState("#3ca7b7")
    const api = useApi();

    const [loadingProjectsByMonth, setLoadingProjectsByMonth] = useState(true);
    const [loadingDetailedUsers, setLoadingDetailedUsers] = useState(true);
    const [projectsByMonth, setProjectsByMonth] = useState<ProjectsByMonthReport | null>(null);
    const [loadingPerformance, setLoadingPerformance] = useState(true);
    const [performanceData, setPerformanceData] = useState<any>(null);
    const [detailedUsers, setDetailedUsers] = useState<DetailedUser[] | null>(null);

    // --- Filtros globales (dummy) ---
    const [selectedYear, setSelectedYear] = useState('');
    const [selectedCountry, setSelectedCountry] = useState('');
    const [selectedZone, setSelectedZone] = useState('');
    const [selectedTypology, setSelectedTypology] = useState('');

    // Datos dummy para selects
    const years = ['','2022', '2023', '2024', '2025'];
    const countries = ['','Perú', 'Ecuador', 'Chile', 'Colombia'];
    const zones = ['','A', 'B', 'C', 'D','E','F'];
    const typologies = ['','Residencial en altura', 'Residencial en extensión', 'Educación', 'Salud', 'Comercio', 'Servicios (oficinas)'];

    // Elimina duplicados de EnergyChart State and Effect

    useEffect(() => {
        const fetchEnergyReport = async () => {
            setLoadingEnergyChart(true);
            try {
                const params: string[] = [];
                if (selectedYear) params.push(`year=${encodeURIComponent(selectedYear)}`);
                if (selectedCountry) params.push(`country=${encodeURIComponent(selectedCountry)}`);
                if (selectedZone) params.push(`zone=${encodeURIComponent(selectedZone)}`);
                if (selectedTypology) params.push(`typology=${encodeURIComponent(selectedTypology)}`);
                const queryString = params.length ? `?${params.join('&')}` : '';
                const response = await api.get(`reports/energy${queryString}`);
                if (response?.status === "success" && Array.isArray(response.data)) {
                    setEnergyChartData({
                        labels: response.data.map((item: any) => `${item.year} - ${item.country}`),
                        datasets: [
                            {
                                label: "Demanda Calefacción",
                                data: response.data.map((item: any) => item.demanda_calefaccion)
                            },
                            {
                                label: "Demanda Refrigeración",
                                data: response.data.map((item: any) => item.demanda_refrigeracion)
                            },
                            {
                                label: "Consumo Calefacción",
                                data: response.data.map((item: any) => item.consumo_calefaccion)
                            },
                            {
                                label: "Consumo Refrigeración",
                                data: response.data.map((item: any) => item.consumo_refrigeracion)
                            }
                        ]
                    });
                } else {
                    setEnergyChartData({ labels: [], datasets: [] });
                }
            } catch (e) {
                setEnergyChartData({ labels: [], datasets: [] });
            } finally {
                setLoadingEnergyChart(false);
            }
        };
        fetchEnergyReport();
    }, [selectedYear, selectedCountry, selectedZone, selectedTypology]);

    useEffect(() => {
        const pColor = getCssVarValue("--primary-color", "#3ca7b7")
        setPrimaryColor(pColor)
    }, [])

    // Fetch performance (reporte) data usando los filtros globales
    useEffect(() => {
        const fetchPerformanceReport = async () => {
            setLoadingPerformance(true);
            try {
                const params = new URLSearchParams();
                if (selectedYear) params.append('year', selectedYear);
                if (selectedCountry) params.append('country', selectedCountry);
                if (selectedZone) params.append('zone', selectedZone);
                if (selectedTypology) params.append('building_type', selectedTypology);
                const url = `${process.env.NEXT_PUBLIC_API_ENDPOINT?.replace(/\/$/, '')}/calculation-results/report?${params.toString()}`;
                const token = localStorage.getItem('token');
                const headers: Record<string, string> = { accept: 'application/json' };
                if (token) headers['Authorization'] = `Bearer ${token}`;
                const res = await fetch(url, { headers });
                if (!res.ok) throw new Error('Error al obtener el reporte');
                const data = await res.json();
                // Mapear la respuesta al formato esperado por PerformanceReport
                const mappedPerformance: any = {
                    co2_equivalent: {
                        total: data?.co2_eq?.total ?? 0,
                        baseline: data?.co2_eq?.baseline ?? 0
                    },
                    comfort_hours: {
                        heating: data?.horas_confort_anual?.calefaccion ?? 0,
                        cooling: data?.horas_confort_anual?.refrigeracion ?? 0,
                        baseline: data?.horas_confort_anual?.baseline ?? 0
                    }
                };
                setPerformanceData(mappedPerformance);
            } catch (err: any) {
                notify(err.message || 'Error inesperado', 'error');
                setPerformanceData(null);
            } finally {
                setLoadingPerformance(false);
            }
        };
        fetchPerformanceReport();
    }, [selectedYear, selectedCountry, selectedZone, selectedTypology]);

    // Fetch all report data concurrentemente
    useEffect(() => {
        const fetchReportData = async () => {
            try {
                // Construir query string para los filtros activos
                const params = [];
                if (selectedYear) params.push(`year=${encodeURIComponent(selectedYear)}`);
                if (selectedCountry) params.push(`country=${encodeURIComponent(selectedCountry)}`);
                if (selectedZone) params.push(`climate_zone=${encodeURIComponent(selectedZone)}`);
                if (selectedTypology) params.push(`building_type=${encodeURIComponent(selectedTypology)}`);
                const queryString = params.length ? `?${params.join('&')}` : '';
                // Prepare all API requests to run concurrently
                const requests = [
                    api.get(`reports/projects_registered_by_month${queryString}`).then(response => {
                        if (response?.status === 'success') {
                            const data = convertObjectToArrays(response?.data);
                            if (data) {
                                Object.keys(data).forEach(key => {
                                    if (Array.isArray(data[key])) {
                                        data[key] = data[key].reverse();
                                    }
                                });
                            }
                            setProjectsByMonth(data);
                        }
                        setLoadingProjectsByMonth(false);
                    }).catch(error => {
                        console.error("Error fetching projects by month:", error);
                        setLoadingProjectsByMonth(false);
                    }),

                    // Detailed users report
                    api.get('reports/users/detailed').then(response => {
                        if (response?.status === 'success') {
                            setDetailedUsers(response?.data);
                        }
                        setLoadingDetailedUsers(false);
                    }).catch(error => {
                        console.error("Error fetching detailed users:", error);
                        setLoadingDetailedUsers(false);
                    }),
                ];
                setLoadingPerformance(false);

                // Execute all requests concurrently
                await Promise.all(requests);

            } catch (error) {
                console.error("Error fetching report data:", error);
                setLoadingProjectsByMonth(false);
                setLoadingDetailedUsers(false);
            }
        };

        fetchReportData();
    }, [selectedYear, selectedCountry, selectedZone, selectedTypology]);


    return (
        <div className="">
            <Card className="header-card">
                <div className="d-flex align-items-center w-100">
                    <Title text="Dashboard" />
                    <Breadcrumb items={[
                        { title: 'Dashboard', href: '/dashboard', active: true },
                    ]} />
                </div>
            </Card>

            {/* Filtros globales */}
            {/* Filtros SOLO para los reportes Proyectos Registrados y Energy Report */}
            <Card className="mb-3 p-3">
                <div className="row g-2 align-items-end">
                    <div className="col-6 col-md-3">
                        <label>Año</label>
                        <select className="form-select" value={selectedYear} onChange={e => setSelectedYear(e.target.value)}>
                            {years.map(year => <option key={year} value={year}>{year}</option>)}
                        </select>
                    </div>
                    <div className="col-6 col-md-3">
                        <label>País</label>
                        <select className="form-select" value={selectedCountry} onChange={e => setSelectedCountry(e.target.value)}>
                            {countries.map(country => <option key={country} value={country}>{country}</option>)}
                        </select>
                    </div>
                    <div className="col-6 col-md-3">
                        <label>Zona climática</label>
                        <select className="form-select" value={selectedZone} onChange={e => setSelectedZone(e.target.value)}>
                            {zones.map(zone => <option key={zone} value={zone}>{zone}</option>)}
                        </select>
                    </div>
                    <div className="col-6 col-md-3">
                        <label>Tipología de edificación</label>
                        <select className="form-select" value={selectedTypology} onChange={e => setSelectedTypology(e.target.value)}>
                            {typologies.map(typology => <option key={typology} value={typology}>{typology}</option>)}
                        </select>
                    </div>
                </div>
            </Card>


            <Card className="charts-card p-2">
                <div className="row g-3 mt-1">

                    <div className="col-md-6 col-lg-6">
                        <ProjectsByMonthReport
                            loading={loadingProjectsByMonth}
                            data={projectsByMonth}
                            primaryColor={primaryColor}
                        />
                    </div>

                    <div className="col-md-6 col-lg-6">
                        <EnergyChart
                            chartData={energyChartData}
                            loading={loadingEnergyChart}
                            primaryColor={primaryColor}
                        />
                    </div>



                    <div className="col-md-6 col-lg-6">
                        <DetailedUsersReport
                            loading={loadingDetailedUsers}
                            data={detailedUsers}
                        />
                    </div>

                    <div className="col-md-6 col-lg-6">
                        <PerformanceReport
                            loading={loadingPerformance}
                            data={performanceData}
                        />
                    </div>

                </div>
            </Card>
        </div>
    );
};

export default DashboardPage;
