export interface SystemOption {
    code: string;
    description: string;
    value?: number;
    fep?: number;
    co2_eq?: number;
}

export interface SystemSelection {
    code: string;
    description: string;
}

export interface EnergySystemConfig {
    energySystems: SystemOption;
    rendimientoCalef: SystemOption;
    distribucionHvac: SystemOption;
    controlHvac: SystemOption;
}

export interface EnergySystemSelection {
    combustibleCalef: SystemOption | null;
    rendimientoCalef: SystemOption | null;
    distribucionCalef: SystemOption | null;
    controlCalef: SystemOption | null;
    combustibleRef: SystemOption | null;
    rendimientoRef: SystemOption | null;
    distribucionRef: SystemOption | null;
    controlRef: SystemOption | null;
}

export interface EnergySystemSelectorsProps {
    config?: EnergySystemConfig;
    onChange: (selection: EnergySystemSelection, consumosEnergia?: SystemOption[]) => void;
}
