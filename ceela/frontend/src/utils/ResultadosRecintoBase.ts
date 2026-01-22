
interface DatoRecintoBase {
    ID_Recinto: number;
    Hora: number;
    Dia: number;
    Mes: number;
    Temperatura_exterior: number;
    Temperatura_operativa_con_clima: number;
    Temperatura_operativa_free_float: number;
    demanda_total: number;
    // ...otros campos relevantes
    [key: string]: any;
}

export class ResultadosRecintoBase {
    private datos: DatoRecintoBase[];
    private superficie: number;
    private potenciaBase: number;
    private horaInicio: number;
    private horaFinal: number;

    constructor(datos: DatoRecintoBase[], superficie: number, potenciaBase: number, horaInicio: number, horaFinal: number) {
        this.datos = datos;
        this.superficie = superficie;
        this.potenciaBase = potenciaBase;
        this.horaInicio = horaInicio;
        this.horaFinal = horaFinal;
    }

    calcularDemandaCalefaccion(): number {
        const suma = this.datos.reduce((acc, curr) => acc + (curr.demanda_total || 0), 0);
        return this.superficie > 0 ? suma / this.superficie : 0;
    }

    calcularRefrigeracion(): number {
        const sumaNegativos = this.datos
            .filter(d => (d.demanda_total || 0) < 0)
            .reduce((acc, curr) => acc + Math.abs(curr.demanda_total || 0), 0);
        return this.superficie > 0 ? sumaNegativos / this.superficie : 0;
    }

    calcularIluminacion(): number {
        // Suponiendo que el porcentaje de iluminación verano está en columnas AS y AT
        // y que hay que sumar los valores para horarios entre horaInicio y horaFinal
        // Aquí se asume que los campos se llaman 'iluminacion_verano_as' y 'iluminacion_verano_at'
        // Ajusta los nombres de campos según tu estructura real
        const suma = this.datos
            .filter(d => d.Hora > this.horaInicio && d.Hora < this.horaFinal)
            .reduce((acc, curr) => {
                const porcentaje = (curr.iluminacion_verano_as || 0) + (curr.iluminacion_verano_at || 0);
                return acc + (porcentaje * this.potenciaBase / 100);
            }, 0);
        return suma;
    }

    calcularTotal(): number {
        return this.calcularDemandaCalefaccion() + this.calcularRefrigeracion() + this.calcularIluminacion();
    }

    // Suma de demanda_total > 0 para un recinto dado
    static sumaDemandaPositivaPorRecinto(df: DatoRecintoBase[], recintoId: number): number {
        return df
            .filter(d => d.ID_Recinto === recintoId && (d.demanda_total || 0) > 0)
            .reduce((acc, curr) => acc + (curr.demanda_total || 0), 0);
    }

    // Suma de demanda_total < 0 para un recinto dado
    static sumaDemandaNegativaPorRecinto(df: DatoRecintoBase[], recintoId: number): number {
        return df
            .filter(d => d.ID_Recinto === recintoId && (d.demanda_total || 0) < 0)
            .reduce((acc, curr) => acc + (curr.demanda_total || 0), 0);
    }
}
