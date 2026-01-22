import { useState, useCallback } from 'react';
import { constantUrlApiEndpoint } from '@/utils/constant-url-endpoint';

interface MaterialInfo {
    id: number;
    [key: string]: any;
}

const materialsCache: Record<string, MaterialInfo> = {};

export const useMaterialData = () => {
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<Error | null>(null);

    const getMaterialByCode = useCallback(async (code: string | undefined | null): Promise<MaterialInfo | null> => {
        if (!code || typeof code !== 'string' || code.toLowerCase() === 'unknown') {
            console.log(`Invalid or unknown material code: ${code}`);
            return null;
        }

        const normalizedCode = code.toLowerCase();

        if (materialsCache[normalizedCode]) {
            console.log(`Using cached material for code: ${normalizedCode}`);
            return materialsCache[normalizedCode];
        }

        setLoading(true);
        setError(null);

        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${constantUrlApiEndpoint}/constants-code_ifc?code_ifc=${encodeURIComponent(normalizedCode)}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`,
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            // Asumimos que la API devuelve un array y tomamos el primer elemento, o null si está vacío.
            const materialInfo: MaterialInfo | null = data && data.length > 0 ? data[0] : null;

            if (materialInfo) {
                materialsCache[normalizedCode] = materialInfo;
            }
            
            setLoading(false);
            return materialInfo;
        } catch (err) {
            console.error('Error fetching material by code:', err);
            setError(err as Error);
            setLoading(false);
            return null;
        }
    }, []);

    return {
        getMaterialByCode,
        loading,
        error,
    };
};