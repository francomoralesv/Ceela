
const ORIENTATION_RANGES: Record<Orientation, { min: number; max: number }> = {
    N:    { min: 0, max: 22.5 },
    NE:   { min: 22.5, max: 45 },
    E:    { min: 67.5, max: 90 },
    SE:   { min: 112.5, max: 135 },
    S:    { min: 157.5, max: 180 },
    SO:   { min: -157.5, max: -135 },
    O:    { min: -112.5, max: -90 },
    NO:   { min: -67.5, max: -45 },
};

// Devuelve el rango de azimut en formato "-90° ≤ Az < -67.5°" dado un ángulo string como "270"
export function angleToAzimutRangeString(angleString: string): string {
    const angle = parseFloat(angleString.replace(/,/g, '.'));
    if (isNaN(angle)) throw new Error('Ángulo inválido');
    // Definir los rangos de 8 orientaciones principales

    const ranges = [
        ORIENTATION_RANGES.N,
        ORIENTATION_RANGES.NE,
        ORIENTATION_RANGES.E,
        ORIENTATION_RANGES.SE,
        ORIENTATION_RANGES.S,
        ORIENTATION_RANGES.SO,
        ORIENTATION_RANGES.O,
        ORIENTATION_RANGES.NO,
    ];
    // Normalizar ángulo a [0, 360)
    let norm = angle % 360;
    if (norm < 0) norm += 360;
    // Buscar el rango correspondiente
    for (const r of ranges) {
        let min = r.min;
        const max = r.max;
        // Ajustar para el rango Norte que cruza 0°
        if (min < 0) {
            if (norm >= (360 + min) || norm < max) {
                min = 360 + min;
                return `${min}° ≤ Az < ${max}°`;
            }
        } else if (norm >= min && norm < max) {
            return `${min}° ≤ Az < ${max}°`;
        }
    }
    // Si no coincide, devolver el ángulo como rango puntual
    return `${norm}° ≤ Az < ${norm}°`;
}
// Tipos de orientación principales (8 direcciones)
type Orientation = 'N' | 'NE' | 'E' | 'SE' | 'S' | 'SO' | 'O' | 'NO';

/**
 * Devuelve el rango de azimut en formato string dado una orientación.
 * @param orientation Abreviatura de orientación ('N', 'S', etc.)
 * @returns Rango en string, por ejemplo: '157.5° ≤ Az < 202.5°'
 */
export function orientationToAzimutRange(orientation: string): string {
    const upper = orientation.toUpperCase() as Orientation;
    const range = ORIENTATION_RANGES[upper];
    if (!range) throw new Error(`Orientación desconocida: ${orientation}`);
    // Ajustar para el caso de Norte (cruza 0°)
    // Helper para formatear con coma como decimal
    const format = (num: number) => num.toString().replace('.', ',');
    return `${format(range.min)}° ≤ Az < ${format(range.max)}°`;
}

// Interfaz para representar un rango de azimut
interface AzimutRange {
    min: number;
    max: number;
    minInclusive: boolean;
    maxInclusive: boolean;
}

// Función para parsear el rango literal (con soporte para comas decimales)
function parseAzimutRange(rangeString: string): AzimutRange {
    // Remover espacios y reemplazar comas por puntos para decimales
    const cleanRange = rangeString.trim().replace(/\s+/g, ' ').replace(/,/g, '.');

    // Patrones para diferentes formatos de rangos
    const patterns = [
        // Formato: -90° ≤ Az < -67.5°
        /^(-?\d+(?:\.\d+)?)°?\s*≤\s*Az\s*<\s*(-?\d+(?:\.\d+)?)°?$/,
        // Formato: -90 <= Az < -67.5
        /^(-?\d+(?:\.\d+)?)\s*<=?\s*Az\s*<\s*(-?\d+(?:\.\d+)?)$/
    ];

    for (const pattern of patterns) {
        const match = cleanRange.match(pattern);
        if (match) {
            return {
                min: parseFloat(match[1]),
                max: parseFloat(match[2]),
                minInclusive: true,
                maxInclusive: false
            };
        }
    }

    throw new Error(`No se pudo parsear el rango: ${rangeString}`);
}

// Función para obtener la orientación basada en un rango
function getOrientationFromRange(min: number, max: number): Orientation {
    // Normalizar ángulos al rango [0, 360)
    const normalizeAngle = (angle: number): number => {
        let normalized = angle % 360;
        if (normalized < 0) normalized += 360;
        return normalized;
    };

    const normalizedMin = normalizeAngle(min);
    const normalizedMax = normalizeAngle(max);

    // Calcular el punto medio del rango para determinar la orientación
    let midPoint: number;

    if (normalizedMax > normalizedMin) {
        midPoint = (normalizedMin + normalizedMax) / 2;
    } else {
        // Caso donde el rango cruza el 0° (ej: 350° a 10°)
        midPoint = ((normalizedMin + normalizedMax + 360) / 2) % 360;
    }

    // Definir los rangos de orientación (8 direcciones principales de 45° cada una)
    if (midPoint >= 337.5 || midPoint < 22.5) return 'N';   // Norte
    if (midPoint >= 22.5 && midPoint < 67.5) return 'NE';   // Noreste
    if (midPoint >= 67.5 && midPoint < 112.5) return 'E';   // Este
    if (midPoint >= 112.5 && midPoint < 157.5) return 'SE'; // Sureste
    if (midPoint >= 157.5 && midPoint < 202.5) return 'S';  // Sur
    if (midPoint >= 202.5 && midPoint < 247.5) return 'SO'; // Suroeste
    if (midPoint >= 247.5 && midPoint < 292.5) return 'O';  // Oeste
    if (midPoint >= 292.5 && midPoint < 337.5) return 'NO'; // Noroeste

    return 'N'; // Valor por defecto
}

// Función principal que recibe el rango literal
export function azimutRangeToOrientation(rangeString: string): Orientation | undefined {
    try {
        if (rangeString) {
            const range = parseAzimutRange(rangeString);
            return getOrientationFromRange(range.min, range.max);
        }
    } catch (error) {
        console.error(`Error processing range "${rangeString}":`, error);
        // throw new Error(`Error processing range "${rangeString}": ${error}`);
    }
}

export function azimutRangeToFullOrientation(rangeString: string): string | undefined {
    const orientationMap: Record<Orientation, string> = {
        'N': 'Norte',
        'NE': 'Noreste',
        'E': 'Este',
        'SE': 'Sureste',
        'S': 'Sur',
        'SO': 'Suroeste',
        'O': 'Oeste',
        'NO': 'Noroeste'
    };

    const orientation = azimutRangeToOrientation(rangeString);
    if (orientation)
        return orientationMap[orientation];
}



function calculateAzimut(rangeString: string): number {
    const range = parseAzimutRange(rangeString);
    // Calculate the midpoint of the range
    return (range.min + range.max) / 2;
}

// Función de conveniencia para obtener un objeto con todas las conversiones
export const getOrientationMapping = (azimuthRanges: []): Record<string, { orientation: Orientation, fullName: string, azimut: number }> => {
    const mapping: Record<string, { orientation: Orientation, fullName: string, azimut: number }> = {};
    azimuthRanges.forEach((range) => {
        const orientation = azimutRangeToOrientation(range);
        const fullName = azimutRangeToFullOrientation(range);
        const azimut = calculateAzimut(range);
        if (orientation && fullName)
            mapping[range] = { orientation, fullName, azimut };
    });
    return mapping;
};

// Función de conveniencia para obtener un array de orientaciones únicas con su azimut
export const getOrientationMapping2 = (azimuthRanges: []): Array<{ orientation: Orientation, fullName: string, azimut: number }> => {
    const uniqueOrientations = new Map<Orientation, { orientation: Orientation, fullName: string, azimut: number }>();

    azimuthRanges.forEach((range) => {
        const orientation = azimutRangeToOrientation(range);
        const fullName = azimutRangeToFullOrientation(range);
        const azimut = range;

        if (orientation && fullName)
            if (!uniqueOrientations.has(orientation)) {
                uniqueOrientations.set(orientation, { orientation, fullName, azimut });
            }
    });

    return Array.from(uniqueOrientations.values());
};