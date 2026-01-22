from src.services.enclosures.enclosures_services import get_enclosure_ventilation_flows_by_id


class Formulas:
    @staticmethod
    def hve_infiltracion( enclosure_id:int, altura_promedio, areas_piso, rho_aire=1.225, cp_aire=1.005,db=None):
            """ Calcula la potencia de ventilación por infiltración en W/K """

            print("Calculando Hve por infiltración...")
            print(f"enclosure_id: {enclosure_id}, areas piso {areas_piso} ,altura_promedio: {altura_promedio}, areas_piso: {areas_piso}, rho_aire: {rho_aire}, cp_aire: {cp_aire}, db: {db}")
            infiltracion = get_enclosure_ventilation_flows_by_id(enclosure_id, "infiltraciones", db)
            altura_eq= altura_promedio * areas_piso
            caudal_m3s = infiltracion.get("value", None)
            print(f"infiltracion: {infiltracion}")
            if caudal_m3s is None:
                raise ValueError("El caudal de infiltración no está definido para el enclosure con ID {}".format(enclosure_id))
            return Formulas.calcular_Hve_por_caudal(float(caudal_m3s),altura_eq, rho_aire=rho_aire, cp_aire=cp_aire)


    @staticmethod
    def hve(R_pers_l_s,m2_por_pers,altura_eq=None,alturaxarea_piso=None,ro_aire=1.225,cp_aire=1.005,dt_hr=3600)   :
        """ Calcula la potencia de ventilación  en W/K """
        print(f"calcular_renovacion_aire: {Formulas.calcular_renovacion_aire(R_pers_l_s, m2_por_pers, altura_eq)}")
        print(f"1000: {1000}")
        print(f"alturaxarea_piso: {alturaxarea_piso}")
        print(f"ro_aire: {ro_aire}")
        print(f"cp_aire: {cp_aire}")
        print(f"dt_hr: {dt_hr}")
        return Formulas.calcular_renovacion_aire(R_pers_l_s,m2_por_pers, altura_eq)*1000*alturaxarea_piso*ro_aire*cp_aire/dt_hr

    @staticmethod
    def calcular_Hve_por_caudal(caudal_m3s,altura_eq, rho_aire=1.225, cp_aire=1.005,dt_hr=3600): # Hve de infiltracion en W/K
        """ Calcula la potencia de ventilación por caudal de aire. dt_hr 3600 seg """
        print(f"Fórmula: Hve infiltración = {caudal_m3s}  * 1000 *{altura_eq}* {rho_aire} * {cp_aire} / {dt_hr}")
        return caudal_m3s * altura_eq *1000*rho_aire * cp_aire / dt_hr
    
    @staticmethod
    def calcular_renovacion_aire(R_pers_l_s: float, m2_por_pers: float, altura_m: float) -> float:
        """
        Calcula la tasa de renovación de aire (R) en h⁻¹ por m².
        Si m2_por_pers o altura_m es 0, devuelve 0 en lugar de provocar división por cero.
        """
        # Si alguno de los denominadores fuera 0, devolvemos 0

        ocupacion = 0 if m2_por_pers == 0 else 1.0 / m2_por_pers
        caudal_l_s_m2 = R_pers_l_s * ocupacion
        caudal_m3_h_m2 = (caudal_l_s_m2 / 1000.0) * 3600.0
        volumen_m3_m2 = altura_m
        R = caudal_m3_h_m2 / volumen_m3_m2
        return R


    @staticmethod
    def calc_potencia(hora,hora_inicio=8,hora_fin=16, is_base=False):
        resta= 2 if is_base else 0
        constante_base = 10 - resta

        # Manejar horarios que cruzan medianoche
        if hora_inicio <= hora_fin:
            en_horario = (hora_inicio <= hora <= hora_fin)
        else:
            # Horario nocturno que cruza medianoche
            en_horario = (hora >= hora_inicio) or (hora <= hora_fin)

        if en_horario:
            factor = 1.0        # valor en columna E14 + 68 = 69
            if factor == 0:
                factor = 1

            return constante_base * factor
        else:
            return 0
    @staticmethod
    def flujo_interno(hora, hora_inicio=8, hora_fin=16, area_pisos=0, is_base=False):
        return Formulas.calc_potencia(hora, hora_inicio=hora_inicio, hora_fin=hora_fin,  is_base=is_base) * area_pisos
    @staticmethod
    def flujo_interno2(hora,total_cargas_internas,potencia_base,hora_inicio=8,hora_fin=18,area_pisos=100):
        # Manejar horarios que cruzan medianoche
        if hora_inicio <= hora_fin:
            en_horario = (hora_inicio <= hora <= hora_fin)
        else:
            # Horario nocturno que cruza medianoche
            en_horario = (hora >= hora_inicio) or (hora <= hora_fin)

        if en_horario:
                return (total_cargas_internas+potencia_base)*area_pisos
        else:
                return 0