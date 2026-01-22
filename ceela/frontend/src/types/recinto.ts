export interface Recinto {
    id?: number;
    enclosure_id?: number;
    name_enclosure?: string;
    nombre_recinto?: string;
    perfil_uso?: string;
    usage_profile_name?: string;
    superficie?: number;

    // Demands
    demanda_calef?: number;
    demanda_calefaccion?: number;
    demanda_ref?: number;
    demanda_refrigeracion?: number;
    demanda_ilum?: number;
    demanda_iluminacion?: number;
    demanda_total?: number;

    // Consumption
    consumo_calef?: number;
    consumo_calefaccion?: number;
    consumo_ref?: number;
    consumo_refrigeracion?: number;
    consumo_total?: number;

    // CO2 emissions
    co2_eq?: number;
    co2_eq_calef?: number;
    co2_eq_calefaccion?: number;
    co2_eq_ref?: number;
    co2_eq_refrigeracion?: number;
    co2_eq_ilum?: number;
    co2_eq_iluminacion?: number;
    co2_eq_total?: number;

    // Caso base fields
    caso_base_demanda_calefaccion?: number;
    caso_base_demanda_refrigeracion?: number;
    caso_base_demanda_iluminacion?: number;
    caso_base_demanda_total?: number;
    caso_base_consumo_calefaccion?: number;
    caso_base_consumo_refrigeracion?: number;
    caso_base_consumo_total?: number;
    caso_base_co2_eq_calefaccion?: number;
    caso_base_co2_eq_refrigeracion?: number;
    caso_base_co2_eq_iluminacion?: number;
    caso_base_co2_eq_total?: number;
    caso_base_hrs_disconfort_calefaccion?: number;
    caso_base_hrs_disconfort_refrigeracion?: number;
    caso_base_hrs_disconfort_total?: number;

    // Primary energy consumption
    consumo_energia_primaria_calef?: number;
    consumo_energia_primaria_ref?: number;
    consumo_energia_primaria_total?: number;

    // Efficiency
    scop_calef?: number;
    seer_ref?: number;

    // Discomfort hours
    hrs_disconfort_calef?: number;
    hrs_disconfort_calefaccion?: number;
    hrs_disconfort_ref?: number;
    hrs_disconfort_refrigeracion?: number;
    hrs_disconfort_total?: number;

    // Systems configuration
    combustible_calef_code?: string;
    combustible_calef_value?: number;
    combustible_calef_fep?: number;

    combustible_ref_code?: string;
    combustible_ref_value?: number;
    combustible_ref_fep?: number;
    rendimiento_calef_code?: string;
    distribucion_hvac_code?: string;
    control_hvac_code?: string;
    rendimiento_ref_code?: string;
    distribucion_hvac_ref_code?: string;
    control_hvac_ref_code?: string;
}
