import { useEffect, useState } from 'react';
import { useApi } from './useApi';

interface Constant {
    type: string;
    is_deleted: boolean;
    user_id: string | null;
    name: string;
    atributs: Record<string, any>;
    id: number;
    create_status: string;
}

export const useConstants = (type?: string, name?: string) => {
    const api = useApi();
    const [constant, setConstants] = useState<Constant | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    const fetchConstants = async () => {
        setLoading(true);
        setError(null);
        try {
            const params = new URLSearchParams();
            if (type) params.append('type', type);
            if (name) params.append('name', name);
            console.log(`[Constants] Fetching constants... /constants?${params.toString()}`);

            const response = await api.get(`/constants?${params.toString()}`);
            console.log('[Constants] Response:', response);
            setConstants(response);
        } catch (err: any) {
            setError(err.message || 'Error fetching constants');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchConstants();
    }, []);

    return { constant, loading, error };
};
