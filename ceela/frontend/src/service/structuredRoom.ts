
import { useApi } from '@/hooks/useApi';

// Hook para usar en componentes funcionales
export function useStructuredRoomService() {
    const { post, loading, error } = useApi();

    const postStructuredRoom = async (buildingStructure: any, projectId: string) => {
        const url = `/structured/room/${projectId}`;
        return post(url, buildingStructure);
    };

    return { postStructuredRoom, loading, error };
}
