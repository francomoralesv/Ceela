import { ApexOptions } from 'apexcharts';
import dynamic from 'next/dynamic';
import React, { ReactElement } from 'react';
import Title from './Title';

const ReactApexChart = dynamic(() => import('react-apexcharts'), { ssr: false });

interface Project {
    divisions?: {
        department?: string;
    };
}

interface ChartProps {
    data: {
        projects: Project[];
    };
}

interface ChartOptions extends ApexOptions {
    chart: {
        type: 'bar';
        toolbar: {
            show: boolean;
        };
    };
}

const ChartProjectsByRegion = ({ data }: ChartProps): ReactElement => {
    const [departments, setDepartments] = React.useState<string[]>([]);
    const [projectCounts, setProjectCounts] = React.useState<number[]>([]);

    React.useEffect(() => {
        const departmentMap = new Map<string, number>();
        
        data.projects.forEach((project: Project) => {
            const department = project.divisions?.department || 'No especificado';
            departmentMap.set(department, (departmentMap.get(department) || 0) + 1);
        });

        const sortedDepartments = Array.from(departmentMap.entries())
            .sort((a, b) => b[1] - a[1]);

        setDepartments(sortedDepartments.map(([dept]) => dept));
        setProjectCounts(sortedDepartments.map(([, count]) => count));
    }, [data]);

    const chartOptions: ChartOptions = {
        chart: {
            type: 'bar',
            toolbar: {
                show: false
            }
        },
        plotOptions: {
            bar: {
                horizontal: true,
                borderRadius: 4,
                distributed: true
            }
        },
        dataLabels: {
            enabled: false
        },
        colors: ['#00B4D8', '#90E0EF', '#CAF0F8', '#0077B6', '#023E8A'],
        xaxis: {
            categories: departments,
            labels: {
                style: {
                    fontSize: '12px',
                    fontWeight: '500'
                }
            }
        },
        grid: {
            borderColor: '#E2E8F0',
            strokeDashArray: 4,
            xaxis: {
                lines: {
                    show: true
                }
            },
            yaxis: {
                lines: {
                    show: false
                }
            }
        },
        tooltip: {
            y: {
                formatter: (val: number): string => `${val} proyectos`
            }
        },
        legend: {
            show: false
        }
    };

    const series = [{
        name: 'Proyectos',
        data: projectCounts
    }];

    return (
        <div className="card ">
            <div className="card-header">
                <Title text="Distribución por Región" />
            </div>
            <div className="card-body ">
                <div style={{ minHeight: '50px', maxHeight: '300px', width: '100%', overflow: 'hidden' }}>
                    <div id="chart" style={{ width: '100%' }}>
                        <ReactApexChart
                            options={chartOptions}
                            series={series}
                            type="bar"
                            height={250}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ChartProjectsByRegion;