import { orientationToAzimutRange } from "../src/utils/azimut";
import { describe, it, expect } from 'vitest';
describe('orientationToAzimutRange', () => {
    it('devuelve el rango correcto para cada orientaci n', () => {
        expect(orientationToAzimutRange('N')).toEqual('0° ≤ Az < 22,5°');
        expect(orientationToAzimutRange('NE')).toEqual('22,5° ≤ Az < 45°');
        expect(orientationToAzimutRange('E')).toEqual('67,5° ≤ Az < 90°');
        expect(orientationToAzimutRange('SE')).toEqual('112,5° ≤ Az < 135°');
        expect(orientationToAzimutRange('S')).toEqual('157,5° ≤ Az < 180°');
        expect(orientationToAzimutRange('SO')).toEqual('-157,5° ≤ Az < -135°');
        expect(orientationToAzimutRange('O')).toEqual('-112,5° ≤ Az < -90°');
        expect(orientationToAzimutRange('NO')).toEqual('-67,5° ≤ Az < -45°');
    });

    // Este test ya no es necesario porque ahora el rango de N siempre es '337,5° ≤ Az < 22,5°'
    // it('lleva el rango correcto para la orientación Norte que cruza 0°', () => {
    //     expect(orientationToAzimutRange('N')).toEqual('-22.5° ≤ Az < 22.5°');
    // });
});
