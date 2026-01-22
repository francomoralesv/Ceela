import React, { useState, useEffect } from 'react';
import { notify } from '@/utils/notify';
import { constantUrlApiEndpoint } from '@/utils/constant-url-endpoint';
import SaveButton from './common/SaveButton';
import CustomButton from './common/CustomButton';

export interface EnergySource {
  code: string;
  name: string;
  co2_eq: number | null;
}

const EmissionFactorsManager: React.FC = () => {
  const [loading, setLoading] = useState<boolean>(true);
  const [saving, setSaving] = useState<boolean>(false);
  const [energySources, setEnergySources] = useState<EnergySource[]>([]);
  const [editingRow, setEditingRow] = useState<number | null>(null);
  const [tempValue, setTempValue] = useState<string>('');

  const fetchEnergySources = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${constantUrlApiEndpoint}/constants?type=energy_systems&name=general`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Error al cargar los factores de emisión');
      }

      const data = await response.json();
      const energySourcesData = data.atributs?.consumos_por_fuente_de_energia || [];
      
      if (Array.isArray(energySourcesData)) {
        setEnergySources(energySourcesData);
      } else {
        console.error('Invalid data format received from API');
        notify('Formato de datos inválido recibido del servidor', 'error');
      }
    } catch (error) {
      console.error('Error fetching energy sources:', error);
      notify('Error al cargar los factores de emisión', 'error');
    } finally {
      setLoading(false);
    }
  };

  // Fetch initial data from API
  useEffect(() => {
    fetchEnergySources();
  }, []);  

  const handleUpdate = async () => {
    try {
      setSaving(true);
      const requestData = {
        consumos_por_fuente_de_energia: energySources
      };
      
      const response = await fetch(`${constantUrlApiEndpoint}/update_energy_systems_consumos_por_fuente_de_energia`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(requestData)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('API Error:', errorData);
        throw new Error(errorData.detail?.[0]?.msg || 'Error al actualizar los factores de emisión');
      }
      notify('Factores de emisión actualizados correctamente', 'success');

    } catch (error:any) {
      console.error('Error updating emission factors:', error);
      notify(error.message || 'Error al actualizar los factores de emisión', 'error');
    } finally {
      setSaving(false);
      setEditingRow(null);
    }
  };

  const startEditing = (index: number) => {
    setEditingRow(index);
    setTempValue(energySources[index].co2_eq?.toString() || '');
  };

  const handleValueChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setTempValue(e.target.value);
  };

  const saveEdit = (index: number) => {
    const newValue = parseFloat(tempValue);
    if (!isNaN(newValue) && newValue >= 0) {
      const updatedSources = [...energySources];
      updatedSources[index].co2_eq = newValue;
      setEnergySources(updatedSources);
    }
    setEditingRow(null);
  };

  if (loading) {
    return <div>Cargando factores de emisión...</div>;
  }

  return (
    <div className="emission-factors-container">
      <h3>Factores de emisión de CO₂ por fuente de energía</h3>
      <p>Actualice los factores de emisión según corresponda.</p>
      
      <div className="table-responsive">
        <table className="table ">
          <thead>
            <tr>
              <th>Fuente de energía</th>
              <th>Factor de emisión (kg CO₂eq/kWh)</th>
            </tr>
          </thead>
          <tbody>
            {energySources.map((source, index) => (
              <tr key={source.code}>
                <td>{source.name}</td>
                <td>
                  {editingRow === index ? (
                    <div className="input-group">
                      <input
                        type="number"
                        className="form-control"
                        value={tempValue}
                        onChange={handleValueChange}
                        step="0.001"
                        min="0"
                      />
                      <button 
                        className="btn btn-sm"
                        style={{ backgroundColor: '#307EF3', color: 'white', border: '1px solid #307EF3' }}
                        onClick={() => saveEdit(index)}
                      >
                        <i className="bi bi-check"></i>
                      </button>
                      <button 
                        className="btn btn-sm"
                        style={{ backgroundColor: '#6c757d', color: 'white', border: '1px solid #6c757d' }}
                        onClick={() => setEditingRow(null)}
                      >
                        <i className="bi bi-x"></i>
                      </button>
                    </div>
                  ) : (
                    <div className="d-flex justify-content-between align-items-center">
                      <span>{source.co2_eq !== null ? source.co2_eq : 'N/A'}</span>
                      <CustomButton
                        variant="editIcon"
                        onClick={() => startEditing(index)}
                      />
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-4 d-flex justify-content-end">
        <SaveButton onClick={handleUpdate} disabled={saving} /> 
      </div>

      <style jsx>{`
        .emission-factors-container {
          padding: 1rem;
        }
        .table {
          margin-top: 1rem;
        }
        .input-group {
          max-width: 300px;
        }
        .btn-sm {
          padding: 0.25rem 0.5rem;
          font-size: 0.875rem;
        }
      `}</style>
    </div>
  );
};

export default EmissionFactorsManager;
