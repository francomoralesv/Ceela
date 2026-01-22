import { useApi } from '@/hooks/useApi';
import { EnergySystemSelection } from '@/types/energySystem';
import React, { useEffect, useState } from 'react';
import CustomButton from '../../common/CustomButton';
import EnergySystemSelectors, { ConfigState } from '../recinto/EnergySystemSelectors';
import { Save } from 'lucide-react';

const ConfiguracionEnergiaTab: React.FC = () => {
    const [config, setConfig] = useState<ConfigState>({
        energySystems: [],
        rendimientoCalef: [],
        distribucionHvac: [],
        controlHvac: [],
        rendimientoRef: [],
        consumosEnergia: []
    });
    const [energyConfig, setEnergyConfig] = useState<EnergySystemSelection>({
        combustibleCalef: null,
        rendimientoCalef: null,
        distribucionCalef: null,
        controlCalef: null,
        combustibleRef: null,
        rendimientoRef: null,
        distribucionRef: null,
        controlRef: null
    });
    const [success, setSuccess] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [isAdmin, setIsAdmin] = useState<boolean>(false);
    const { post, get, loading } = useApi();

    const projectId = typeof window !== 'undefined' ? localStorage.getItem('project_id') : null;
    
    useEffect(() => {
        if (typeof window !== 'undefined') {
            const roleId = localStorage.getItem('role_id');
            setIsAdmin(roleId === '1');
        }
    }, []);

    useEffect(() => {
        const fetchConfig = async () => {
            if (!projectId) return;
            try {
                const data = await get(`/heating-config/by-project/${projectId}`);
                if (data && typeof data === 'object') {
                    setEnergyConfig(prev => ({
                        ...prev,
                        combustibleCalef: data.combustible_codigo ? {
                            code: data.combustible_codigo,
                            description: data.combustible_codigo,
                            value: data.combustible_valor
                        } : null,
                        rendimiento: data.rendimiento_codigo ? {
                            code: data.rendimiento_codigo,
                            description: data.rendimiento_codigo,
                            value: data.rendimiento_valor
                        } : null,
                        distribucion: data.distribucion_codigo ? {
                            code: data.distribucion_codigo,
                            description: data.distribucion_codigo,
                            value: data.distribucion_valor
                        } : null,
                        control: data.control_codigo ? {
                            code: data.control_codigo,
                            description: data.control_codigo,
                            value: data.control_valor
                        } : null
                    }));
                }
            } catch (err: any) {
                // Si es 404, no hay config previa, no mostrar error
                if (err?.response?.status !== 404) setError('Error al obtener la configuración.');
            }
        };
        fetchConfig();
    }, [projectId]);

    const handleSave = async () => {
        setSuccess(null);
        setError(null);
        if (!projectId) {
            setError('No se encontró el ID del proyecto.');
            return;
        }
        if (!energyConfig.combustibleCalef) {
            setError('Selecciona un combustible.');
            return;
        }
        try {
            const payload: any = {
                project_id: Number(projectId),
                combustible_codigo: energyConfig.combustibleCalef.code,
                combustible_valor: energyConfig.combustibleCalef.value ?? 0,
                rendimiento_codigo: energyConfig.rendimientoCalef?.code || '',
                rendimiento_valor: energyConfig.rendimientoCalef?.value ?? 0,
                caldera_codigo: '', // No hay selector, se deja vacío o puedes agregar uno
                caldera_valor: 0,   // No hay selector, se deja 0 o puedes agregar uno
                distribucion_codigo: energyConfig.distribucionCalef?.code || '',
                distribucion_valor: energyConfig.distribucionCalef?.value ?? 0,
                control_codigo: energyConfig.controlCalef?.code || '',
                control_valor: energyConfig.controlCalef?.value ?? 0,
            };
            await post(`/heating-config/by-project/${projectId}`, payload);
            setSuccess('Configuración guardada correctamente.');
        } catch {
            setError('Error al guardar la configuración.');
        }
    };

    return (
        <div>
            {success && <div className="alert alert-success mt-2">{success}</div>}
            {error && <div className="alert alert-danger mt-2">{error}</div>}
            <EnergySystemSelectors
                onChange={(selection: EnergySystemSelection, consumosEnergia?: any[]) => {
                    setEnergyConfig(selection);
                    setConfig(prev => ({
                        ...prev,
                        consumosEnergia: consumosEnergia || []
                    }));
                }}
            />
            {!isAdmin && (
                <div className="d-flex justify-content-end">
                    <CustomButton
                        variant="save"
                        onClick={handleSave}
                        disabled={loading}
                        style={{ minWidth: 180 }}
                        color="orange"
                    >
                        <Save className="me-2" size={18} />
                        {loading ? 'Guardando...' : 'Guardar'}
                    </CustomButton>
                </div>
            )}
        </div>
    );
};

export default ConfiguracionEnergiaTab;
