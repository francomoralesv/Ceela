import { Bar, Doughnut, Line, Pie, PolarArea, Radar } from 'react-chartjs-2';

interface ChartComponentProps {
    title: string;
    chartData: any;
    chartType: 'Line' | 'Bar' | 'Pie' | 'Doughnut' | 'PolarArea' | 'Radar';
    className?: string;
    options?: any;
}

const ChartComponent: React.FC<ChartComponentProps> = ({
    title,
    chartData,
    chartType,
    className = "",
    options = {}
}) => {
    const defaultOptions = {
        maintainAspectRatio: true,
        responsive: true,
        plugins: {
            legend: {
                display: false
            }
        },
        layout: {
            padding: {
                top: 20,
                bottom: 20,
                left: 20,
                right: 20
            }
        }
    };

    const mergedOptions = { ...defaultOptions, ...options };

    const renderChart = () => {
        switch (chartType) {
            case 'Line':
                return <Line data={chartData} options={mergedOptions} />;
            case 'Bar':
                return <Bar data={chartData} options={mergedOptions} />;
            case 'Pie':
                return <Pie data={chartData} options={mergedOptions} />;
            case 'Doughnut':
                return <Doughnut data={chartData} options={mergedOptions} />;
            case 'PolarArea':
                return <PolarArea data={chartData} options={mergedOptions} />;
            case 'Radar':
                return <Radar data={chartData} options={mergedOptions} />;
            default:
                return null;
        }
    };
    return (
        <div className={className}>
            <div className="chart-container">
                <h3 className="title-chart">
                    {title}
                </h3>
                <div className="chart-wrapper" style={{  position: 'relative' }}>
                    {renderChart()}
                </div>
            </div>
            <style jsx>{`
                .chart-container {
                    background: #fff;
                    border-radius: 8px;
                    padding: 1rem;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                    height: 100%;
                    display: flex;
                    flex-direction: column;
                }
                .title-chart {
                    font-size: 1rem;
                    font-weight: 600;
                    margin-bottom: 1rem;
                    text-align: center;
                }
                .chart-wrapper {
                    flex: 1;
                    min-height: 300px;
                }
            `}</style>
        </div>
    );
};

export default ChartComponent;
