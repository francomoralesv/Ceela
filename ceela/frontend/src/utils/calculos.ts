/**
 * Calcula la demanda de ACS (Agua Caliente Sanitaria) en kWh para un período dado.
 *
 * @param {number} numPersonas - Número de personas que consumen ACS.
 * @param {number} litrosPorPersonaDia - Litros de ACS consumidos por persona al día.
 * @param {number} tempRed - Temperatura de red de agua fría (en °C) promedio durante el período.
 * @param {number} tempObjetivo - Temperatura objetivo del agua caliente (en °C).
 * @param {number} cpAguaWhKgK - Calor específico del agua en Wh/(kg·K). Aprox 1.16 Wh/(kg·K).
 * @param {number} dias - Cuántos días abarca el cálculo (30, 31, etc.).
 * @returns {number} Demanda total de ACS en kWh para el período especificado.
 *
 * Ejemplo de uso:
 * const demanda = calcularDemandaACS(
 *   5,     // numPersonas
 *   40,    // litrosPorPersonaDia
 *   12,    // tempRed
 *   45,    // tempObjetivo
 *   1.16,  // cpAguaWhKgK
 *   31     // dias
 * );
 */
export function calcularDemandaACS(
    numPersonas: number = 3,
    litrosPorPersonaDia: number = 30,
    tempRed: number = 15,
    tempObjetivo: number = 45,
    cpAguaWhKgK: number = 1.16,
    dias: number = 30
  ): number {
    // Litros totales por día
    const litrosTotalesDia = numPersonas * litrosPorPersonaDia;
    // Asumir densidad del agua ~ 1 kg/l
    const masaKgDia = litrosTotalesDia; // 1 litro ~ 1 kg
    // Salto térmico (K)
    const deltaT = tempObjetivo - tempRed;
  
    // Energía en Wh/día
    const energiaWhDia = masaKgDia * cpAguaWhKgK * deltaT;
    // Pasar a kWh/día
    const energiaKwhDia = energiaWhDia / 1000;
  
    // Multiplicar por número de días para total kWh
    return energiaKwhDia * dias;
  }
  