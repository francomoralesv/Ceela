// pages/resumen-energia.js
import 'bootstrap/dist/css/bootstrap.min.css';
import { Cloud, Droplet, Flame, Snowflake, PlayCircle, Download } from 'lucide-react';
import ChartComponent from '../src/components/chart/ChartComponent';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend
);

import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';

declare module 'jspdf' {
  interface jsPDF {
    autoTable: typeof autoTable;
  }
}

import { notify } from '../src/utils/notify';
import { useEffect, useState, useMemo } from 'react';
import { useRouter } from 'next/router';

import FileDropzone from '../src/components/FileDropzone';
import { constantUrlApiEndpoint } from '../src/utils/constant-url-endpoint';
import EnergyAnalysis from '@/components/energy/EnergyAnalysis';

interface ChartDataItem {
  concepto: string;
  kwh_m2_ano: string | number;
  kwh_ano?: string | number;
  vsCasoBase?: string;
  nota?: string;

  // Valores “base” traídos del endpoint
  base_kwh_m2_ano?: number | null;
  base_kwh_ano?: number | null;
}

export default function ResumenEnergia(props: any) {
  const [consumoPrimario, setConsumoPrimario] = useState<ChartDataItem[]>([]);
  const [hrsDisconfort, setHrsDisconfort] = useState<ChartDataItem[]>([]);
  const [demandaData, setDemandaData] = useState<ChartDataItem[]>([]);
  const [co2eqData, setCo2eqData] = useState<any>({ total: 0, unidad: '[kg CO2eq]', comparacion: '0%' });
  const [showPercentage, setShowPercentage] = useState<boolean>(false);
  const [chartView, setChartView] = useState<'monthly' | 'annual'>('annual');
  const [recintoData, setRecintoData] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [loadingPdf, setLoadingPdf] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const router = useRouter();
  const { id: projectId } = router.query;
  const [useAttachedData, setUseAttachedData] = useState<boolean>(false);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [isAdmin, setIsAdmin] = useState<boolean>(false);

  useEffect(() => {
    const roleId = localStorage.getItem('role_id');
    setIsAdmin(roleId === '1');
  }, []);

  // ======== HELPERS DE FORMATO (2 decimales, coma decimal, miles con punto) ========
  const fmt = (v: any) => {
    if (v === null || v === undefined || v === '' || v === '-') return '-';
    const n = Number(String(v).replace(',', '.'));
    if (!isFinite(n)) return String(v);
    return n.toLocaleString('es-CL', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  };

  const fmtPct = (v: any) => {
    if (v === null || v === undefined || v === '' || v === '-') return '-';
    const n = Number(v);
    if (!isFinite(n)) return String(v);
    return `${n.toLocaleString('es-CL', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}%`;
  };

  const fmtPctStr = (s: any) => {
    if (s === null || s === undefined || s === '') return '-';
    const str = String(s).trim();
    if (!str.includes('%')) {
      // por si viene número sin el símbolo
      return fmt(str);
    }
    const num = Number(str.replace('%', '').replace(',', '.'));
    if (!isFinite(num)) return str;
    return `${num.toLocaleString('es-CL', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}%`;
  };

  // Para totales base desde API (suma de base_kwh_* por concepto)
  const baseApiTotals = useMemo(() => {
    const sum = (arr: ChartDataItem[], key: 'base_kwh_m2_ano' | 'base_kwh_ano') =>
      arr
        .filter(i => i.concepto !== 'Total' && typeof i[key] === 'number')
        .reduce((acc, it) => acc + Number(it[key] ?? 0), 0);

    return {
      demandaTotal_m2: sum(demandaData, 'base_kwh_m2_ano'),
      demandaTotal_ano: sum(demandaData, 'base_kwh_ano'),
      consumoTotal_m2: sum(consumoPrimario, 'base_kwh_m2_ano'),
      consumoTotal_ano: sum(consumoPrimario, 'base_kwh_ano'),
    };
  }, [demandaData, consumoPrimario]);

  // Para EnergyAnalysis: arrays “base” con nombres que espera
  const demandaDataBase = useMemo(() => {
    return demandaData.map(it => ({
      ...it,
      'Base kWh/m²·año': it.base_kwh_m2_ano ?? null,
      baseCaseKwh_ano: it.base_kwh_ano ?? null,
    }));
  }, [demandaData]);

  const consumoPrimarioBase = useMemo(() => {
    return consumoPrimario.map(it => ({
      ...it,
      'Base kWh/m²·año': it.base_kwh_m2_ano ?? null,
      baseCaseKwh_ano: it.base_kwh_ano ?? null,
    }));
  }, [consumoPrimario]);

  // Gráficos (igual que antes)
  const chartData = useMemo(() => {
    const labels = demandaData
      .filter((item: any) => item.concepto !== 'Total')
      .map((item: any) => item.concepto);

    const demandaValues = demandaData
      .filter((item: any) => item.concepto !== 'Total')
      .map((item: any) => Number(item.kwh_m2_ano as any || 0));

    const consumoValues = consumoPrimario
      .filter((item: any) => item.concepto !== 'Total')
      .map((item: any) => Number(item.kwh_m2_ano as any || 0));

    if (showPercentage) {
      const totalDemanda = demandaValues.reduce((sum: number, val: number) => sum + val, 0);
      const totalConsumo = consumoValues.reduce((sum: number, val: number) => sum + val, 0);

      return {
        labels,
        demandaValues: totalDemanda > 0 ? demandaValues.map((v: number) => (v / totalDemanda) * 100) : demandaValues,
        consumoValues: totalConsumo > 0 ? consumoValues.map((v: number) => (v / totalConsumo) * 100) : consumoValues,
        yAxisSuffix: '%',
        tooltipSuffix: '%',
        isPercentage: true
      };
    }

    return {
      labels,
      demandaValues,
      consumoValues,
      yAxisSuffix: ' kWh/m²·año',
      tooltipSuffix: ' kWh/m²·año',
      isPercentage: false
    };
  }, [demandaData, consumoPrimario, showPercentage]);

  // Fetch
  useEffect(() => {
    if (!projectId) return;
    const fetchResults = async () => {
      setLoading(true);
      setError(null);
      try {
        const token = localStorage.getItem('token');
        const url = `${constantUrlApiEndpoint}/calculation-results/projects/${projectId}`;
        const res = await fetch(url, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Accept': 'application/json'
          }
        });
        if (!res.ok) {
          if (res.status === 404) {
            setLoading(false);
            return;
          }
          throw new Error('Error al obtener resultados de cálculo');
        }
        const data = await res.json();

        if (data && data.final_indicators) {
          const fi = data.final_indicators;

          // DEMANDA (normal) + BASE desde endpoint
          const demandaArr: ChartDataItem[] = [
            {
              concepto: 'Calefacción',
              kwh_m2_ano: Number(fi.demanda_calefaccion_final).toFixed(2),
              kwh_ano: Number(fi.demanda_calefaccion_final2).toFixed(2),
              vsCasoBase: fmtPct((fi.demanda_calef_vs ?? 0) * 100),
              base_kwh_m2_ano: fi.base_demanda_calefaccion_final ?? null,
              base_kwh_ano: fi.base_demanda_calefaccion_final2 ?? null
            },
            {
              concepto: 'Refrigeración',
              kwh_m2_ano: Number(fi.demanda_ref_final).toFixed(2),
              kwh_ano: Number(fi.demanda_ref_final2).toFixed(2),
              vsCasoBase: fmtPct((fi.demanda_ref_vs ?? 0) * 100),
              // las claves base_* dependen de tu backend; aquí usas las que ya tenías en este archivo
              base_kwh_m2_ano: fi.base_demanda_ref_final ?? null,
              base_kwh_ano: fi.base_demanda_ref_final2 ?? null
            },
            {
              concepto: 'Iluminación',
              kwh_m2_ano: Number(fi.demanda_iluminacion_final).toFixed(2),
              kwh_ano: Number(fi.demanda_iluminacion_final2).toFixed(2),
              vsCasoBase: fmtPct((fi.demanda_iluminacion_vs ?? 0) * 100),
              base_kwh_m2_ano: fi.base_demanda_iluminacion_final ?? null,
              base_kwh_ano: fi.base_demanda_iluminacion_final2 ?? null
            },
            {
              concepto: 'ACS',
              kwh_m2_ano: Number(fi.demanda_acs_m2).toFixed(2),
              kwh_ano: Number(fi.demanda_acs).toFixed(2),
              vsCasoBase: fmtPct((fi.demanda_acs_vs_caso_base ?? 0) * 100),
              base_kwh_m2_ano: fi.base_demanda_ref_acs_final ?? null,
              base_kwh_ano: fi.base_demanda_ref_acs_final2 ?? null
            }
          ];

          const demandaBaseTotal_m2 = demandaArr.reduce((a, it) => a + (typeof it.base_kwh_m2_ano === 'number' ? it.base_kwh_m2_ano : 0), 0);
          const demandaBaseTotal_ano = demandaArr.reduce((a, it) => a + (typeof it.base_kwh_ano === 'number' ? it.base_kwh_ano : 0), 0);

          demandaArr.push({
            concepto: 'Total',
            kwh_m2_ano: (Number(fi.demanda_calefaccion_final) + Number(fi.demanda_ref_final) + Number(fi.demanda_iluminacion_final) + Number(fi.demanda_acs_m2)).toFixed(2),
            kwh_ano: (Number(fi.demanda_calefaccion_final2) + Number(fi.demanda_ref_final2) + Number(fi.demanda_iluminacion_final2) + Number(fi.demanda_acs)).toFixed(2),
            vsCasoBase: '-',
            base_kwh_m2_ano: demandaBaseTotal_m2,
            base_kwh_ano: demandaBaseTotal_ano
          });

          setDemandaData(demandaArr);

          // CONSUMO PRIMARIO (normal) + BASE desde endpoint
          const consumoArr: ChartDataItem[] = [
            {
              concepto: 'Calefacción',
              kwh_m2_ano: Number(fi.consumo_calefaccion_final).toFixed(2),
              kwh_ano: Number(fi.consumo_calefaccion_final2).toFixed(2),
              vsCasoBase: fmtPct((fi.consumo_calef_vs ?? 0) * 100),
              base_kwh_m2_ano: fi.base_consumo_calefaccion_final ?? null,
              base_kwh_ano: fi.base_consumo_calefaccion_final2 ?? null
            },
            {
              concepto: 'Refrigeración',
              kwh_m2_ano: Number(fi.consumo_refrigeracion_final).toFixed(2),
              kwh_ano: Number(fi.consumo_refrigeracion_final2).toFixed(2),
              vsCasoBase: fmtPct((fi.consumo_ref_vs ?? 0) * 100),
              base_kwh_m2_ano: fi.base_consumo_refrigeracion_final ?? null,
              base_kwh_ano: fi.base_consumo_refrigeracion_final2 ?? null
            },
            {
              concepto: 'Iluminación',
              kwh_m2_ano: Number(fi.consumo_iluminacion_final).toFixed(2),
              kwh_ano: Number(fi.consumo_iluminacion_final2).toFixed(2),
              vsCasoBase: fmtPct((fi.consumo_iluminacion_vs ?? 0) * 100),
              base_kwh_m2_ano: fi.base_consumo_iluminacion_final ?? null,
              base_kwh_ano: fi.base_consumo_iluminacion_final2 ?? null
            },
            {
              concepto: 'ACS',
              kwh_m2_ano: Number(fi.consumo_acs_m2).toFixed(2),
              kwh_ano: Number(fi.consumo_acs).toFixed(2),
              vsCasoBase: fmtPct(fi.consumo_acs_vs_caso_base ?? 0),
              base_kwh_m2_ano: fi.base_consumo_acs_final ?? null,
              base_kwh_ano: fi.base_consumo_acs_final2 ?? null
            }
          ];

          const consumoBaseTotal_m2 = consumoArr.reduce((a, it) => a + (typeof it.base_kwh_m2_ano === 'number' ? it.base_kwh_m2_ano : 0), 0);
          const consumoBaseTotal_ano = consumoArr.reduce((a, it) => a + (typeof it.base_kwh_ano === 'number' ? it.base_kwh_ano : 0), 0);

          consumoArr.push({
            concepto: 'Total',
            kwh_m2_ano: (Number(fi.consumo_calefaccion_final) + Number(fi.consumo_refrigeracion_final) + Number(fi.consumo_iluminacion_final) + Number(fi.consumo_acs_m2)).toFixed(2),
            kwh_ano: (Number(fi.consumo_calefaccion_final2) + Number(fi.consumo_refrigeracion_final2) + Number(fi.consumo_iluminacion_final2) + Number(fi.consumo_acs)).toFixed(2),
            vsCasoBase: '-',
            base_kwh_m2_ano: consumoBaseTotal_m2,
            base_kwh_ano: consumoBaseTotal_ano
          });

          setConsumoPrimario(consumoArr);

          // HRS DISCONFORT (normal)
          setHrsDisconfort([
            { concepto: 'Calefacción',   kwh_m2_ano: Number(fi.disconfort_calef).toFixed(2) },
            { concepto: 'Refrigeración', kwh_m2_ano: Number(fi.disconfort_ref).toFixed(2) },
            { concepto: 'Total',         kwh_m2_ano: Number(fi.disconfort_total).toFixed(2) },
            { concepto: 'Ahorro versus caso base', kwh_m2_ano: fmtPct((fi.disconfort_vs ?? 0) * 100), nota: '[%]' },
          ]);

          setCo2eqData({
            total: Number(fi.co2_eq_total).toFixed(2),
            unidad: '[kg CO2eq/KWh]',
            comparacion: fmtPct((fi.co2_eq_vs_caso_base ?? 0) * 100),
          });

          if (data.result_by_enclosure) setRecintoData(data.result_by_enclosure);
          else setRecintoData([]);
        } else {
          setCo2eqData({ total: 0, unidad: '[kgCO2eq/KWh]', comparacion: '0%' });
          setDemandaData([]);
          setConsumoPrimario([]);
          setHrsDisconfort([]);
          setRecintoData([]);
        }
      } catch (err: any) {
        const m = err?.message || 'Error inesperado';
        setError(m);
        notify(m, 'error');
      } finally {
        setLoading(false);
      }
    };
    fetchResults();
  }, [projectId]);

  const handleFileAccepted = (files: File[]) => setUploadedFiles(files);

  // Mantener la vista incluso si hay error; la notificación ya informa al usuario

  return (
    <div className="container my-4">
      <h1 className="mb-3">Resumen de Energía</h1>

      {/* Botones */}
      <div className="d-flex align-items-center mb-3" style={{ gap: 16 }}>
        <button
          type="button"
          className="btn d-flex align-items-center"
          style={{ backgroundColor: 'orange', color: 'white', fontWeight: 'bold' }}
          disabled={loading || isAdmin}
          onClick={async () => {
            if (!projectId) return;
            setLoading(true);
            setError(null);
            try {
              if (useAttachedData) {
                if (!uploadedFiles || uploadedFiles.length === 0) {
                  notify('Debe adjuntar al menos un archivo antes de calcular.', 'error');
                  setLoading(false);
                  return;
                }
                const formData = new FormData();
                const token = localStorage.getItem('token');
                uploadedFiles.forEach(file => formData.append('files', file));
                const uploadRes = await fetch(`${process.env.NEXT_PUBLIC_API_ENDPOINT}/calculator/upload/${projectId}`, {
                  method: 'POST',
                  body: formData,
                  headers: { Authorization: `Bearer ${token}` },
                });
                if (!uploadRes.ok) {
                  const errMsg = await uploadRes.text();
                  throw new Error('Error al subir el archivo: ' + errMsg);
                }
              }

              const v2res = await fetch(`/api/calculate_v2/${projectId}?force_data=${useAttachedData ? 'true' : 'false'}`, {
                headers: { Authorization: `Bearer ${localStorage.getItem('token') || ''}` }
              });
              if (!v2res.ok) {
                let msg = 'Error al ejecutar cálculo v2';
                try {
                  const errJson = await v2res.json();
                  msg = errJson?.error || errJson?.details?.detail || msg;
                } catch {}
                throw new Error(msg);
              }

              const token = localStorage.getItem('token');
              const res = await fetch(`/api/calculate_v3/${projectId}`, {
                headers: { Authorization: `Bearer ${token}` }
              });
              if (!res.ok) throw new Error('Error al obtener resultados de cálculo');
              const data = await res.json();

              const fi = data.final_indicators;

              const demandaArrBtn: ChartDataItem[] = [
                {
                  concepto: 'Calefacción',
                  kwh_m2_ano: Number(fi.demanda_calefaccion_final).toFixed(2),
                  kwh_ano: Number(fi.demanda_calefaccion_final2).toFixed(2),
                  vsCasoBase: fmtPct((fi.demanda_calef_vs ?? 0) * 100),
                  base_kwh_m2_ano: fi.base_demanda_calefaccion_final ?? null,
                  base_kwh_ano: fi.base_demanda_calefaccion_final2 ?? null
                },
                {
                  concepto: 'Refrigeración',
                  kwh_m2_ano: Number(fi.demanda_ref_final).toFixed(2),
                  kwh_ano: Number(fi.demanda_ref_final2).toFixed(2),
                  vsCasoBase: fmtPct((fi.demanda_ref_vs ?? 0) * 100),
                  base_kwh_m2_ano: fi.base_demanda_ref_final ?? null,
                  base_kwh_ano: fi.base_demanda_ref_final2 ?? null
                },
                {
                  concepto: 'Iluminación',
                  kwh_m2_ano: Number(fi.demanda_iluminacion_final).toFixed(2),
                  kwh_ano: Number(fi.demanda_iluminacion_final2).toFixed(2),
                  vsCasoBase: fmtPct((fi.demanda_iluminacion_vs ?? 0) * 100),
                  base_kwh_m2_ano: fi.base_demanda_iluminacion_final ?? null,
                  base_kwh_ano: fi.base_demanda_iluminacion_final2 ?? null
                },
                {
                  concepto: 'ACS',
                  kwh_m2_ano: Number(fi.demanda_acs_m2).toFixed(2),
                  kwh_ano: Number(fi.demanda_acs).toFixed(2),
                  vsCasoBase: fmtPct((fi.demanda_acs_vs_caso_base ?? 0) * 100),
                  base_kwh_m2_ano: fi.base_demanda_ref_acs_final ?? null,
                  base_kwh_ano: fi.base_demanda_ref_acs_final2 ?? null
                }
              ];
              const demandaBaseTotal_m2_btn = demandaArrBtn.reduce((a, it) => a + (typeof it.base_kwh_m2_ano === 'number' ? it.base_kwh_m2_ano : 0), 0);
              const demandaBaseTotal_ano_btn = demandaArrBtn.reduce((a, it) => a + (typeof it.base_kwh_ano === 'number' ? it.base_kwh_ano : 0), 0);
              demandaArrBtn.push({
                concepto: 'Total',
                kwh_m2_ano: (Number(fi.demanda_calefaccion_final) + Number(fi.demanda_ref_final) + Number(fi.demanda_iluminacion_final) + Number(fi.demanda_acs_m2)).toFixed(2),
                kwh_ano: (Number(fi.demanda_calefaccion_final2) + Number(fi.demanda_ref_final2) + Number(fi.demanda_iluminacion_final2) + Number(fi.demanda_acs)).toFixed(2),
                vsCasoBase: '-',
                base_kwh_m2_ano: demandaBaseTotal_m2_btn,
                base_kwh_ano: demandaBaseTotal_ano_btn
              });
              setDemandaData(demandaArrBtn);

              const consumoArrBtn: ChartDataItem[] = [
                {
                  concepto: 'Calefacción',
                  kwh_m2_ano: Number(fi.consumo_calefaccion_final).toFixed(2),
                  kwh_ano: Number(fi.consumo_calefaccion_final2).toFixed(2),
                  vsCasoBase: fmtPct((fi.consumo_calef_vs ?? 0) * 100),
                  base_kwh_m2_ano: fi.base_consumo_calefaccion_final ?? null,
                  base_kwh_ano: fi.base_consumo_calefaccion_final2 ?? null
                },
                {
                  concepto: 'Refrigeración',
                  kwh_m2_ano: Number(fi.consumo_refrigeracion_final).toFixed(2),
                  kwh_ano: Number(fi.consumo_refrigeracion_final2).toFixed(2),
                  vsCasoBase: fmtPct((fi.consumo_ref_vs ?? 0) * 100),
                  base_kwh_m2_ano: fi.base_consumo_refrigeracion_final ?? null,
                  base_kwh_ano: fi.base_consumo_refrigeracion_final2 ?? null
                },
                {
                  concepto: 'Iluminación',
                  kwh_m2_ano: Number(fi.consumo_iluminacion_final).toFixed(2),
                  kwh_ano: Number(fi.consumo_iluminacion_final2).toFixed(2),
                  vsCasoBase: fmtPct((fi.consumo_iluminacion_vs ?? 0) * 100),
                  base_kwh_m2_ano: fi.base_consumo_iluminacion_final ?? null,
                  base_kwh_ano: fi.base_consumo_iluminacion_final2 ?? null
                },
                {
                  concepto: 'ACS',
                  kwh_m2_ano: Number(fi.consumo_acs_m2).toFixed(2),
                  kwh_ano: Number(fi.consumo_acs).toFixed(2),
                  vsCasoBase: fmtPct(fi.consumo_acs_vs_caso_base ?? 0),
                  base_kwh_m2_ano: fi.base_consumo_acs_final ?? null,
                  base_kwh_ano: fi.base_consumo_acs_final2 ?? null
                }
              ];
              const consumoBaseTotal_m2_btn = consumoArrBtn.reduce((a, it) => a + (typeof it.base_kwh_m2_ano === 'number' ? it.base_kwh_m2_ano : 0), 0);
              const consumoBaseTotal_ano_btn = consumoArrBtn.reduce((a, it) => a + (typeof it.base_kwh_ano === 'number' ? it.base_kwh_ano : 0), 0);
              consumoArrBtn.push({
                concepto: 'Total',
                kwh_m2_ano: (Number(fi.consumo_calefaccion_final) + Number(fi.consumo_refrigeracion_final) + Number(fi.consumo_iluminacion_final) + Number(fi.consumo_acs_m2)).toFixed(2),
                kwh_ano: (Number(fi.consumo_calefaccion_final2) + Number(fi.consumo_refrigeracion_final2) + Number(fi.consumo_iluminacion_final2) + Number(fi.consumo_acs)).toFixed(2),
                vsCasoBase: '-',
                base_kwh_m2_ano: consumoBaseTotal_m2_btn,
                base_kwh_ano: consumoBaseTotal_ano_btn
              });
              setConsumoPrimario(consumoArrBtn);

              setHrsDisconfort([
                { concepto: 'Calefacción',   kwh_m2_ano: Number(fi.disconfort_calef).toFixed(2) },
                { concepto: 'Refrigeración', kwh_m2_ano: Number(fi.disconfort_ref).toFixed(2) },
                { concepto: 'Total',         kwh_m2_ano: Number(fi.disconfort_total).toFixed(2) },
                { concepto: 'Ahorro versus caso base', kwh_m2_ano: fmtPct((fi.disconfort_vs ?? 0) * 100), nota: '[%]' },
              ]);

              setCo2eqData({
                total: Number(fi.co2_eq_total).toFixed(2),
                unidad: '[kg CO2eq/KWh]',
                comparacion: fmtPct((fi.co2_eq_vs_caso_base ?? 0) * 100),
              });

              if (data.result_by_enclosure) setRecintoData(data.result_by_enclosure);
              else setRecintoData([]);

            } catch (err: any) {
              const m = err?.message || 'Error inesperado';
              setError(m);
              notify(m, 'error');
            } finally {
              setLoading(false);
            }
          }}
        >
          {loading ? (
            <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
          ) : (
            <PlayCircle size={20} style={{ marginRight: 8 }} />
          )}
          Calcular
        </button>

        {/* Botón PDF */}
        <button
          type="button"
          className="btn btn-primary d-flex align-items-center"
          style={{ fontWeight: 'bold' }}
          disabled={loadingPdf || demandaData.length === 0}
          onClick={async () => {
            if (demandaData.length === 0) return;
            setLoadingPdf(true);
            try {
              const doc = new jsPDF();
              const pageWidth = doc.internal.pageSize.getWidth();
              const margin = 15;
              let yPos = 20;

              // Helper para formatear celdas en PDF (números y porcentajes)
              const fmtCell = (val: any) => {
                if (val === null || val === undefined) return '';
                const s = String(val).trim();
                if (s.endsWith('%')) {
                  return fmtPctStr(s);
                }
                const n = Number(s.replace(',', '.'));
                if (isFinite(n)) return fmt(n);
                return s;
              };

              doc.setFontSize(18);
              doc.text('Reporte de Análisis Energético', pageWidth / 2, yPos, { align: 'center' });
              yPos += 15;
              doc.setFontSize(10);
              doc.text(`Generado el: ${new Date().toLocaleDateString('es-CL')}`, pageWidth - margin, 10, { align: 'right' });

              const addTable = (title: string, headers: string[][], data: any[], columns: string[]) => {
                if (yPos > 250) {
                  doc.addPage();
                  yPos = 20;
                }
                doc.setFontSize(12);
                doc.text(title, margin, yPos);
                yPos += 8;
                autoTable(doc, {
                  startY: yPos,
                  head: headers,
                  body: data.map(row => columns.map(col => fmtCell(row[col]))),
                  margin: { left: margin, right: margin },
                  styles: { fontSize: 8, cellPadding: 2 },
                  headStyles: { fillColor: [41, 128, 185], textColor: 255, fontStyle: 'bold' },
                  alternateRowStyles: { fillColor: 245 }
                });
                yPos = (doc as any).lastAutoTable.finalY + 10;
              };

              addTable(
                'Demanda Energética',
                [['Concepto', 'kWh/m²-año', 'kWh-año', '% vs Caso Base']],
                demandaData,
                ['concepto', 'kwh_m2_ano', 'kwh_ano', 'vsCasoBase']
              );

              addTable(
                'Consumo de Energía Primaria',
                [['Concepto', 'kWh/m²-año', 'kWh-año', '% vs Caso Base']],
                consumoPrimario,
                ['concepto', 'kwh_m2_ano', 'kwh_ano', 'vsCasoBase']
              );

              addTable(
                'Horas de Disconfort Térmico',
                [['Concepto', 'Horas/año', 'Nota']],
                hrsDisconfort,
                ['concepto', 'hrs_ano', 'nota'] // (se mantiene tal cual tus columnas)
              );

              doc.setFontSize(12);
              doc.text('Emisiones de CO2 Equivalente', margin, yPos);
              yPos += 8;
              doc.text(`Total: ${fmt(co2eqData.total)} ${co2eqData.unidad} (${fmtPctStr(co2eqData.comparacion)} vs caso base)`, margin + 5, yPos);
              yPos += 10;

              doc.save(`reporte-energetico-${new Date().toISOString().split('T')[0]}.pdf`);
            } catch (err) {
              console.error('Error al generar el PDF:', err);
              notify('Error al generar el reporte PDF', 'error');
            } finally {
              setLoadingPdf(false);
            }
          }}
        >
          {loadingPdf ? (
            <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
          ) : (
            <Download size={20} style={{ marginRight: 8 }} />
          )}
          Descargar Reporte PDF
        </button>
      </div>

      <EnergyAnalysis
        demandaData={demandaData}
        consumoPrimario={consumoPrimario}
        demandaDataBase={demandaDataBase}
        consumoPrimarioBase={consumoPrimarioBase}
        showPercentage={showPercentage}
      />

      {/* TABLA DEMANDA */}
      <div className="row">
        <div className="col-12 col-lg-6 mb-4">
          <div className="card h-100 border">
            <div className="card-header bg-white border-bottom py-3">
              <div className="d-flex align-items-center">
                <Flame className="me-2 text-warning" size={20} />
                <h5 className="mb-0 fw-semibold text-dark">Demanda Energética</h5>
              </div>
            </div>
            <div className="card-body p-0">
              <div className="table-responsive">
                <table className="table table-borderless mb-0">
                  <thead>
                    <tr className="border-bottom border-200">
                      <th rowSpan={2} className="text-uppercase text-900 fw-medium fs--1 text-center align-middle py-3 ps-3">Concepto</th>
                    </tr>
                    <tr className="border-bottom border-200">
                      <th className="text-uppercase text-900 fw-medium fs--1 text-center py-3">[kWh/m²·año]</th>
                      <th className="text-uppercase text-900 fw-medium fs--1 text-center py-3">[kWh/año]</th>
                      <th className="text-uppercase text-900 fw-medium fs--1 text-center py-3">Base kWh/m²·año</th>
                      <th className="text-uppercase text-900 fw-medium fs--1 text-center py-3">Base kWh/año</th>
                      <th className="text-uppercase text-900 fw-medium fs--1 text-center py-3">% vs Caso Base</th>
                    </tr>
                  </thead>
                  <tbody>
                    {demandaData.map((item:any, index:number) => (
                      <tr
                        key={index}
                        className={`border-bottom border-200 ${item.concepto === 'Total' ? 'bg-100 fw-bold' : 'bg-white'}`}
                      >
                        <td className="text-nowrap ps-3 py-2">{item.concepto}</td>
                        <td className="text-end font-mono text-900 py-2">{fmt(item.kwh_m2_ano)}</td>
                        <td className="text-end font-mono text-900 py-2">{fmt(item.kwh_ano)}</td>
                        {/* Base desde API con formato */}
                        <td className="text-end font-mono text-600 py-2">
                          {fmt(item.concepto === 'Total' ? baseApiTotals.demandaTotal_m2 : item.base_kwh_m2_ano)}
                        </td>
                        <td className="text-end font-mono text-600 py-2">
                          {fmt(item.concepto === 'Total' ? baseApiTotals.demandaTotal_ano : item.base_kwh_ano)}
                        </td>
                        <td className="text-end font-mono fw-semi-bold text-900 py-2">
                          {fmtPctStr(item.vsCasoBase)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        {/* TABLA CONSUMO */}
        <div className="col-12 col-lg-6 mb-4">
          <div className="card h-100 border">
            <div className="card-header bg-white border-bottom py-3">
              <div className="d-flex align-items-center">
                <Droplet className="me-2  text-danger" size={20} />
                <h5 className="mb-0 fw-semibold text-dark">Consumo Energía Primaria</h5>
              </div>
            </div>
            <div className="card-body p-0">
              <div className="table-responsive">
                <table className="table table-borderless mb-0">
                  <thead>
                    <tr className="border-bottom border-200">
                      <th rowSpan={2} className="text-uppercase text-900 fw-medium fs--1 text-center align-middle py-3 ps-3">Concepto</th>
                    </tr>
                    <tr className="border-bottom border-200">
                      <th className="text-uppercase text-900 fw-medium fs--1 text-center py-3">[kWh/m²·año]</th>
                      <th className="text-uppercase text-900 fw-medium fs--1 text-center py-3">[kWh/año]</th>
                      <th className="text-uppercase text-900 fw-medium fs--1 text-center py-3">Base kWh/m²·año</th>
                      <th className="text-uppercase text-900 fw-medium fs--1 text-center py-3">Base kWh/año</th>
                      <th className="text-uppercase text-900 fw-medium fs--1 text-center py-3">% vs Caso Base</th>
                    </tr>
                  </thead>
                  <tbody>
                    {consumoPrimario.map((item: any, idx: number) => (
                      <tr
                        key={idx}
                        className={`border-bottom border-200 ${item.concepto === 'Total' ? 'bg-100 fw-bold' : 'bg-white'}`}
                      >
                        <td className="text-nowrap ps-3 py-2">{item.concepto}</td>
                        <td className="text-end font-mono text-900 py-2">{fmt(item.kwh_m2_ano)}</td>
                        <td className="text-end font-mono text-900 py-2">{fmt(item.kwh_ano)}</td>
                        {/* Base desde API con formato */}
                        <td className="text-end font-mono text-600 py-2">
                          {fmt(item.concepto === 'Total' ? baseApiTotals.consumoTotal_m2 : item.base_kwh_m2_ano)}
                        </td>
                        <td className="text-end font-mono text-600 py-2">
                          {fmt(item.concepto === 'Total' ? baseApiTotals.consumoTotal_ano : item.base_kwh_ano)}
                        </td>
                        <td className="text-end font-mono fw-semi-bold text-900 py-2">
                          {fmtPctStr(item.vsCasoBase)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        {/* Hrs Disconfort */}
        <div className="col-12 col-lg-6 mb-4">
          <div className="card h-100 border">
            <div className="card-header bg-white border-bottom py-3">
              <div className="d-flex align-items-center">
                <Snowflake className="me-2 text-primary" size={20} />
                <h5 className="mb-0 fw-semibold text-dark">Horas de Disconfort Térmico</h5>
              </div>
            </div>
            <div className="card-body p-0">
              <div className="table-responsive">
                <table className="table table-borderless mb-0">
                  <thead>
                    <tr className="border-bottom border-200">
                      <th className="text-uppercase text-900 fw-medium fs--1 ps-3 py-3">Concepto</th>
                      <th className="text-uppercase text-900 fw-medium fs--1 text-end pe-3 py-3">[horas/año]</th>
                    </tr>
                  </thead>
                  <tbody>
                    {hrsDisconfort.map((item: any, idx: number) => (
                      <tr
                        key={idx}
                        className={`border-bottom border-200 ${item.concepto === 'Total' ? 'bg-100 fw-bold' : 'bg-white'}`}
                      >
                        <td className="ps-3 py-2">{item.concepto}</td>
                        <td className="text-end pe-3 py-2">
                          <div className="d-flex flex-column align-items-end">
                            <span className="font-mono text-900">
                              {fmt(item.kwh_m2_ano)}
                            </span>
                            {item.nota && <small className="text-500 font-sans-serif">{item.nota}</small>}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        {/* CO2eq */}
        <div className="col-12 col-lg-6 mb-4">
          <div className="card h-100 border">
            <div className="card-header bg-white border-bottom py-3">
              <div className="d-flex align-items-center">
                <Cloud className="me-2 text-info" size={20} />
                <h5 className="mb-0 fw-semibold text-dark">Emisiones de CO₂ Equivalente</h5>
              </div>
            </div>
            <div className="card-body p-0">
              <div className="table-responsive">
                <table className="table table-borderless mb-0">
                  <thead>
                    <tr className="border-bottom border-200">
                      <th className="text-uppercase text-900 fw-medium fs--1 ps-3 py-3">Concepto</th>
                      <th className="text-uppercase text-900 fw-medium fs--1 text-center py-3">Valor</th>
                      <th className="text-uppercase text-900 fw-medium fs--1 text-center py-3">Ahorro vs Caso Base</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-bottom border-200">
                      <td className="ps-3 py-2">Emisiones Totales</td>
                      <td className="text-center font-mono text-900 py-2">
                        {fmt(co2eqData.total)} {co2eqData.unidad}
                      </td>
                      <td className="text-center font-mono text-900 py-2">
                        {fmtPctStr(co2eqData.comparacion)}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recintos */}
      <div className="row">
        <div className="col-12">
          <div className="card">
            <div className="card-header ">
              <strong>Datos del Recinto</strong>
            </div>
            <div className="card-body p-2">
              <table className="table table-bordered table-sm mb-0">
                <thead>
                  <tr className="table-light text-center">
                    <th>#</th>
                    <th>Recinto</th>
                    <th>Perfil de Ocupación</th>
                    <th>Superficie [m2]</th>
                  </tr>
                </thead>
                <tbody>
                  {recintoData.length > 0 ? (
                    recintoData.map((recinto, idx) => (
                      <tr key={recinto.enclosure_id || idx} className="text-center">
                        <td>{recinto.enclosure_id}</td>
                        <td>{recinto.nombre_recinto || recinto.name_enclosure || '-'}</td>
                        <td>{recinto.perfil_uso || recinto.usage_profile_name || '-'}</td>
                        <td>{recinto.superficie != null ? Number(recinto.superficie).toLocaleString('es-CL', { maximumFractionDigits: 2, minimumFractionDigits: 2 }) : '-'}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={4} className="text-center">No hay datos de recintos</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
