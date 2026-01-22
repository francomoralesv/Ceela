import ReactECharts from 'echarts-for-react';
import React, { useEffect, useRef, useState } from 'react';
import { constantUrlApiEndpoint } from "../../utils/constant-url-endpoint";
import ModalCreate from './ModalCreate';
import CustomButton from "@/components/common/CustomButton";
import { useApi } from "@/hooks/useApi";
import { notify } from '@/utils/notify';

interface ScheduleData {
  [key: string]: number | string | null;
}

interface HoursRange {
  start: string;
  end: string;
}

const ProfileSchedules: React.FC<{ onUpdate?: () => void }> = ({ onUpdate }) => {
  const [data, setData] = useState<ScheduleData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [perfilId, setPerfilId] = useState<number | null>(null);
  const [typeSelect, setTypeSelect] = useState<string>('usuarios');
  const [tipologia, setTipologia] = useState<string>('');
  const [hoursRange, setHoursRange] = useState<HoursRange>({ start: '08:00', end: '18:00' });
  const [isEditingHours, setIsEditingHours] = useState<boolean>(false);
  const [tempHours, setTempHours] = useState<HoursRange>({ start: '08:00', end: '18:00' });
  const chartRef = useRef<any>(null);
  const api = useApi();

  const format24h = (raw: string | number): string => {
    let hours: number;
    let minutes: number = 0;
    if (typeof raw === 'string') {
      if (raw.includes(':')) {
        const [h, m] = raw.split(':');
        hours = parseInt(h, 10);
        minutes = parseInt(m, 10);
      } else {
        hours = parseInt(raw, 10);
      }
    } else {
      hours = raw;
    }
    const hh = hours.toString().padStart(2, '0');
    const mm = minutes.toString().padStart(2, '0');
    return `${hh}:${mm}`;
  };

  const fetchWorkingHours = async () => {
    if (perfilId === null) return;
    const token = localStorage.getItem("token");
    try {
      const res = await fetch(
        `${constantUrlApiEndpoint}/user/enclosure-typing/${perfilId}`,
        { headers: { accept: 'application/json', Authorization: `Bearer ${token}` } }
      );
      const result = await res.json();
      const internalLoad = result.building_conditions?.find((bc: any) => bc.type === 'internal_loads');
      const inicioRaw = internalLoad?.details?.horario?.laboral?.inicio;
      const finRaw = internalLoad?.details?.horario?.laboral?.fin;
      setHoursRange({
        start: inicioRaw != null ? format24h(inicioRaw) : '08:00',
        end: finRaw != null ? format24h(finRaw) : '18:00',
      });
    } catch (error) {
      console.error("Error fetching working hours", error);
    }
  };

  useEffect(() => {
    const storedId = localStorage.getItem("perfil_id");
    if (storedId) setPerfilId(parseInt(storedId, 10));
  }, []);

  useEffect(() => {
    if (perfilId === null) return;
    const token = localStorage.getItem("token");
    const fetchInfo = async () => {
      try {
        const response = await fetch(
          `${constantUrlApiEndpoint}/user/enclosure-typing/${perfilId}`,
          { headers: { accept: 'application/json', Authorization: `Bearer ${token}` } }
        );
        const result = await response.json();
        setTipologia(result.name);
        const internalLoad = result.building_conditions?.find((bc: any) => bc.type === 'internal_loads');
        const inicioRaw = internalLoad?.details?.horario?.laboral?.inicio;
        const finRaw = internalLoad?.details?.horario?.laboral?.fin;
        setHoursRange({
          start: inicioRaw != null ? format24h(inicioRaw) : '08:00',
          end: finRaw != null ? format24h(finRaw) : '18:00',
        });
      } catch (error) {
        console.error("Error fetching tipología y horas", error);
      }
    };
    fetchInfo();
  }, [perfilId]);

  useEffect(() => {
    if (perfilId === null) return;
    const token = localStorage.getItem("token");
    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await fetch(
          `${constantUrlApiEndpoint}/${typeSelect}/schedule/${perfilId}`,
          { headers: { accept: 'application/json', Authorization: `Bearer ${token}` } }
        );
        const result = await response.json();
        setData(result);
      } catch (error) {
        console.error("Error fetching schedule data", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [typeSelect, perfilId]);

  const hours = Array.from({ length: 24 }, (_, i) => (i + 1).toString());
  const values = data ? hours.map((hour, i) => {
    const currentHour = i + 1;
    const startHour = parseInt(hoursRange.start.split(':')[0]);
    const endHour = hoursRange.end === '24:00' ? 24 : parseInt(hoursRange.end.split(':')[0]);
    const endMin = hoursRange.end === '24:00' ? 0 : parseInt(hoursRange.end.split(':')[1]);
    // Set value to 0 if outside working hours
    if (
      currentHour < startHour ||
      (currentHour > endHour) ||
      (currentHour === endHour && endMin === 0 && hoursRange.end !== '24:00')
    ) {
      return 0;
    }
    return data[`hour_${currentHour}`] ?? 0;
  }) : [];

  const option = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: hours, name: 'Horas' },
    yAxis: { type: 'value', name: 'Horas de uso', axisLabel: { formatter: '{value}%' } },
    series: [{
      name: typeSelect,
      type: 'bar',
      data: values,
      barMinHeight: 10,
      itemStyle: {
        color: (params: any) => {
          const hour = params.dataIndex + 1;
          const startHour = parseInt(hoursRange.start.split(':')[0]);
          const endHour = parseInt(hoursRange.end.split(':')[0]);
          return (hour >= startHour && hour <= endHour) ? '#2ab0c5' : '#cccccc';
        },
        borderRadius: [10, 10, 0, 0]
      }
    }]
  };

  const handleHoursUpdate = async () => {
    if (!perfilId) return;

    const token = localStorage.getItem("token");
    if (!token) {
      console.error("❌ No hay token en localStorage");
      return;
    }

    try {
      const res = await fetch(
        `${constantUrlApiEndpoint}/user/enclosure-typing/${perfilId}`,
        { headers: { Accept: "application/json", Authorization: `Bearer ${token}` } }
      );

      if (!res.ok) {
        console.error("❌ GET enclosure-typing falló:", res.status, await res.text());
        return;
      }

      const { id: enclosureId, building_conditions = [] } = await res.json();
      if (!enclosureId) {
        console.error("❌ La respuesta no contiene enclosure_id");
        return;
      }

      const internalLoad = building_conditions.find(
        (bc: any) => bc.type === "internal_loads"
      );
      if (!internalLoad) {
        console.error("❌ No se encontró el bloque internal_loads");
        return;
      }

      const newHorario = {
        ...(internalLoad.details?.horario ?? {}),
        funcionamiento_semanal: (internalLoad.details?.horario?.funcionamiento_semanal ?? "5x2"),
        laboral: {
          inicio: (internalLoad.details?.horario?.laboral?.inicio ?? tempHours.start),
          fin: (internalLoad.details?.horario?.laboral?.fin ?? tempHours.end)
        }
      };

      // Si el usuario está editando horas, sí se debe actualizar con tempHours
      if (isEditingHours) {
        newHorario.laboral.inicio = tempHours.start;
        newHorario.laboral.fin = tempHours.end;
      }

      const payload = {
        type: "internal_loads",
        attributes: {
          ...internalLoad.details,
          horario: newHorario
        }
      };
      const headers = {
        Accept: "application/json",
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`
      };
      const url = `/building_condition/${enclosureId}/update?section=user`;
      const patchRes = await api.patch(url, payload, { headers });
      notify(`Horario actualizado con éxito`);

      // Actualizar el gráfico inmediatamente
      setHoursRange(tempHours);
      chartRef.current?.getEchartsInstance().setOption({
        series: [{
          data: hours.map((hour, i) => {
            const currentHour = i + 1;
            const startHour = parseInt(tempHours.start.split(':')[0]);
            const endHour = parseInt(tempHours.end.split(':')[0]);

            if (currentHour < startHour || currentHour > endHour) {
              return 0;
            }
            return data?.[`hour_${currentHour}`] ?? 0;
          })
        }]
      });

      await fetchWorkingHours();
      setIsEditingHours(false);

    } catch (err) {
      console.error("❌ Error inesperado en handleHoursUpdate:", err);
    }
  };

  const updateSchedule = async (newData: ScheduleData) => {
    if (perfilId === null) return;
    const token = localStorage.getItem("token");
    try {
      const putResponse = await fetch(
        `${constantUrlApiEndpoint}/${typeSelect}/schedule-update/${perfilId}`,
        {
          method: 'PATCH',
          headers: {
            accept: 'application/json',
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
          },
          body: JSON.stringify(newData)
        }
      );
      if (!putResponse.ok) {
        console.error("Error en el PUT:", putResponse.statusText);
        return;
      }

      const resp = await fetch(
        `${constantUrlApiEndpoint}/${typeSelect}/schedule/${perfilId}`,
        { headers: { accept: 'application/json', Authorization: `Bearer ${token}` } }
      );
      const updated = await resp.json();
      setData(updated);

      await fetchWorkingHours();

      onUpdate && onUpdate();
    } catch (error) {
      console.error("Error updating schedule", error);
    }
  };

  const [currentHourIndex, setCurrentHourIndex] = useState<number | null>(null);
  const [currentValue, setCurrentValue] = useState<number | null>(null);
  const [inputValue, setInputValue] = useState<number>(0);
  const [showModal, setShowModal] = useState<boolean>(false);

  const onChartReady = (chart: any) => {
    chart.on('click', (params: any) => {
      setCurrentHourIndex(params.dataIndex);
      setCurrentValue(params.value);
      setInputValue(params.value);
      setShowModal(true);
    });
  };

  const handleModalConfirm = () => {
    if (currentHourIndex === null || data === null) return;
    const schedule: ScheduleData = {};
    for (let i = 1; i <= 24; i++) {
      schedule[`hour_${i}`] = data[`hour_${i}`] ?? 0;
    }
    schedule[`hour_${currentHourIndex + 1}`] = inputValue;

    chartRef.current
      ?.getEchartsInstance()
      .setOption({
        series: [{
          data: [
            ...values.slice(0, currentHourIndex),
            inputValue,
            ...values.slice(currentHourIndex + 1)
          ]
        }]
      });

    updateSchedule(schedule);
    setShowModal(false);
    setCurrentHourIndex(null);
    setCurrentValue(null);
  };

  const renderHoursSection = () => (
    <div className="text-center mt-3">
      <p>
        <strong>
          <span>HORA DE INICIO: </span>
        </strong>
        {isEditingHours ? (
          <select
            value={tempHours.start}
            onChange={e => setTempHours(prev => ({ ...prev, start: e.target.value }))}
            className="mx-2"
          >
            {Array.from({ length: 24 }, (_, i) => {
              const hour = i + 1;
              const value = `${hour.toString().padStart(2, '0')}:00`;
              return <option key={value} value={value}>{value}</option>;
            })}
          </select>
        ) : (
          <span>{hoursRange.start}</span>
        )}
        &nbsp;&nbsp;
        <strong>
          <span>HORA FINAL: </span>
        </strong>
        {isEditingHours ? (
          <select
            value={tempHours.end}
            onChange={e => setTempHours(prev => ({ ...prev, end: e.target.value }))}
            className="mx-2"
          >
            {Array.from({ length: 24 }, (_, i) => {
              const hour = i + 1;
              const value = `${hour.toString().padStart(2, '0')}:00`;
              return <option key={value} value={value}>{value}</option>;
            })}
          </select>
        ) : (
          <span>{hoursRange.end}</span>
        )}
      </p>
      <div className="mt-2">
        {isEditingHours ? (
          <>
            <CustomButton
              color='red'
              className="btn btn-secondary"
              onClick={() => {
                setTempHours(hoursRange);
                setIsEditingHours(false);
              }}
            >
              Cancelar
            </CustomButton>
            <CustomButton
              className="btn btn-primary mx-2"
              onClick={handleHoursUpdate}
            >
              Guardar
            </CustomButton>
          </>
        ) : (
          <CustomButton
            className="btn btn-outline-primary" onClick={() => {
              setTempHours(hoursRange);
              setIsEditingHours(true);
            }}>
            Editar Horario
          </CustomButton>
        )}
      </div>
    </div>
  );

  return (
    <div className="apache-container">
      <div className="header text-center mb-3">
        <h2>{tipologia || "Tipología de Recinto"}</h2>
      </div>

      <div className="d-flex justify-content-center mb-3">
        <select
          className="form-select form-select-lg text-center"
          style={{ maxWidth: "300px", textAlignLast: "center" }}
          value={typeSelect}
          onChange={e => setTypeSelect(e.target.value)}
        >
          <option value="usuarios">Usuarios</option>
          <option value="iluminacion verano">Iluminación verano</option>
          <option value="iluminacion invierno">Iluminación invierno</option>
          <option value="equipos">Equipos</option>
        </select>
      </div>

      {loading ? (
        <p>Cargando datos...</p>
      ) : (
        <ReactECharts
          ref={chartRef}
          option={option}
          style={{ height: "100%", width: "100%", minHeight: "400px" }}
          onChartReady={onChartReady}
        />
      )}

      {renderHoursSection()}

      {showModal && (
        <ModalCreate
          isOpen={showModal}
          initialValue={currentValue}
          onSave={handleModalConfirm}
          onClose={() => {
            setShowModal(false);
            setCurrentHourIndex(null);
            setCurrentValue(null);
          }}
        >
          <div className="container d-flex flex-column align-items-center space-y-4">
            <label
              htmlFor="valueInput"
              className="text-lg font-medium text-gray-800 text-center"
            >
              Ingrese el nuevo valor:
            </label>
            <br />
            <div className="d-flex align-items-center">
              <input
                id="valueInput"
                type="number"
                min="0"
                max="100"
                className="border border-gray-300 rounded p-2 text-gray-800 text-center"
                value={inputValue}
                onChange={e => setInputValue(Math.min(100, Number(e.target.value)))}
                onKeyDown={e => {
                  if (e.key === '-') e.preventDefault();
                }}
              />
              <span style={{ marginLeft: '10px' }}>%</span>
            </div>
          </div>
        </ModalCreate>
      )}
    </div>
  );
};

export default ProfileSchedules;
