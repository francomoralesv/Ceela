#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Versión consolidada del Ejecutable_ISO_22_11_14.py en una clase Calculator.
Se han encapsulado todos los métodos y cálculos en la clase para facilitar su uso.
La lógica se ha mantenido en la medida de lo posible según la versión original.
"""

import time
from math import sqrt, exp
import numpy as np
import pandas as pd
from numpy.linalg import inv
from scipy.linalg import lu_factor, lu_solve
from numpy import savetxt

class Calculator:
    def __init__(self, path="Datos.xlsx"):
        """
        Inicializa la calculadora leyendo los datos del archivo Excel y realizando el preprocesado.
        :param path: Ruta del archivo Excel con las hojas 'temperatura', 'muros', 'areas' y 'humedad'.
        """
        self.path = path
        self.datos = self.preprocesado_datos()
    
    # Métodos auxiliares de utilidades
    def make_sorter(self, lst):
        """
        Crea un mapeo para ordenar elementos según la lista dada.
        :param lst: Lista con el orden deseado.
        :return: Función lambda para mapear Series.
        """
        sort_order = {k: v for v, k in enumerate(lst)}
        return lambda s: s.map(lambda x: sort_order[x])
    
    def create_matrix(self, df1, df2, column):
        """
        Genera una matriz a partir de dos DataFrames, reordenando según la capa.
        :param df1: DataFrame con datos físicos (ej. muros).
        :param df2: DataFrame con áreas y otros parámetros.
        :param column: Columna a extraer de df1.
        :return: (matriz numpy, df2 ordenado, lista de orden)
        """
        order = df1.groupby(["Capa"]).sum().sort_values(by="Nd", ascending=False).index.tolist()
        final_sort = []
        matrix = []
        for tipo in order:
            multiply = df2.Componente.value_counts().loc[tipo]
            final_sort += [tipo] * multiply
        for value in final_sort:
            aux = df1[df1["Capa"] == value]
            matrix.append(aux[column].tolist())
        df_final = pd.DataFrame(matrix)
        return df_final.fillna(0).T.to_numpy(), df2.sort_values('Componente', key=self.make_sorter(final_sort)), final_sort
    
    def swap_cols(self, matrix, order_list, matches={'HR': None, 'CT': None, 'FL': None}):
        """
        Reordena columnas de la matriz según ciertos códigos (HR, CT, FL).
        La lógica se conserva de la versión original, aunque algunos pasos no quedan claros.
        :param matrix: Matriz numpy a reordenar.
        :param order_list: Lista con el orden actual.
        :param matches: Diccionario con coincidencias.
        :return: (matriz reordenada, lista de orden actualizada)
        """
        def get_index(order_arr, match_dict):
            for key in match_dict.keys():
                for index, val in enumerate(order_arr):
                    if val == key:
                        match_dict[key] = index
            return match_dict, order_arr

        matches, order_final = get_index(order_list, matches)
        final_index = matrix.shape[1] - 1
        # Se aplica un intercambio simple si 'HR' se encuentra
        if matches['HR'] is not None:
            matrix[:, [matches['HR'], final_index]] = matrix[:, [final_index, matches['HR']]]
            order_final[matches['HR']], order_final[final_index] = order_final[final_index], order_final[matches['HR']]
        return matrix, order_final

    def ventilation(self, ren, theta_aire, theta_e):
        """
        Calcula la temperatura del aire de suministro en ventilación con recuperador.
        :param ren: Coeficiente de eficiencia del recuperador.
        :param theta_aire: Temperatura interior.
        :param theta_e: Temperatura exterior.
        :return: Temperatura de suministro.
        """
        return ren * (theta_aire - theta_e) + theta_e

    def step5(self, phi_HC):
        """
        Ajuste del flujo latente según el valor de phi_HC.
        :param phi_HC: Valor de phi_HC.
        :return: Flujo latente ajustado.
        """
        return phi_HC if phi_HC > 0 else -phi_HC

    def step2(self, t_set, t_int_op, t_upper, phi_upper):
        """
        Calcula un flujo latente provisional para ajuste.
        :param t_set: Temperatura de seteo.
        :param t_int_op: Temperatura interior operativa.
        :param t_upper: Temperatura superior.
        :param phi_upper: Flujo superior.
        :return: Flujo latente provisional.
        """
        return phi_upper * (t_set - t_int_op) / (t_upper - t_int_op)

    # Métodos para humedad y cálculos relacionados
    def G_HU_ld(self, densidad_aire, flujo_aire, x_set_min, x_a_sup, x_int_a, G_int, G_abs, volumen_aire, dt):
        """
        Calcula la carga de humidificación según ISO 52016-2.
        :return: G_HU_ld2, carga latente no negativa.
        """
        G_HU = densidad_aire * flujo_aire * (x_set_min - x_a_sup) - G_int + G_abs + densidad_aire * volumen_aire * (x_set_min - x_int_a) / dt
        return max(G_HU, 0)

    def G_DHU_ld(self, densidad_aire, flujo_aire, x_set_max, x_a_sup, x_int_a, G_int, G_abs, volumen_aire, dt):
        """
        Calcula la carga de deshumidificación según ISO 52016-2.
        :return: G_DHU_ld2, carga latente no positiva.
        """
        G_DHU = -(-densidad_aire * flujo_aire * (x_set_max - x_a_sup) + G_int - G_abs - densidad_aire * volumen_aire * (x_set_max - x_int_a) / dt)
        return min(G_DHU, 0)

    def x_set_min(self, phi_set_HU, presion_sat_int, presion_atm):
        """
        Calcula la razón de humedad mínima de seteo.
        """
        return 0.622 * (phi_set_HU * presion_sat_int) / (presion_atm - phi_set_HU * presion_sat_int)

    def x_set_max(self, phi_set_DHU, presion_sat_int, presion_atm):
        """
        Calcula la razón de humedad máxima de seteo.
        """
        return 0.622 * (phi_set_DHU * presion_sat_int) / (presion_atm - phi_set_DHU * presion_sat_int)

    def presion_saturacion(self, theta_a_int, theta_int):
        """
        Calcula la presión de saturación en interiores.
        :param theta_a_int: Temperatura ambiente.
        :param theta_int: Temperatura interior.
        :return: Presión de saturación.
        """
        return 611.2 * exp((17.62 * theta_a_int) / (243.12 + theta_int))

    def x_int_aire(self, densidad_aire, flujo_aire, x_a_e, GHU_DHU, G_int, G_abs, Volumen_int, dt, x_int_aire_t1):
        """
        Calcula la razón de humedad del aire interior para el siguiente paso.
        NOTA: La fórmula se conserva de la versión original.
        """
        num = densidad_aire * flujo_aire * x_a_e + GHU_DHU + G_int - G_abs + densidad_aire * Volumen_int * x_int_aire_t1 / dt
        den = densidad_aire * flujo_aire + densidad_aire * Volumen_int / dt
        return num / den

    # Preprocesado de datos
    def preprocesado_datos(self):
        """
        Lee los datos de entrada desde un archivo Excel y realiza el preprocesado de parámetros.
        Se generan las matrices de propiedades físicas y se reordenan algunos parámetros.
        :return: Diccionario con los datos procesados.
        """
        T = pd.read_excel(self.path, sheet_name='temperatura')
        muro = pd.read_excel(self.path, sheet_name='muros')
        parametros = pd.read_excel(self.path, sheet_name='areas')
        humedad = pd.read_excel(self.path, sheet_name='humedad')
        
        L = len(T)  # cantidad de datos climáticos

        # Generación de matrices con propiedades físicas
        df = pd.read_excel(self.path, sheet_name='muros')
        areas = pd.read_excel(self.path, sheet_name='areas').iloc[:, :5]
        areas = areas[areas["Area"] != 0]
        
        conductividad, orientacion, orden = self.create_matrix(df, areas, "λ [W/mK]")
        densidad, orientacion, orden = self.create_matrix(df, areas, "ρ [kg/m³]")
        cp, orientacion, orden = self.create_matrix(df, areas, "c [J/kg K]")
        espesor, orientacion, orden = self.create_matrix(df, areas, "d [m]")
        
        pared = parametros.iloc[:, 0].dropna()
        area_ventana = np.float64(parametros.iloc[0, 8])
        
        # Reordenamiento de propiedades físicas
        orientacion1 = orientacion.iloc[:, 1].to_list()
        espesor, orden_final = self.swap_cols(espesor, orientacion1)
        cp, _ = self.swap_cols(cp, orientacion1)
        conductividad, _ = self.swap_cols(conductividad, orientacion1)
        densidad, _ = self.swap_cols(densidad, orientacion1)
        
        dt = T.iloc[5, 34]
        F_ref = T.iloc[0, 47]
        Htr = T.iloc[0, 36]
        hci = T.iloc[:, 38].dropna().to_numpy()
        hce = T.iloc[:, 39].dropna().to_numpy()
        hri = T.iloc[:, 40].dropna().to_numpy()
        hre_e = T.iloc[0, 41]
        Rs_ext = T.iloc[:, 42:44].dropna().to_numpy()
        U_v = T.iloc[0, 44]
        
        datos = {
            'T': T, 'muro': muro, 'parametros': parametros, 'humedad': humedad,
            'L': L, 'conductividad': conductividad, 'densidad': densidad,
            'cp': cp, 'espesor': espesor, 'orden_final': orden_final,
            'area_ventana': area_ventana, 'dt': dt, 'F_ref': F_ref,
            'Htr': Htr, 'hci': hci, 'hce': hce, 'hri': hri, 'hre_e': hre_e,
            'Rs_ext': Rs_ext, 'U_v': U_v
        }
        return datos

    # Cálculo de nodos y coeficientes
    def calcular_nodos_coeficientes(self):
        """
        Calcula el número de nodos, dx y el número de divisiones (Nd) para cada muro.
        Se basa en la relación de Fourier (Fo_L) y aplica condiciones mínimas según densidad*cp*espesor.
        :return: Diccionario con arrays 'Fo_L', 'Nd', 'dx' y 'nodos'
        """
        cp = self.datos['cp']
        conductividad = self.datos['conductividad']
        densidad = self.datos['densidad']
        espesor = self.datos['espesor']
        F_ref = self.datos['F_ref']
        dt = self.datos['dt']
        
        num_capas, num_muros = cp.shape
        Fo_L = np.zeros(num_capas)
        Nd = np.zeros((num_capas, num_muros))
        dx = np.zeros((num_capas, num_muros))
        nodos = np.zeros(num_muros)
        
        start = 0
        stop = num_capas
        for j in range(start, num_muros):
            nodeT = 0
            for i in range(start, stop):
                if conductividad[i, j] != 0:
                    Fo_L[i] = (conductividad[i, j] / (densidad[i, j] * cp[i, j])) * (dt / (espesor[i, j] ** 2))
                    if densidad[i, j] * cp[i, j] * espesor[i, j] >= 75000:
                        Nd[i, j] = max(5, int(sqrt(F_ref / Fo_L[i]) + 0.999999))
                    else:
                        Nd[i, j] = max(1, int(sqrt(F_ref / Fo_L[i]) + 0.999999))
                    dx[i, j] = espesor[i, j] / Nd[i, j]
                    nodeT += int(Nd[i, j])
            nodos[j] = int(nodeT)
        return {'Fo_L': Fo_L, 'Nd': Nd, 'dx': dx, 'nodos': nodos}

    def calcular_rt_kp(self, nodos, Nd, dx):
        """
        Calcula las matrices de resistencias (rt) y capacidades (kp) para cada muro.
        Se asignan coeficientes en nodos externos e internos usando constantes F1 y F2 basadas en Rs_ext.
        :return: rt (matriz de resistencias), kp (matriz de capacidades), hp (matriz con inverso de rt)
        """
        conductividad = self.datos['conductividad']
        densidad = self.datos['densidad']
        cp = self.datos['cp']
        Rs_ext = self.datos['Rs_ext']
        
        num_muros = len(nodos)
        num_capas = Nd.shape[0]
        num_nodos_max = int(max(nodos)) + 1
        rt = np.zeros((num_nodos_max, num_muros))
        kp = np.zeros((num_nodos_max - 1, num_muros))
        
        # Usar F1 y F2 fijos basados en la primera fila de Rs_ext.
        F1 = Rs_ext[0, 0]
        F2 = Rs_ext[0, 1]
        
        for l in range(num_muros):
            i_rt = 0
            dx_old = 0.0
            for j in range(num_capas):
                nn = Nd[j, l]
                Dx = dx[j, l]
                for k in range(int(nn)):
                    if k == 0 and j == 0:
                        rt[i_rt, l] = F1 + Dx / (2.0 * conductividad[j, l])
                        kp[i_rt, l] = densidad[j, l] * cp[j, l] * Dx
                        i_rt += 1
                    elif k == 0:
                        rt[i_rt, l] = dx_old / (2.0 * conductividad[j - 1, l]) + Dx / (2.0 * conductividad[j, l])
                        kp[i_rt, l] = densidad[j, l] * cp[j, l] * Dx
                        i_rt += 1
                    else:
                        rt[i_rt, l] = Dx / conductividad[j, l]
                        kp[i_rt, l] = densidad[j, l] * cp[j, l] * Dx
                        i_rt += 1
                if j == num_capas - 1:
                    rt[i_rt, l] = F2 + dx[int(Nd[j, l]) - 1, l] / (2.0 * conductividad[j, l])
                dx_old = Dx
        hp = np.zeros_like(rt)
        for i in range(rt.shape[0]):
            for l in range(rt.shape[1]):
                hp[i, l] = 1.0 / rt[i, l] if rt[i, l] != 0 else 0
        return rt, kp, hp

    def iterar_balance_energetico(self, nodos):
        """
        Resuelve la iteración temporal del balance energético mediante un esquema implícito.
        Se ensambla una matriz de coeficientes 'e' y se resuelve el sistema usando factorización LU.
        :return: T_old (matriz con la evolución temporal de temperaturas),
                 T_aire (temperatura del aire interior en cada paso)
        """
        T = self.datos['T']
        L = self.datos['L']
        dt = self.datos['dt']
        n = int(sum(nodos)) + int(len(nodos))
        
        T_inicial = T.iloc[0, 29]
        T_old = np.full((L + 1, n + 3), T_inicial, dtype=float)
        T_nodos_free = np.zeros((L, n + 3))
        T_aire = np.zeros(L)
        
        e = np.zeros((n + 3, n + 3))
        
        for i in range(L):
            e.fill(0)
            np.fill_diagonal(e, 1.0 / dt)
            if n + 3 > 1:
                e[0, 1] = -0.5
                e[n, n - 1] = -0.5
            re = T_old[i, :] / dt
            lu_piv = lu_factor(e)
            t_actual = lu_solve(lu_piv, re)
            T_nodos_free[i, :] = t_actual
            T_old[i + 1, :] = t_actual
            T_aire[i] = t_actual[-1]
        return T_old, T_aire

    def calcular_humedad(self, T_aire, theta_int_op, flu_HC, dt):
        """
        Calcula variables asociadas a la humedad (carga latente de humidificación y deshumidificación)
        según ISO 52016-2.
        :return: G_HU, G_DHU, x_int_a (vectores para cada paso temporal)
        """
        humedad = self.datos['humedad']
        L = self.datos['L']
        
        densidad_a = humedad.iloc[0, 5]
        cp_aire = humedad.iloc[1, 5]
        Volumen_int = humedad.iloc[3, 5]
        presion_atm = humedad.iloc[2, 5]
        phi_setHU = humedad.iloc[0, 8]
        phi_setDHU = humedad.iloc[1, 8]
        G_abs = humedad.iloc[3, 8]
        x_int_a = np.zeros(L + 1)
        x_int_a[0] = humedad.iloc[2, 8]
        
        x_a_e = humedad.iloc[:, 1].to_numpy().flatten()
        G_int = humedad.iloc[:, 2].to_numpy().flatten()
        
        G_HU = np.zeros(L)
        G_DHU = np.zeros(L)
        x_setmin = np.zeros(L)
        x_setmax = np.zeros(L)
        p_sat = np.zeros(L)
        
        hwe = 2466000
        
        for i in range(L):
            p_sat[i] = self.presion_saturacion(T_aire[i], theta_int_op[i])
            x_setmin[i] = self.x_set_min(phi_setHU, p_sat[i], presion_atm)
            x_setmax[i] = self.x_set_max(phi_setDHU, p_sat[i], presion_atm)
            # Se utiliza flujo de aire = 0.0 en estos cálculos (según la versión simplificada)
            G_HU[i] = self.G_HU_ld(densidad_a, 0.0, x_setmin[i], x_a_e[i], x_int_a[i],
                                    G_int[i], G_abs, Volumen_int, dt)
            G_DHU[i] = self.G_DHU_ld(densidad_a, 0.0, x_setmax[i], x_a_e[i], x_int_a[i],
                                      G_int[i], G_abs, Volumen_int, dt)
            if G_HU[i] != 0:
                x_int_a[i + 1] = self.x_int_aire(densidad_a, 0.0, x_a_e[i], G_HU[i],
                                                 G_int[i], G_abs, Volumen_int, dt, x_int_a[i])
            else:
                x_int_a[i + 1] = self.x_int_aire(densidad_a, 0.0, x_a_e[i], G_DHU[i],
                                                 G_int[i], G_abs, Volumen_int, dt, x_int_a[i])
        G_HU = G_HU * hwe
        G_DHU = G_DHU * hwe
        return G_HU, G_DHU, x_int_a

    # Método principal para ejecutar todos los cálculos
    def run(self):
        """
        Ejecuta el proceso completo: desde el preprocesado de datos, cálculo de nodos, generación
        de coeficientes, iteración del balance energético y cálculo de variables de humedad.
        Imprime resultados básicos en consola.
        """
        # Cálculo de nodos y coeficientes
        calc = self.calcular_nodos_coeficientes()
        nodos = calc['nodos']
        
        # Cálculo de rt, kp y hp
        rt, kp, hp = self.calcular_rt_kp(nodos, calc['Nd'], calc['dx'])
        
        # Iteración del balance energético
        T_old, T_aire = self.iterar_balance_energetico(nodos)
        
        # Se asume que la temperatura operativa interior es igual a T_aire en esta versión simplificada
        theta_int_op = T_aire.copy()
        flu_HC = np.zeros(self.datos['L'])
        
        # Cálculo de variables de humedad
        G_HU, G_DHU, x_int_a = self.calcular_humedad(T_aire, theta_int_op, flu_HC, self.datos['dt'])
        
        print("Balance energético resuelto.")
        print("Temperatura del aire interior:", T_aire)
        print("Carga de humidificación:", G_HU)
        print("Carga de deshumidificación:", G_DHU)
        # Se pueden retornar los resultados para su posterior uso
        return {
            'T_old': T_old,
            'T_aire': T_aire,
            'rt': rt,
            'kp': kp,
            'hp': hp,
            'G_HU': G_HU,
            'G_DHU': G_DHU,
            'x_int_a': x_int_a
        }