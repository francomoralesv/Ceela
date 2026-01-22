import os

import numpy as np
import pandas as pd

from .energy_balance import OutputCalculations
from .parameters import Parameters
from .const import get_muros, muros2, muros3, muros4, output_format
from .sanitize_variables import SanitizeVariablesDTO

init_row = 0
end_row = 8761
class OutputProcessor:
    def __init__(self, output_name, output_calc: OutputCalculations, variables: SanitizeVariablesDTO,
                 params: Parameters, ordenfinal, nodos, c_interior):
        """
        Inicializa el procesador de salida con los datos principales y todas
        las variables requeridas que anteriormente estaban en ámbito global.

        Parámetros:
            output: Matriz de salida a ser procesada.
            T: DataFrame con datos temporales.
            humedad: DataFrame con datos de humedad y otros parámetros.
            ID2: Identificador del recinto.

            [Parámetros relacionados con el flujo y cálculos energéticos]
            Hve, Hve_i, dt: Variables para el cálculo del flujo de aire.
            T_aire, theta_int_op, T_aire2, theta_int_op2, t_e: Variables de temperaturas.
            theta_sup, theta_sup2: Variables de temperaturas superficiales.
            flu_HC, flu_int, flu_sol: Flujos de calor (HC, interior y solar).
            NORTE, NORESTE, ESTE, SURESTE, SUR, SUROESTE, OESTE, NOROESTE: Orientaciones.
            HORIZONTAL, PHISOL_DIF, PHISOL_VENTANA: Otras variables geométricas/físicas.
            theta_C_set, theta_H_set, area: Variables de ajustes y áreas.

            [Variables de propiedades de materiales]
            conductividad, cp, espesor, densidad, c_interior, a_sol, dx, e,
            f_HC, f_int, F_ref, F_sh, f_sol,
            hce, hce_v, hci, hci_v, hre, hri, Htr, he, hi,
            hpl, kpl, hpl_v, kpl_v,
            Nd, nodos2, pot_max, ren, Rg, Rs_ext, U_v,

            [Variables adicionales]
            CLIMA, T_old, T_old4: Variables para acondicionamiento térmico y matrices.
            ordenfinal, nodos, area_ventana: Variables para el procesamiento de muros.
        """
        # Variables de entrada principales
        self.output_calc = output_calc
        self.output_name = output_name
        self.ordenfinal = ordenfinal
        self.nodos = nodos

        self.muros2 = None
        self.muros4 = None
        self.muros3 = None
        self.output2 = None
        self.output4 = None
        self.muros = None
        self.variables = variables
        self.params = params
        self.c_interior = c_interior
        self.e = None
        self.output_path = '.'
    def set_output_path(self, output_path):
        """
        Establece la ruta de salida para los archivos generados.
        """
        self.output_path = output_path
    @staticmethod
    def f_list(var, output, contador):
        """
        Inserta la lista 'var' en la columna 'contador' de la matriz 'output'.
        """
        for i, value in enumerate(var):
            output[i, contador] = value
        contador += 1
        return output, contador

    @staticmethod
    def f_list2(var, output, contador, desplazamiento):
        """
        Inserta la lista 'var' desplazada en 'desplazamiento' en la columna 'contador' de 'output'.
        """
        for i in range(len(var) - desplazamiento):
            output[i, contador] = var[i + desplazamiento]
        contador += 1
        return output, contador

    @staticmethod
    def f_2d(var, output, contador):
        """
        Inserta una matriz 2D 'var' en 'output', comenzando en la columna 'contador'.
        """
        num_filas, num_cols = var.shape
        for j in range(num_cols):
            output[:num_filas, j + contador] = var[:, j]
        contador += num_cols
        return output, contador

    @staticmethod
    def f_var(var, output, contador):
        """
        Inserta un valor escalar 'var' en 'output' en la posición [0, contador].
        Convierte cadenas con porcentajes ('0%') a flotantes.
        """
        if isinstance(var, str) and '%' in var:
            var = float(var.replace('%', '')) / 100  # Eliminar '%' y convertir a decimal
        output[0, contador] = var
        contador += 1
        return output, contador

    @staticmethod
    def G_HU_ld(densidad_aire, flujo_aire, x_set_min, x_a_sup, x_int_a, G_int, G_abs, volumen_aire, dt):
        """
        Calcula la carga de calor latente para humidificación.
        """
        G_HU = (densidad_aire * flujo_aire * (x_set_min - x_a_sup) -
                G_int + G_abs +
                densidad_aire * volumen_aire * (x_set_min - x_int_a) / dt)
        return max(G_HU, 0)

    @staticmethod
    def G_DHU_ld(densidad_aire, flujo_aire, x_set_max, x_a_sup, x_int_a, G_int, G_abs, volumen_aire, dt):
        """
        Calcula la carga de calor latente para deshumidificación.
        """
        G_DHU = -(-densidad_aire * flujo_aire * (x_set_max - x_a_sup) +
                  G_int - G_abs -
                  densidad_aire * volumen_aire * (x_set_max - x_int_a) / dt)
        return min(G_DHU, 0)

    @staticmethod
    def x_set_min(phi_set_HU, presion_sat_int, presion_atm):
        """
        Calcula la fracción de humedad mínima (x_set_min).
        """
        return 0.622 * (phi_set_HU * presion_sat_int) / (presion_atm - phi_set_HU * presion_sat_int)

    @staticmethod
    def x_set_max(phi_set_DHU, presion_sat_int, presion_atm):
        """
        Calcula la fracción de humedad máxima (x_set_max).
        """
        return 0.622 * (phi_set_DHU * presion_sat_int) / (presion_atm - phi_set_DHU * presion_sat_int)

    @staticmethod
    def presion_saturacion(theta_a_int, theta_int):
        """
        Calcula la presión de saturación interna según la temperatura.
        """
        return 611.2 * np.exp((17.62 * theta_a_int) / (243.12 + theta_int))

    @staticmethod
    def x_int_aire(densidad_aire, flujo_aire, x_a_e, GHU_DHU, G_int, G_abs, volumen_int, dt, x_int_aire_t1):
        """
        Calcula la fracción interna de aire (x_int_aire).
        """
        numerador = (densidad_aire * flujo_aire * x_a_e +
                     GHU_DHU + G_int - G_abs +
                     densidad_aire * volumen_int * x_int_aire_t1 / dt)
        denominador = (densidad_aire * flujo_aire +
                       densidad_aire * volumen_int / dt)
        return numerador / denominador

    def creating_headers(self, type: str, nodes, ordenfinal, area_ventana):

        print(f"[Calculator engine] Headers de salida: type {type} with nodes {len(nodes)}")

        if type == 0:
            headers = muros3
            headers2 = None
        elif type == 1:
            headers = muros2
            headers2 = muros4
        elif type == 2:
            headers = get_muros(nodes, ordenfinal, area_ventana, self.e)
            headers2 = muros4
        return headers, headers2, type

    def process(self, type_project, hp, hi, hpl, kpl):
        """
        Procesa y organiza los datos de entrada para calcular variables de humedad y otros parámetros.
        Se asume que los parámetros necesarios se definieron en el constructor.
        """
        T = self.variables.T
        humedad = self.variables.humedad
        L = self.variables.L

        ID_Recinto = []
        for i in range(0, L):
            ID_Recinto.append(self.params.ID2)
        # Extraer columnas del DataFrame T
        hora = T.iloc[:, 4]
        dia = T.iloc[:, 3]
        mes = T.iloc[:, 1]

        # Extraer parámetros del DataFrame 'humedad'
        densidad_a = humedad.iloc[0, 5]
        cp_aire = humedad.iloc[1, 5]
        Volumen_int = humedad.iloc[3, 5]
        presion_atm = humedad.iloc[2, 5]
        phi_setHU = humedad.iloc[0, 8]
        phi_setDHU = humedad.iloc[1, 8]
        G_abs = humedad.iloc[3, 8]
        x_int_aire_t1 = humedad.iloc[2, 8]
        x_a_e = humedad.iloc[:, 1]
        G_int = humedad.iloc[:, 2]
        hwe = 2466000

        # Cálculo del flujo de aire (en m3/s) usando variables declaradas en el constructor
        flujo_aire = (self.params.Hve + self.params.Hve_i) / (cp_aire * densidad_a)

        # Inicializar vectores para los cálculos
        G_HU = np.zeros(L)
        G_DHU = np.zeros(L)
        x_setmin = np.zeros(L)
        x_setmax = np.zeros(L)
        p_sat = np.zeros(L)
        x_int_a = np.zeros(L + 1)
        x_int_a[0] = x_int_aire_t1

        n = int(sum(self.params.nodos)) + int(self.params.lenpared)
        self.e = np.zeros([n + 3, n + 3])
        # Cálculo de variables de humedad según ISO52016-1 (cap. 6.5.14)
        for i in range(L):
            p_sat[i] = self.presion_saturacion(self.output_calc.T_aire[i], self.output_calc.theta_int_op[i])
            x_setmin[i] = self.x_set_min(phi_setHU, p_sat[i], presion_atm)
            x_setmax[i] = self.x_set_max(phi_setDHU, p_sat[i], presion_atm)
            G_HU[i] = self.G_HU_ld(densidad_a, flujo_aire[i], x_setmin[i],
                                   x_a_e[i], x_int_a[i], G_int[i], G_abs,
                                   Volumen_int, self.params.dt)
            G_DHU[i] = self.G_DHU_ld(densidad_a, flujo_aire[i], x_setmax[i],
                                     x_a_e[i], x_int_a[i], G_int[i], G_abs,
                                     Volumen_int, self.params.dt)

            x_int_a[i + 1] = self.x_int_aire(densidad_a, flujo_aire[i],
                                             x_a_e[i], G_HU[i] if G_HU[i] != 0 else G_DHU[i],
                                             G_int[i], G_abs,
                                             Volumen_int, self.params.dt,
                                             x_int_a[i])

        # Conversión de unidades para las cargas de calor latente
        G_HU = G_HU * hwe
        G_DHU = G_DHU * hwe
        G_HU = self.params.CLIMA * G_HU
        G_DHU = self.params.CLIMA * G_DHU
        x_int_a[1:8761] = self.params.CLIMA*x_int_a[1:8761]

        # Copiar datos en 'output' usando T_old y T_old4
        for i in range(len(self.output_calc.e)):
            self.output_calc.output[0:9504, i] = self.output_calc.T_old[1:9505, i]
            self.output_calc.output[0:9504, i + len(self.output_calc.e)] = self.output_calc.T_old4[1:9505, i]

        # Redondear ciertos arrays
        self.theta_int_op = np.round(self.output_calc.theta_int_op, 2)
        self.theta_int_op2 = np.round(self.output_calc.theta_int_op2, 2)
        self.flu_HC = np.round(self.params.flu_HC, 2)
        promedios = self.get_average(T, G_HU, G_DHU)

        ID_Recinto = []
        for i in range(0, L):
            ID_Recinto.append(self.params.ID2)
        self.process_by_type(type_project, promedios, ID_Recinto, hora, dia, mes, p_sat, hp, hi, hpl, kpl, x_setmin,
                             x_setmax, x_int_a, G_HU, G_DHU)

    def get_average(self, T, G_HU, G_DHU):
        df2 = T.iloc[init_row:end_row, 0:6].reset_index()
        vectores = np.array(
            [self.theta_int_op2[init_row:end_row], self.theta_int_op[init_row:end_row], self.flu_HC[init_row:end_row], G_HU[init_row:end_row],
             G_DHU[init_row:end_row]]).T
        df3 = pd.DataFrame(vectores,
                           columns=['Temperatura op free float', 'Temperatura op', 'Demanda', 'G_HU', 'G_DHU'])

        df4 = pd.concat([df2, df3], axis=1)
        promedios = df4.groupby(['month', 'hours/week']).mean()
        return promedios.reset_index()

    def process_by_type(self, type: int, promedios, ID_Recinto, hora, dia, mes, p_sat, he, hi, hpl, kpl, x_setmin,
                        x_setmax, x_int_a, G_HU, G_DHU):
        print(f"[process_by_type] Starting processing with type: {type}")
        headers, headers2, project_type = self.creating_headers(self.params.Informes, self.nodos, self.ordenfinal,
                                                                self.variables.area_ventana)
        print(f"[process_by_type] Headers created for type {type}: {headers}")

        if type == 0:
            print("[process_by_type] Processing type 0")
            output = np.zeros([promedios.shape[0], 9])
            count = 0
            output, count = self.f_list2(ID_Recinto[0:promedios.shape[0]], output, count, 0)
            print(f"[process_by_type] ID_Recinto processed, count: {count}")
            output[:, 1:3] =  promedios.iloc[:,0:2]
            output[:, 3:7] =promedios.iloc[:,6:10].round(2)
            output[:, 7:9] = promedios.iloc[:,10:12].round(4)
            print(f"[process_by_type] Promedios processed for type 0")
            self.__write_report(self.output_name + "_simple_promedios" + output_format, headers, output, '%1.2f')

        elif type == 1:
            print("[process_by_type] Processing type - Informe Simple")
            count = 0
            listas2 = [ID_Recinto, hora, dia, mes, self.params.t_e,
                       self.theta_int_op2, self.theta_int_op, self.flu_HC,
                       self.params.flu_sol, G_HU, G_DHU]
            output = np.zeros([self.variables.L, len(listas2)])
            for lista in listas2:
                output, count = self.f_list2(lista, output, count, 0)
                print(f"[process_by_type] Processed list for type - Informe Simple, count: {count}")
            self.__write_report(self.output_name + "_simple" + output_format, headers, output, '%1.2f')

        elif type == 2:
            print("[process_by_type] Processing type 2")
            contador = len(self.output_calc.e) * 2
            listas = [ID_Recinto, hora, dia, mes,
                      self.output_calc.T_aire, self.output_calc.T_aire2, self.params.t_e,
                      self.output_calc.theta_int_op, self.output_calc.theta_int_op2, self.output_calc.theta_sup,
                      self.output_calc.theta_sup2, self.params.flu_HC, self.params.flu_int, self.params.flu_sol,
                      self.params.Hve, self.params.Hve_i, self.params.NORTE, self.params.NORESTE, self.params.ESTE,
                      self.params.SURESTE, self.params.SUR, self.params.SUROESTE, self.params.OESTE,
                      self.params.NOROESTE,
                      self.params.HORIZONTAL, self.params.PHISOL_DIF, self.params.PHISOL_VENTANA,
                      self.output_calc.theta_C_set, self.output_calc.theta_H_set, self.output_calc.area]
            for lista in listas:
                self.output, contador = self.f_list(lista, self.output_calc.output, contador)
                print(f"[process_by_type] Processed list for type 2, contador: {contador}")

            matrices_2d = [self.variables.conductividad, self.variables.cp, self.variables.espesor,
                           self.variables.densidad]
            for matriz in matrices_2d:
                self.output, contador = self.f_2d(matriz, self.output, contador)
                print(f"[process_by_type] Processed 2D matrix for type 2, contador: {contador}")

            escalares = [self.c_interior, self.params.dt, self.params.a_sol]
            for escalar in escalares:
                self.output, contador = self.f_var(escalar, self.output, contador)
                print(f"[process_by_type] Processed scalar for type 2, contador: {contador}")

            output, contador = self.f_2d(self.params.dx, self.output, contador)
            output, contador = self.f_2d(self.output_calc.e, self.output, contador)
            output, contador = self.f_var(self.params.f_HC, self.output, contador)
            output, contador = self.f_var(self.params.f_int, self.output, contador)
            output, contador = self.f_var(self.params.F_ref, self.output, contador)
            output, contador = self.f_var(self.params.F_sh, self.output, contador)
            output, contador = self.f_var(self.params.f_sol, self.output, contador)
            output, contador = self.f_list(self.params.hce, self.output, contador)
            output, contador = self.f_var(self.params.hce_v, self.output, contador)
            output, contador = self.f_list(self.params.hci, self.output, contador)
            output, contador = self.f_var(self.params.hci_v, self.output, contador)
            output, contador = self.f_list(self.params.hre, self.output, contador)
            output, contador = self.f_list(self.params.hri, self.output, contador)
            output, contador = self.f_var(self.params.Htr, self.output, contador)
            output, contador = self.f_list(he.flatten(), self.output, contador)
            output, contador = self.f_list(hi, self.output, contador)
            output, contador = self.f_2d(hpl, self.output, contador)
            output, contador = self.f_2d(kpl, self.output, contador)
            output, contador = self.f_var(self.params.hpl_v, self.output, contador)
            output, contador = self.f_list(self.params.kpl_v, self.output, contador)
            output, contador = self.f_2d(self.params.Nd, self.output, contador)
            output, contador = self.f_list(self.output_calc.nodos2, self.output, contador)
            output, contador = self.f_var(self.output_calc.pot_max, self.output, contador)
            output, contador = self.f_var(self.params.ren, self.output, contador)
            output, contador = self.f_var(self.output_calc.Rg, self.output, contador)
            output, contador = self.f_2d(self.params.Rs_ext, self.output, contador)
            output, contador = self.f_var(self.params.U_v, self.output, contador)
            print(f"[process_by_type] Completed processing for type 2, final contador: {contador}")
            self.__write_report(self.output_name + "_completo" + output_format, headers, output, '%1.2f')

        if type == 1 or type == 2:
            print(f"[process_by_type] Processing additional output for type {type}")
            output2 = np.zeros([self.variables.L , 10])
            contador4 = 0
            output2, contador4 = self.f_list2(ID_Recinto, output2, contador4, 0)
            output2, contador4 = self.f_list2(hora, output2, contador4, 0)
            output2, contador4 = self.f_list2(dia, output2, contador4, 0)
            output2, contador4 = self.f_list2(mes, output2, contador4, 0)
            output2, contador4 = self.f_list2(p_sat, output2, contador4, 0)
            output2, contador4 = self.f_list2(x_setmin, output2, contador4, 0)
            output2, contador4 = self.f_list2(x_setmax, output2, contador4, 0)
            output2, contador4 = self.f_list2(x_int_a, output2, contador4, 0)
            output2, contador4 = self.f_list2(G_HU, output2, contador4, 0)
            output2, contador4 = self.f_list2(G_DHU, output2, contador4, 0)
            print(f"[process_by_type] Completed additional output for type {type}, final contador4: {contador4}")
            df = self.__write_report(self.output_name + "_humedad" + output_format, headers2, output2, '%1.6f')
            print(f"Result dataframe {df}")

    def __write_report(self, file_name, headers, data, fmt):
        full_path = os.path.join(self.output_path, file_name)
        mode = "a" if os.path.exists(full_path) else "w"
        with open(full_path, mode) as file:
            if mode == "w":
                file.write(" ".join(headers) + "\n")
            print(f"[Calculator engine] Generando archivo de salida {full_path}")
            np.savetxt(file, data, fmt=fmt)
        return data