// Energy calculation utilities

/**
 * Calculate SCOP (Seasonal Coefficient of Performance) for heating
 */
export const calculateSCOP = (
    rendimientoCalef: number,
    distribucionHvac: number,
    controlHvac: number
): number => {
    if (rendimientoCalef && distribucionHvac && controlHvac) {
        return rendimientoCalef * distribucionHvac * controlHvac;
    }
    return 0;
};

/**
 * Calculate SEER (Seasonal Energy Efficiency Ratio) for cooling
 */
export const calculateSEER = (
    rendimientoRef: number,
    distribucionHvac: number,
    controlHvac: number
): number => {
    if (rendimientoRef && distribucionHvac && controlHvac) {
        return rendimientoRef * distribucionHvac * controlHvac;
    }
    return 0;
};

/**
 * Calculate primary energy consumption for heating
 */
export const calculatePrimaryEnergyCalef = (
    demandaCalef: number,
    scopCalef: number
): number => {
    if (scopCalef <= 0) {
        return 0;
    }
    return demandaCalef / scopCalef;
};

/**
 * Calculate primary energy consumption for cooling
 */
export const calculatePrimaryEnergyRef = (
    demandaRef: number,
    seerRef: number
): number => {
    if (seerRef <= 0) {
        return 0;
    }
    return demandaRef / seerRef;
};

/**
 * Calculate total primary energy consumption
 */
export const calculateTotalPrimaryEnergy = (
    consumoEnergiaPrimariaCalef: number,
    consumoEnergiaPrimariaRef: number,
    demandaIlum: number
): number => {
    const consumoCalefVerificado = !isNaN(consumoEnergiaPrimariaCalef) ? consumoEnergiaPrimariaCalef : 0;
    const consumoRefVerificado = !isNaN(consumoEnergiaPrimariaRef) ? consumoEnergiaPrimariaRef : 0;
    const demandaIlumVerificada = !isNaN(demandaIlum) ? demandaIlum : 0;

    return consumoCalefVerificado + consumoRefVerificado + demandaIlumVerificada;
};

/**
 * Calculate CO2 emissions for heating
 */
export const calculateCO2EmissionsCalef = (
    consumoEnergiaPrimariaCalef: number,
    co2Factor: number,
    superficie: number
): number => {
    return (consumoEnergiaPrimariaCalef || 0) * (co2Factor || 0) * (superficie || 0);
};

/**
 * Calculate CO2 emissions for cooling
 */
export const calculateCO2EmissionsRef = (
    consumoEnergiaPrimariaRef: number,
    co2Factor: number,
    superficie: number
): number => {
    return (consumoEnergiaPrimariaRef || 0) * (co2Factor || 0) * (superficie || 0);
};

/**
 * Calculate CO2 emissions for lighting
 */
export const calculateCO2EmissionsIlum = (
    demandaIlum: number,
    co2Factor: number,
    superficie: number
): number => {
    return (demandaIlum || 0) * (co2Factor || 0) * (superficie || 0);
};

/**
 * Calculate total CO2 emissions
 */
export const calculateTotalCO2Emissions = (
    co2EqCalef: number,
    co2EqRef: number,
    co2EqIlum: number
): number => {
    return (co2EqCalef || 0) + (co2EqRef || 0) + (co2EqIlum || 0);
};

/**
 * Get a value from a list based on code
 */
export const getValueByCode = (
    list: any[],
    selectedCode: string | undefined
): number => {
    if (!selectedCode) return 0;

    const selectedItem = list.find((item) => item.code === selectedCode);
    return selectedItem?.value || 0;
};

/**
 * Process global results to create recinto objects
 */
export const processGlobalResults = (
    resultByEnclosure: any[]
) => {
    if (!resultByEnclosure) return [];

    return resultByEnclosure.map((enclosure: any) => {
        // Calculate the demand values
        const demandaCalef = enclosure.positive_sum / enclosure.surface || 0;
        const demandaRef = enclosure.negative_sum / enclosure.surface || 0;
        const demandaIlum = 0; // Default value if not provided
        const demandaTotal = demandaCalef + demandaRef + demandaIlum;

        return {
            id: enclosure.enclosure_id,
            name_enclosure: enclosure.enclosure_name,
            perfil_uso: enclosure.occupation_profile_name,
            superficie: enclosure.surface,
            demanda_calef: demandaCalef,
            demanda_ref: demandaRef,
            demanda_ilum: demandaIlum,
            demanda_total: demandaTotal,
            consumo_calef: 0,
            consumo_ref: 0,
            consumo_total: 0,
            co2_eq: 0,
            hrs_disconfort_calef: 0,
            hrs_disconfort_ref: 0,
            hrs_disconfort_total: 0,
            // Additional properties for calculations
            rendimiento_calef: 0,
            distribucion_calef: 0,
            control_calef: 0,
            scop_calef: 0,
            scop_mc_calef: 0,
            rendimiento_ref: 0,
            distribucion_ref: 0,
            control_ref: 0,
            seer_ref: 0,
            seer_mc_ref: 0,
            consumo_energia_primaria_calef: 0,
            consumo_energia_primaria_ref: 0,
            consumo_energia_primaria_total: 0,
            co2_eq_calef: 0,
            co2_eq_ref: 0,
            co2_eq_ilum: 0,
            co2_eq_total: 0
        };
    });
};

/**
 * Process base results to create recinto objects
 */
export const processBaseResults = (
    baseByEnclosure: any[],
    energySystems: any[]
) => {
    if (!baseByEnclosure) return [];

    return baseByEnclosure.map((enclosure: any) => {
        // Calculate the demand values
        const demandaCalef = enclosure.positive_sum / enclosure.surface || 0;
        const demandaRef = enclosure.negative_sum / enclosure.surface || 0;
        const demandaIlum = 0; // Default value if not provided
        const demandaTotal = demandaCalef + demandaRef + demandaIlum;

        // Get combustible data
        const combustibleCalefCode = enclosure.combustible_calef_code || "";;

        const valorCombustibleCalef = combustibleCalefCode && energySystems.length > 0
            ? energySystems.find(system => system.code === combustibleCalefCode)?.value || 1
            : enclosure.combustible_calef_value || 1;

        const seerRefValue = enclosure.seer_ref || 1;

        // Calculate consumption
        const consumoCalef = demandaCalef * valorCombustibleCalef;
        const consumoRef = seerRefValue > 0 ? demandaRef / seerRefValue : 0;
        const consumoTotal = consumoCalef + consumoRef;

        // Calculate CO2 emissions
        const co2FactorCalef = enclosure.co2_factor_calef || 0;
        const co2FactorRef = enclosure.co2_factor_ref || 0;
        const surface = enclosure.surface || 0;

        const co2EqCalef = consumoCalef * co2FactorCalef * surface;
        const co2EqRef = consumoRef * co2FactorRef * surface;
        const co2EqTotal = co2EqCalef + co2EqRef;

        return {
            id: enclosure.enclosure_id,
            name_enclosure: enclosure.enclosure_name,
            perfil_uso: enclosure.occupation_profile_name || "",
            superficie: enclosure.surface,
            demanda_calef: demandaCalef,
            demanda_ref: demandaRef,
            demanda_ilum: demandaIlum,
            demanda_total: demandaTotal,
            consumo_calef: consumoCalef,
            consumo_ref: consumoRef,
            consumo_total: consumoTotal,
            co2_eq_calef: co2EqCalef,
            co2_eq_ref: co2EqRef,
            co2_eq_total: co2EqTotal,
            hrs_disconfort_calef: enclosure.discomfort_hours_heating || 0,
            hrs_disconfort_ref: enclosure.discomfort_hours_cooling || 0,
            hrs_disconfort_total: (enclosure.discomfort_hours_heating || 0) + (enclosure.discomfort_hours_cooling || 0),
            scop_calef: 1, // Fixed value for the base case
            seer_ref: seerRefValue,
            // Other properties will have default values (0)
            rendimiento_calef: 0,
            distribucion_calef: 0,
            control_calef: 0,
            scop_mc_calef: 0,
            rendimiento_ref: 0,
            distribucion_ref: 0,
            control_ref: 0,
            seer_mc_ref: 0,
            consumo_energia_primaria_calef: 0,
            consumo_energia_primaria_ref: 0,
            consumo_energia_primaria_total: 0,
            co2_eq_ilum: 0
        };
    });
};
