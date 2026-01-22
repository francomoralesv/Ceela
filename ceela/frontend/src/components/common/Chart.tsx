import React from 'react';
import { Bar } from 'react-chartjs-2';
import 'chart.js/auto';

interface ChartProps {
  title: string;
  data: {
    labels: string[];
    datasets: {
      label: string;
      data: number[];
      backgroundColor: string;
    }[];
  };
}

const Chart: React.FC<ChartProps> = ({ title, data }) => {
  return (
    <div className="chart-container">
      <h5 className="text-center">{title}</h5>
      <Bar data={data} />
    </div>
  );
};

export default Chart;
