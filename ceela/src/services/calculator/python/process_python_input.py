import os
import pickle

from src.calc_engine.formulas import Formulas
from src.services.calculator.calc_humidity import calc_humidity_by_project, usage_profile
from src.services.enclosures.enclosures_services import get_enclosure_ventilation_flows_by_id, \
    get_enclosure_internal_loads_by_id, get_total_floor_area_by_enclosure_id, get_enclosure_lightning_by_id, \
    get_enclosure_internal_loads
from src.services.sol.sol_elements import read_sol_window_parquet
from src.utils.logging import logger
from src.utils.constants import public_folder
from src.models.entity.project_table import Project
from pandas.core.interchange.dataframe_protocol import DataFrame
from dateutil import parser
import pandas as pd
import numpy as np

from src.utils.redis_utils import get_redis_sync

FLUJO_INT = 0
HVE_INFIL = 15
TEMP_ADD_TT = 5
TEMP_ADD_ZTU = 3

densidad_aire = 1.20 #1.225
cp_aire_kj_kgK = 1.005  # kJ/(kg·K)
presion_atmos = 101325
CP_AIRE= 1006


class PyProcessInput:

    def clima_laboral_mask(self, row, climatizado, dia_inicio=1, dia_final=5, hora_inicio=8, hora_final=18):

        dias_laborables = range(dia_inicio, dia_final+1)
        es_laboral = (row['day/week'] in dias_laborables)

        # Manejar horarios que cruzan medianoche (ej: 23 a 5)
        if hora_inicio <= hora_final:
            en_horario = (hora_inicio <= row['hours/week'] <= hora_final)
        else:
            # Horario nocturno que cruza medianoche
            en_horario = (row['hours/week'] >= hora_inicio) or (row['hours/week'] <= hora_final)

        es_climatizado = climatizado
        return int(es_laboral and en_horario and es_climatizado)
    
    """
    This class is responsible for processing the input for the Python calculator.
    """

    def __init__(self, project: Project, enclosure_id, weather_processed: DataFrame, monthly_processed: DataFrame,
                 area=50,
                 window_total_for_areas_py=None,
                 altura=2.5, walls_for_py=None, areas_for_py=None, phi_setHU=0.25, phi_set_DHU=0.6, x_int_aire_T=0.01,
                 G_abs=0, sol_file=None, thermal_bridges_sum=None,db=None):

        self.walls_for_py = walls_for_py
        self.areas_for_py = pd.concat([areas_for_py, pd.DataFrame(
            {' ': [None] * len(areas_for_py)}), window_total_for_areas_py], axis=1)
        self.window_total_for_areas_py = window_total_for_areas_py
        self.FLUJO_INT = FLUJO_INT
        self.HVE_INFIL = HVE_INFIL
        self.TEMP_ADD_TT = TEMP_ADD_TT
        self.TEMP_ADD_ZTU = TEMP_ADD_ZTU
        self.area = area
        self.altura = altura
        self.densidad_aire = densidad_aire
        self.cp_aire_kj_kgK = cp_aire_kj_kgK
        self.presion_atmos = presion_atmos
        self.volumen = self.area * self.altura
        self.clima_df= None

        self.weather_processed = weather_processed
        self.monthly_processed = monthly_processed
        self.project = project

        self.phi_setHU = phi_setHU
        self.phi_set_DHU = phi_set_DHU
        self.x_int_aire_T = x_int_aire_T
        self.G_abs = G_abs

        self.enclosure_id = enclosure_id
        self.sol_file = sol_file
        self.thermal_bridges_sum = thermal_bridges_sum

        self.rho_kg_m3 = 1.225
        self.RAH = 0.41
        self.dt_hr = 3600
        self.Cp_kj_kgK = self.cp_aire_kj_kgK
        self.cp_aire = CP_AIRE
        self.db=db

    def parse_fecha_mixta(self, fecha_str):
        try:
            return parser.parse(fecha_str, dayfirst=True)
        except:
            return pd.NaT

    def hve_wk(self, volumen_m3=150.0, rho_kg_m3=1.225, cp_kj_kgK=1.005, RAH=0.41, dt_h=3600):
        """
        Calcula Hve [W/K] para la ventilación.
          - volumen_m3: volumen de aire [m³]
          - rho_kg_m3: densidad del aire [kg/m³]
          - cp_kj_kgK: calor específico (kJ/(kg·K)) (e.g. 1.005)
          - RAH: renovación de aire por hora (adimensional)
          - dt_s: duración de 1 "ciclo" en segundos (3600 = 1 hora)
        """
        # masa de aire en kg
        masa_kg = volumen_m3 * rho_kg_m3
        # convertir cp a J/(kg·K)
        cp_j_kgK = cp_kj_kgK * 1000

        # Fórmula: (RAH * masa * cp) / dt
        Hve = (RAH * masa_kg * cp_j_kgK) / dt_h
        return Hve

    def cal_ventilacion(self,  rendimiento=0):
        """
        Volumen_m3 viene de la hoja CEEUP,
        rendimiento es un porcentaje (0 a 100) que se saca del
        perfil de ocupacion del Recuperador de calor (coincidiendo con el recinto).
        """

        rho_kg_m3 = self.rho_kg_m3
        RAH = self.RAH
        dt_hr = self.dt_hr
        Cp_kj_kgK = self.Cp_kj_kgK
        masa_kg = self.volumen * rho_kg_m3

        # Ajusta la definición de hve_wk si no la tienes
        # (asumiendo que tu hve_wk(vol, rho, Cp, RAH, dt) ya existe).
        # A modo de ejemplo:
        # Ahora construimos la tabla vertical
        data = {
            'Ventilación': [
                "Volumen m3",
                "rho kg/m3",
                "masa kg",
                "RAH",
                "Cp kj/kgK",
                "dt hr",
                "Hve W/K",
                "rendimiento"
            ],
            'Valor': [
                self.volumen,
                rho_kg_m3,
                masa_kg,
                RAH,
                Cp_kj_kgK,
                dt_hr,
                self.hve_wk(self.volumen, rho_kg_m3, Cp_kj_kgK, RAH, dt_hr),
                rendimiento
            ]
        }
        return pd.DataFrame(data)

    def parametros_termicos(self, enclosure_id, U_c=3.01, area=50, type=1):
        """Parametros termicos para el recinto. U_c tabla CEEUP AH74. area es SUMA(CEEUP!H88:H91)"""
        df_parametros_termicos = pd.DataFrame({
            "hci": [5.0, 2.5, 0.7],
            "hce": [20.0, 20.0, 20.0],
            "hri": [5.13, 5.13, 5.13],
            "hre": [4.14, 4.14, 4.14],
            "Rsi": [0.13, 0.10, 0.17],
            "Rse": [0.04, 0.04, 0.04],
            "U_c": [U_c, None, None],
            "area_piso": [area, None, None],
            "c_int": [10000, None, None],
            "F_ref": [0.5, None, None],
            " ": [None, None, None],
            "f_int": [0.4, None, None],
            "f_sol": [0.1, None, None],
            "f_HC": [1.0, None, None],
            "a_sol": [0.0, None, None],
            "flujo_sky": [0.0, None, None],
            "F_sh": [0.0, None, None],
            "ID_proyecto": [self.project.name_project, None, None],
            "ID_recinto": [enclosure_id, None, None],
            "Informes": [type, None, None],
        })
        return df_parametros_termicos

    def month_name_to_number(self, month_name):
        """Convierte el nombre del mes en español a su número correspondiente (1-12)."""
        # Convert month name to lowercase for case-insensitive comparison
        month_name = month_name.lower() if isinstance(month_name, str) else month_name
        
        # Define a mapping of Spanish month names to numbers
        month_map = {
            'enero': 1, 'january': 1, 'ene': 1, 'jan': 1,
            'febrero': 2, 'february': 2, 'feb': 2,
            'marzo': 3, 'march': 3, 'mar': 3,
            'abril': 4, 'april': 4, 'abr': 4, 'apr': 4,
            'mayo': 5, 'may': 5,
            'junio': 6, 'june': 6, 'jun': 6,
            'julio': 7, 'july': 7, 'jul': 7,
            'agosto': 8, 'august': 8, 'ago': 8, 'aug': 8,
            'septiembre': 9, 'september': 9, 'sep': 9, 'set': 9, 'sept': 9,
            'octubre': 10, 'october': 10, 'oct': 10,
            'noviembre': 11, 'november': 11, 'nov': 11,
            'diciembre': 12, 'december': 12, 'dic': 12, 'dec': 12,
        }
        
        return month_map.get(month_name, month_name)
        
    def cargar_datos_solares(self):
        """Carga y preprocesa el archivo parquet con datos solares.
        
        Returns:
            DataFrame: DataFrame con los datos solares normalizados con columnas 'mes' y 'hora'
        
        Raises:
            Exception: Si el archivo solar no está definido o no es válido
        """
        if self.sol_file is None:
            raise Exception("sol_file debe estar definido y apuntar a un archivo parquet válido.")
            
        # Cargar el archivo parquet
        df_sol = pd.read_parquet(self.sol_file)
        
        # Convertir nombres de meses a números si es necesario
        if 'mes' in df_sol.columns and df_sol['mes'].dtype == 'object':
            df_sol['mes'] = df_sol['mes'].apply(
                lambda x: self.month_name_to_number(x) if isinstance(x, str) else x)
        
        # Generar columna 'mes' si no existe
        if 'mes' not in df_sol.columns:
            df_sol = df_sol.copy()
            df_sol['mes'] = ((df_sol.index // 24) % 12) + 1
        
        # Generar columna 'hora' si no existe
        if 'hora' not in df_sol.columns:
            df_sol['hora'] = (df_sol.index % 24) + 1  # 1 a 24
            
        return df_sol
        
    def aplicar_mapeo_solar(self, resultado_df, df_sol):
        """Aplica el mapeo de datos solares al DataFrame de resultados.
        
        Args:
            resultado_df: DataFrame de resultados a actualizar
            df_sol: DataFrame con datos solares
            
        Returns:
            DataFrame actualizado con los datos solares mapeados
        """
        # Mapear columnas de df_sol a las columnas de resultado_df usando mes y hora
        solar_map = {
            'phi_solar_total_N': 'I_sol_Nv',
            'phi_solar_total_NE': 'I_sol2_NEv',
            'phi_solar_total_E': 'I_sol3_Ev',
            'phi_solar_total_SE': 'I_sol4_SEv',
            'phi_solar_total_S': 'I_sol_Sv',
            'phi_solar_total_SO': 'I_sol6_SOv',
            'phi_solar_total_O': 'I_sol7_Ov',
            'phi_solar_total_NO': 'I_sol8_NOv',
            'phi_solar_total_HR': 'I_sol9_Horizontal',
            'phi_solar_total_CT': 'I_sol10_pisoventilado',
            'phi_sky_vent': 'I_sol11_Ventana',
        }
        
        # Para cada fila de resultado_df, buscar la fila correspondiente en df_sol por mes y hora
        for sol_col, res_col in solar_map.items():
            resultado_df[res_col] = 0
            if sol_col in df_sol.columns:
                for idx, row in resultado_df.iterrows():
                    mes = row['month']
                    hora = row['hours/week']
                    match = df_sol[(df_sol['mes'] == mes) &
                                   (df_sol['hora'] == hora)]
                    if not match.empty:
                        resultado_df.at[idx, res_col] = float(
                            match.iloc[0][sol_col])
                            
        return resultado_df
        
    def calcular_flujo_solar(self, clima_df):
        """
        Calcula el flujo solar para cada hora y mes basado en los datos de ventanas.
        
        Args:
            clima_df: DataFrame con datos climáticos que incluye columnas 'month' y 'hours/week'
            
        Returns:
            DataFrame: El mismo DataFrame de entrada con la columna 'flujo_sol' actualizada
        """
        # Obtener datos de ventanas
        ventanas_df = read_sol_window_parquet(enclosure_id=self.enclosure_id, project_id=self.project.id, db=self.db)


        # Crear un diccionario para mapeo directo
        ventanas_map = {}
        for _, row in ventanas_df.iterrows():
            ventanas_map[(row['month'], row['hour'])] = row['window_w_total']
        
        # Asignar directamente a flujo_sol sin columnas intermedias
        clima_df['flujo_sol'] = 0  # Inicializar con valor por defecto
        for idx, row in clima_df.iterrows():
            key = (row['month'], row['hours/week'])
            if key in ventanas_map:
                clima_df.at[idx, 'flujo_sol'] = ventanas_map[key]
                
        return clima_df

    def weather_calc_humidity(self, df: DataFrame, area: float, num_people=10, human_activity=45,
                              dia_inicio=1, dia_fin=5, hora_inicio=8, hora_fin=18):
        """
        Calcula la humedad interna generada por personas usando g_int_humidity, alineada y ordenada.
        Args:
            df: DataFrame con columnas 'day/week' y 'hours/week'.
            area: Área en m².
            num_people: Número de personas.
            human_activity: Actividad humana (g/h).
            dia_inicio, dia_fin: Rango de días (1=lunes).
            hora_inicio, hora_fin: Rango de horas (1-24).
        Returns:
            Serie de humedad calculada, ordenada desde inicio de año.
        """
        try:
            print(f"weather_calc_humiditu es num_people {num_people}")
            humedad_calc = self.g_int_humidity(
                df,
                area=area,
                human_activity=human_activity,
                num_people=num_people,
                dia_inicio=dia_inicio,
                dia_fin=dia_fin,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin
            )
            return humedad_calc
        except Exception as e:
            print(f"Error al calcular la humedad: {str(e)}")
            return 0
    def calcular_hve_condicional(self, df, m2_pers,r_pers_l_s, alturaxarea_piso=200, dia_inicio=1, dia_fin=5, hora_inicio=8, hora_fin=18):

        # Manejar horarios que cruzan medianoche
        if hora_inicio <= hora_fin:
            cond_hora = df['hours/week'].between(hora_inicio, hora_fin)
        else:
            # Horario nocturno que cruza medianoche
            cond_hora = (df['hours/week'] >= hora_inicio) | (df['hours/week'] <= hora_fin)

        cond = (df['day/week'].between(dia_inicio, dia_fin)) & cond_hora

        hve = Formulas.hve(r_pers_l_s, m2_pers,altura_eq=self.altura, alturaxarea_piso=alturaxarea_piso, ro_aire=self.rho_kg_m3,
                                           cp_aire=self.Cp_kj_kgK, dt_hr=self.dt_hr)
        return np.where(cond, hve, 0)

    def g_int_humidity(self, df, area, human_activity=45, num_people=10,
                       dia_inicio=1, dia_fin=5, hora_inicio=8, hora_fin=18):
        """
        Calcula la humedad interna generada por personas en el rango de días y horas especificado.
        df: DataFrame con columnas 'day/week' y 'hours/week'.
        area: área del recinto.
        human_activity: actividad humana (por defecto 45).
        num_people: número de personas (por defecto 10, ajustado si 0 basado en perfil).
        dia_inicio, dia_fin: rango de días de la semana (1=lunes).
        hora_inicio, hora_fin: rango de horas del día (1-24).
        """
        # Manejar horarios que cruzan medianoche
        if hora_inicio <= hora_fin:
            cond_hora = df['hours/week'].between(hora_inicio, hora_fin)
        else:
            # Horario nocturno que cruza medianoche
            cond_hora = (df['hours/week'] >= hora_inicio) | (df['hours/week'] <= hora_fin)

        cond = (df['day/week'].between(dia_inicio, dia_fin)) & cond_hora

        human_activity = human_activity / 3600000
        try:
            vapor_pressure = (area * human_activity) / num_people
        except Exception as e:
            print(f"Error al calcular la humedad: {str(e)}")
            vapor_pressure=0
        # Devuelve vapor_pressure solo donde cond es True, 0 en el resto
        return pd.Series(np.where(cond, vapor_pressure, 0), index=df.index)

    def build(self, clima_df: DataFrame, monthly: DataFrame):
        """Construye el df_resultado con las columnas de la imagen y reemplaza las columnas solares con datos de sol_file."""

        # Convertir la columna Tiempo a datetime

        is_base_case= False

        areas_piso=get_total_floor_area_by_enclosure_id(self.enclosure_id, self.db)
        clima_df['Tiempo'] = pd.to_datetime(
            clima_df['Tiempo'], dayfirst=True, errors='coerce')
        clima_df_original = clima_df.copy()
        
        # ----- SOLUCIÓN PARA HORAS DUPLICADAS -----
        # 1. Obtener la fecha de inicio del año
        if not clima_df.empty:
            year = clima_df['Tiempo'].dt.year.iloc[0]
            fecha_inicio = pd.Timestamp(year=year, month=1, day=1, hour=0)
        else:
            year = pd.Timestamp.now().year
            fecha_inicio = pd.Timestamp(year=year, month=1, day=1, hour=0)
            
        # 2. Crear un rango completo de fechas para el año (8760 horas)
        fechas_completas = pd.date_range(start=fecha_inicio, periods=8760, freq='H')
        
        # 3. Crear un timeline completo
        timeline_df = pd.DataFrame({'Tiempo': fechas_completas})
        
        # 4. Fusionar el timeline con los datos de clima originales para preservar todas las columnas
        # Primero hacemos left join para mantener todas las fechas del timeline
        clima_df = pd.merge(timeline_df, clima_df_original, on='Tiempo', how='left')
        
        # Generar valores arbitrarios para month, week, day/week, hours/week comenzando desde 1
        # En lugar de usar Tiempo, generamos secuencias de números para cada columna
        
        total_horas = len(clima_df)
        
        # Primero inicializar hours/calc
        clima_df['hours/calc'] = range(1, len(clima_df) + 1)
        clima_df['month'] = ((np.arange(total_horas) // 672) % 12) + 1
        clima_df['week'] = ((np.arange(total_horas) // 168) % 52) + 1
        clima_df['day/week'] = ((np.arange(total_horas) // 24) % 7) + 1
        clima_df['hours/week'] = (np.arange(total_horas) % 24) + 1
        
        # Verificamos que no haya cambios de mes en medio de una semana
        month_changes = clima_df['month'].diff().fillna(0) != 0
        week_at_month_change = clima_df.loc[month_changes, 'week'].values

        # Cargar y procesar el DataFrame de datos solares
        df_sol = self.cargar_datos_solares()
        temp_col = 'Temperatura en 2 metros (Corejida)[label: Temp] [C]'
        clima_df['theta_e;air'] = clima_df_original[temp_col].values
        clima_df = self.aplicar_mapeo_solar(clima_df, df_sol)
        monthly = monthly.set_index('month')
        clima_df['TT'] = clima_df['month'].map(
            lambda m: monthly.loc[m, 'tm'] if m in monthly.index else None)

        resultado = usage_profile(self.enclosure_id, self.db)

        if resultado is None:
            raise Exception(f"No se encontraron resultados para cargas internas para el enclosure con ID {self.enclosure_id}")

        hora_inicio=resultado.get('hora_inicio')
        hora_fin=resultado.get('hora_fin')
        # clima_df = self.aplicar_mapeo_ztu(clima_df) # ZTU
        clima_df['ZTU'] = 0
        clima_df['flujo_HC'] = 0
        clima_df = self.calcular_flujo_solar(clima_df) # flujo_sol
        loads = get_enclosure_internal_loads(self.enclosure_id, self.db)
        logger.info(f"[PyProcessInput] Cargas internas obtenidas para enclosure_id={self.enclosure_id}: {loads}")
        usuarios = loads.get('usuarios')
        calor_latente = loads.get('calor_latente')
        calor_sensible = loads.get('calor_sensible')
        equipos = loads.get('equipos')
        potencia_base = get_enclosure_lightning_by_id(self.enclosure_id, 'potencia_base', self.db).get('value')
        if usuarios is None or usuarios == 0:
            logger.error(f"[PyProcessInput] ERROR: El número de usuarios es cero o nulo para enclosure_id={self.enclosure_id}. No se puede calcular total_cargas_internas.")
            raise ValueError(f"El número de usuarios es cero o nulo para enclosure_id={self.enclosure_id}. Corrige los datos de entrada.")
        total_cargas_internas = (calor_latente + calor_sensible + equipos) / usuarios
        clima_df['flujo_int'] = clima_df['hours/week'].apply(lambda h: Formulas.flujo_interno2(h,potencia_base,total_cargas_internas,hora_inicio=hora_inicio,hora_fin=hora_fin,area_pisos=areas_piso))
        clima_df['CLIMA'] = clima_df.apply(
            lambda row: self.clima_laboral_mask(row, bool(resultado.get('climatizado')),
                                                dia_inicio=int(resultado.get('dia_inicio')),
                                                dia_final=int(resultado.get('dia_fin')),
                                                hora_inicio=hora_inicio,
                                                hora_final=hora_fin), axis=1)

        print(f"Enclosure ID: {self.enclosure_id}")
        r_pers_l_s = get_enclosure_ventilation_flows_by_id(self.enclosure_id, "cauldal_min_salubridad", self.db)
        r_pers_l_s = r_pers_l_s.get("r_pers", 8.8)  # L/s por persona

        m2_pers = get_enclosure_internal_loads_by_id(self.enclosure_id, "usuarios", self.db)
        m2_pers = m2_pers.get("value", None)
        if m2_pers is None:
            raise Exception(
                f"El m2 por persona no está definido para el enclosure con ID {self.enclosure_id}")
        print("Cargas internas de usuarios:", m2_pers)
        print("Caudal min salubridad:", r_pers_l_s)
        m2_pers = float(m2_pers)
        clima_df['Hve'] = self.calcular_hve_condicional(
            clima_df, m2_pers=m2_pers,r_pers_l_s=r_pers_l_s,alturaxarea_piso=self.altura*areas_piso)
        clima_df['Hve_infiltracion'] = Formulas.hve_infiltracion(self.enclosure_id, self.altura, areas_piso, rho_aire=self.rho_kg_m3, cp_aire=self.cp_aire_kj_kgK, db=self.db)

        monthly = monthly.reset_index(drop=True)
        monthly.index = range(1, 13)

        def get_tset_h_by_month(m):
            return monthly.loc[m, 'tn_min'] if m in monthly.index else None

        def get_tset_c_by_month(m):
            return monthly.loc[m, 'tn_max'] if m in monthly.index else None

        clima_df['T_SET_H'] = 20
        clima_df['T_SET_C'] = 27
        temp_clima = clima_df[['CLIMA', 'Hve']].copy()
        clima_df = clima_df.iloc[:, 15:]
        clima_df= self.warmup(clima_df)
        print(f"process_python_input clima_df {clima_df}")
        clima_df.loc[:len(temp_clima) - 1, 'CLIMA'] = temp_clima['CLIMA'].values
        clima_df.loc[:len(temp_clima) - 1, 'Hve'] = temp_clima['Hve'].values
        # del temp_clima
        clima_df['T_SET_H'] = clima_df['month'].apply(
            lambda m: get_tset_h_by_month(m))
        clima_df['T_SET_C'] = clima_df['month'].apply(
            lambda m: get_tset_c_by_month(m))

        potencia = pd.DataFrame({'Potencia_máx': [1000]})
        temp_max = pd.DataFrame({'Temperatura_inicial': [10]})
        resultado_df2 = pd.DataFrame({
            'T_set_h_month': monthly['tn_min'].values,
            'T_set_c_month': monthly['tn_max'].values,
            'Mes': monthly.index,
        })
        ventilacion_df = self.cal_ventilacion()
        htr_wk = pd.DataFrame({'htr_wk': [self.thermal_bridges_sum]})
        df_parametros_termicos = self.parametros_termicos(
            self.enclosure_id, area=self.area)

        print(f"process_python_input - 495 resultado {resultado}")
        calculated_humidity = self.weather_calc_humidity(
            df=clima_df,
            area=self.area,
            num_people=resultado.get('num_people', 0),
            human_activity=resultado.get('human_activity', 0),
            dia_inicio=resultado.get('dia_inicio', 0),
            dia_fin=resultado.get('dia_fin', 0),
            hora_inicio=resultado.get('hora_inicio', 0),
            hora_fin=resultado.get('hora_fin', 0),
        )
        
        print(f"🚀Calculated Humidity: {calculated_humidity}")
        # Handle case when calc_humidity returns a scalar value (0)
        if isinstance(calculated_humidity, (int, float)):
            kgagua_seg = pd.DataFrame({
                'calculated_humidity': [calculated_humidity] * len(clima_df)
            }, index=clima_df.index)
        else:
            kgagua_seg = pd.DataFrame({
                'calculated_humidity': calculated_humidity
            })
        
        humedad_abs = clima_df_original['Humedad Abs kg agua / kg Aire']
        humedad_abs = self.warmup(humedad_abs)
        kgagua_combined = pd.concat(
            [humedad_abs.reset_index(drop=True), kgagua_seg['calculated_humidity'].reset_index(drop=True)], axis=1
        )
        kgagua_combined.columns = ['kgagua_kgaire', 'calculated_humidity']
        kgagua_combined = pd.concat(
            [
                pd.DataFrame({' ': [None] * len(kgagua_combined)}),
                kgagua_combined,
                pd.DataFrame({' ': [None] * len(kgagua_combined)}),
                pd.DataFrame({
                    'Variable': ['densidad_aire', 'cp_aire', 'presion_atmos', 'volumen'],
                    'Valor': [self.densidad_aire, self.cp_aire, self.presion_atmos, self.volumen]
                }),
                pd.DataFrame({' ': [None] * len(kgagua_combined)}),
                pd.DataFrame({"VARIABLE": ["phi_setHU", "phi_set_DHU", "x_int_aire_T-1", "G_abs"],
                              "IDA2": [self.phi_setHU, self.phi_set_DHU, self.x_int_aire_T, self.G_abs]})
            ],
            axis=1
        )
        self.clima_df=clima_df
        self.save_weather_results(clima_df)
        return potencia, temp_max, clima_df, resultado_df2, ventilacion_df, htr_wk, df_parametros_termicos, kgagua_combined
    def save_weather_results(self, df):
        cache = get_redis_sync()
        cache.set(f'project:climate_results:{self.enclosure_id}', pickle.dumps(df))
    def warmup(self,df,iterations=744):
        ultimos = df.tail(iterations)
        return pd.concat([ultimos, df], ignore_index=True)

    def prepare(self):
        logger.info(f"[PyProcessInput] prepare() iniciado para enclosure_id={self.enclosure_id}")
        try:
            potencia, temp_max, df_resultado, resultado_df2, ventilacion_df, htr_wk, parametros_termicos, kgagua_combined = self.build(
                self.weather_processed,
                self.monthly_processed)
            logger.info("[PyProcessInput] build() completado")
            space = pd.DataFrame({' ': [None] * len(df_resultado)})
            self.kgagua_combined=kgagua_combined
            self.df_resultado=df_resultado
            self.space=space
            self.potencia=potencia
            self.temp_max=temp_max
            self.resultado_df2=resultado_df2
            self.ventilacion_df=ventilacion_df
            self.htr_wk=htr_wk
            self.parametros_termicos=parametros_termicos
        except Exception as e:
            import traceback
            logger.error(f"[PyProcessInput] ERROR en prepare() para enclosure_id={self.enclosure_id}: {e}\n{traceback.format_exc()}")
            raise

    def run(self,ztu_df):
        logger.info(f"[PyProcessInput] run() iniciado para enclosure_id={self.enclosure_id}")
        logger.info(
            f"[PyProcessInput] weather_processed: {type(self.weather_processed)}; monthly_processed: {type(self.monthly_processed)}")
        try:
            logger.info("[PyProcessInput] Ejecutando build()...")

            merged_df = self.df_resultado.merge(ztu_df, how='left', left_on=['month', 'hours/week'], right_on=['Mes', 'Hora'])
            self.df_resultado['ZTU'] = merged_df['T RNC'].fillna(self.df_resultado['ZTU'])
            self.sheet_temperature = pd.concat(
                [self.df_resultado, self.space, self.potencia, self.temp_max, self.resultado_df2,
                 self.ventilacion_df,  self.space,  self.htr_wk,  self.space,  self.parametros_termicos], axis=1,
                join='outer')
            self.sheet_humidity = self.kgagua_combined
            self.sheet_areas = self.areas_for_py
            self.sheet_walls = self.walls_for_py
        except Exception as e:
            import traceback
            logger.error(f"[PyProcessInput] ERROR en run() para enclosure_id={self.enclosure_id}: {e}\n{traceback.format_exc()}")
            raise
    def save(self):
        """Save the processed data to an Excel file in a project-specific folder. As public/uploads/<ProjectId>/<EnclosureId>.data.xlsx """
        logger.info(
            f"[PyProcessInput] save() iniciado para enclosure_id={self.enclosure_id}")
        try:
            if not hasattr(self, 'sheet_temperature') or self.sheet_temperature is None or self.sheet_temperature.empty:
                logger.error(f"[PyProcessInput] ERROR: sheet_temperature está vacío o no existe para enclosure_id={self.enclosure_id}")
                raise ValueError("No se puede guardar: sheet_temperature está vacío o no existe")
            if not hasattr(self, 'sheet_humidity') or self.sheet_humidity is None or self.sheet_humidity.empty:
                logger.error(f"[PyProcessInput] ERROR: sheet_humidity está vacío o no existe para enclosure_id={self.enclosure_id}")
                raise ValueError("No se puede guardar: sheet_humidity está vacío o no existe")
            if not hasattr(self, 'sheet_areas') or self.sheet_areas is None or self.sheet_areas.empty:
                logger.error(f"[PyProcessInput] ERROR: sheet_areas está vacío o no existe para enclosure_id={self.enclosure_id}")
                raise ValueError("No se puede guardar: sheet_areas está vacío o no existe")
            if not hasattr(self, 'sheet_walls') or self.sheet_walls is None or self.sheet_walls.empty:
                logger.error(f"[PyProcessInput] ERROR: sheet_walls está vacío o no existe para enclosure_id={self.enclosure_id}")
                raise ValueError("No se puede guardar: sheet_walls está vacío o no existe")

            project_folder = os.path.join(public_folder, str(self.project.id))
            os.makedirs(project_folder, exist_ok=True)
            output_data_file = os.path.join(
                project_folder, f"{self.enclosure_id}.data.xlsx")

            # Guardar los datos en el archivo Excel
            with pd.ExcelWriter(output_data_file, engine='openpyxl') as writer:
                self.sheet_temperature.to_excel(
                    writer, index=False, sheet_name='temperatura')
                self.sheet_humidity.to_excel(
                    writer, index=False, sheet_name='humedad')
                self.sheet_areas.to_excel(
                    writer, index=False, sheet_name='areas')
                self.sheet_walls.to_excel(
                    writer, index=False, sheet_name='muros')

            logger.info(
                f"[PyProcessInput] Archivo guardado en {output_data_file}")
            return output_data_file
        except Exception as e:
            logger.error(
                f" {e}", exc_info=True)
            raise
