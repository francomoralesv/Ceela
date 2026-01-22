import { Recinto } from '@/types/recinto';
import { createContext, ReactNode, useContext, useState } from 'react';

interface RecintosContextType {
    recintos: Recinto[];
    selectedRecintoId: number | null;
    baseRecintos: Recinto[];
    setRecintos: (recintos: Recinto[]) => void;
    setSelectedRecintoId: (id: number | null) => void;
    setBaseRecintos: (recintos: Recinto[]) => void;
    addRecinto: (recinto: Recinto) => void;
    updateRecinto: (id: number, updates: Partial<Recinto>) => void;
    deleteRecinto: (id: number) => void;
    createBaseRecinto: (recinto: Recinto) => void;
}

const RecintosContext = createContext<RecintosContextType | undefined>(undefined);

export function RecintosProvider({ children }: { children: ReactNode }) {
    const [recintos, setRecintos] = useState<Recinto[]>([]);
    const [selectedRecintoId, setSelectedRecintoId] = useState<number | null>(null);
    const [baseRecintos, setBaseRecintos] = useState<Recinto[]>([]);

    // Add a new recinto 
    const addRecinto = (recinto: Recinto) => {
        setRecintos(prev => [...prev, recinto]);
    };

    // Update an existing recinto
    const updateRecinto = (id: number, updates: Partial<Recinto>) => {
        setRecintos(prev => prev.map(r =>
            r.id === id ? { ...r, ...updates } : r
        ));
    };

    // Delete a recinto
    const deleteRecinto = (id: number) => {
        setRecintos(prev => prev.filter(r => r.id !== id));
    };

    // Create a base recinto
    const createBaseRecinto = (recinto: Recinto) => {
        setBaseRecintos(prev => [...prev, recinto]);
    };

    return (
        <RecintosContext.Provider value={{
            recintos,
            selectedRecintoId,
            baseRecintos,
            setRecintos,
            setSelectedRecintoId,
            setBaseRecintos,
            addRecinto,
            updateRecinto,
            deleteRecinto,
            createBaseRecinto,
        }}>
            {children}
        </RecintosContext.Provider>
    );
}

export function useRecintos() {
    const context = useContext(RecintosContext);
    if (context === undefined) {
        throw new Error('useRecintos must be used within a RecintosProvider');
    }
    return context;
}
