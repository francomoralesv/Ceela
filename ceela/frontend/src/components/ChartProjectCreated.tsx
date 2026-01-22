import { useApi } from "@/hooks/useApi";
import { ApexOptions } from "apexcharts";
import dynamic from "next/dynamic";
import React, { useEffect, useState } from "react";
import Title from "./Title";
import Card from "./common/Card";
import axios from "axios";
import { constantUrlApiEndpoint } from "@/utils/constant-url-endpoint";

const ReactApexChart = dynamic(() => import("react-apexcharts"), {
  ssr: false,
});

interface Project {
  created_at?: string;
}

interface ProjectsResponse {
  projects: Project[];
}

const months = [
  "Ene",
  "Feb",
  "Mar",
  "Abr",
  "May",
  "Jun",
  "Jul",
  "Ago",
  "Sep",
  "Oct",
  "Nov",
  "Dic",
];

const ChartProjectCreated: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [chartData, setChartData] = useState<number[]>(new Array(12).fill(0));
  const [loading, setLoading] = useState(true);
  const [selectedYear, setSelectedYear] = useState<number>(
    new Date().getFullYear()
  );

  const api = useApi();
  const filterProjectsByYear = (year: number) => {
    const counts = new Array(12).fill(0);
    projects.forEach((project) => {
      if (project.created_at) {
        const date = new Date(project.created_at);
        if (date.getFullYear() === year) {
          counts[date.getMonth()]++;
        }
      }
    });
    setChartData(counts);
  };

  useEffect(() => {
    const fetchData = async () => {
      const token = localStorage.getItem("token");
      if (!token) return;

      try {
        await axios
          .get(`${constantUrlApiEndpoint}/user/projects/`, {
            params: {
              limit: 999999,
              num_pag: 1,
            },
            headers: {
              accept: "application/json",
              Authorization: `Bearer ${token}`,
            },
          })
          .then((response) => setProjects(response.data.projects))
          .catch((error) => console.error("Error fetching projects:", error))
          .finally(() => setLoading(false));
      } catch (error) {
        console.error("Error al crear el detalle:", error);
      }
    };

    fetchData();
  }, []);

  useEffect(() => {
    filterProjectsByYear(selectedYear);
  }, [projects, selectedYear]);

  const chartOptions: ApexOptions = {
    chart: {
      type: "bar",
      stacked: false,
      toolbar: {
        show: false,
      },
      animations: {
        enabled: true,
        speed: 800,
        animateGradually: {
          enabled: true,
          delay: 150,
        },
        dynamicAnimation: {
          enabled: true,
          speed: 350,
        },
      },
    },

    plotOptions: {
      bar: {
        borderRadius: 2,
        columnWidth: "40%",
        distributed: true,
      },
    },
    annotations: {
      yaxis: [
        {
          y: 0,
          // borderColor: '#64748B',
          opacity: 0.2,
          // borderWidth: 1,
        },
      ],
    },
    colors: ["#00B4D8", "#00B4D8", "#00B4D8", "#00B4D8", "#00B4D8"],

    grid: {
      show: false,
    },
    markers: {
      size: 5,
      colors: ["#00B4D8", "#00B4D8", "#00B4D8", "#00B4D8", "#00B4D8"],
      strokeColors: "#fff",
      strokeWidth: 2,
      hover: {
        size: 7,
      },
    },
    xaxis: {
      categories: months,
      axisBorder: {
        show: false,
      },
      axisTicks: {
        show: false,
      },
      labels: {
        style: {
          fontSize: "12px",
          fontWeight: 500,
          // colors: '#64748B',
          fontFamily: "Outfit, sans-serif",
        },
        offsetY: 5,
      },
    },
    yaxis: {
      show: true,
      labels: {
        style: {
          fontSize: "12px",
          // fontWeight: 500,
          // colors: '#64748B',
          fontFamily: "Noto Sans, sans-serif",
        },
        formatter: function (value) {
          return Math.round(value).toString();
        },
      },
      tickAmount: 3,
      min: 0,
      max: (max) => {
        const roundedMax = Math.ceil(max / 3) * 3;
        return roundedMax > 0 ? roundedMax : 3;
      },
    },
    dataLabels: {
      enabled: false,
    },
    legend: {
      show: false,
    },
    tooltip: {
      style: {
        fontSize: "12px",
        fontFamily: "Outfit, sans-serif",
      },
      y: {
        formatter: function (value) {
          return value + " proyectos";
        },
      },
      marker: {
        show: false,
      },
    },
  };

  const series = [
    {
      name: "Proyectos",
      data: chartData,
      type: "bar",
    },
  ];

  const availableYears = [2021, 2022, 2023, 2024, new Date().getFullYear()];

  if (loading) {
    return <div>Loading chart...</div>;
  }

  return (
    <Card>
      <div className="card-header">
        <Title text="Proyectos creados" />
        <div className="header-top d-flex justify-content-between align-items-center">
          <div>
            <select
              value={selectedYear}
              onChange={(e) => setSelectedYear(Number(e.target.value))}
              className="form-select"
            >
              {availableYears.map((year) => (
                <option key={year} value={year}>
                  {year}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>
      <div className="card-body mt-0 pt-0">
        <div
          style={{
            minHeight: "120px",
            maxHeight: "220px",
            width: "100%",
            overflow: "hidden",
          }}
        >
          <div id="chart">
            <ReactApexChart
              options={chartOptions}
              series={series}
              type="line"
              height={100}
              width="100%"
            />
          </div>
        </div>
      </div>
    </Card>
  );
};

export default ChartProjectCreated;
