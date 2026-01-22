from math import sqrt
import numpy as np

from .parameters import Parameters
from .utils import process_shape
from .sanitize_variables import SanitizeVariablesDTO


class VectorProcessor:

    def __init__(self, matches, variables: SanitizeVariablesDTO):
        self.matches = matches
        self.espesor = variables.espesor
        self.cp = variables.cp
        self.conductividad = variables.conductividad
        self.orientation = variables.orientacion.iloc[:, 1].to_list()
        self.orientation_copy = variables.orientacion.copy()
        self.areas = variables.areas
        self.parametros = variables.parametros
        self.densidad = variables.densidad
        self.area_ventana = variables.area_ventana
        self.calculated_area = None

    def get_index(self, order_array):
        for i in self.matches.keys():
            for index, j in enumerate(order_array):
                if j == i:
                    self.matches[i] = index
        return self.matches, order_array

    def swap_cols(self, matrix, order_list):
        roof = None
        matches, order_final = self.get_index(order_list)
        floor = []
        for key, val in matches.items():
            if key == 'HR':
                roof = val
            else:
                if val != None:
                    floor.append([key, val])
        final_index = matrix.shape[1] - 1
        if len(floor) == 1:
            floor = floor[0][1]
            if floor == final_index:
                if roof != None:
                    matrix[:, [roof, final_index - 1]] = matrix[:, [final_index - 1, roof]]
                    # mover el techo al penultimo lugar
                    order_final[roof], order_final[final_index - 1] = order_final[final_index - 1], order_final[roof]
            elif floor != final_index and roof == final_index:
                if floor == final_index - 1:
                    matrix[:, [floor, roof]] = matrix[:, [roof, floor]]
                    # mover el techo por el piso
                    order_final[roof], order_final[floor] = order_final[floor], order_final[roof]
                else:
                    matrix[:, [roof, final_index - 1]] = matrix[:, [final_index - 1, roof]]
                    matrix[:, [floor, roof]] = matrix[:, [roof, floor]]
                    # mover el techo por el penultimo y luego el piso por el penultimo
                    order_final[roof], order_final[final_index - 1] = order_final[final_index - 1], order_final[roof]
                    order_final[roof], order_final[floor] = order_final[floor], order_final[roof]
            elif floor != final_index and roof == None:
                matrix[:, [floor, final_index]] = matrix[:, [final_index, floor]]
                order_final[floor], order_final[final_index] = order_final[final_index], order_final[floor]
            else:
                matrix[:, [floor, final_index]] = matrix[:, [final_index, floor]]
                matrix[:, [roof, final_index - 1]] = matrix[:, [final_index - 1, roof]]
                order_final[floor], order_final[final_index] = order_final[final_index], order_final[floor]
                order_final[roof], order_final[final_index - 1] = order_final[final_index - 1], order_final[roof]

        elif len(floor) == 2:
            """CT,FL,HR --- HR,FL,CT"""
            floor_ct = matches['CT']
            floor_fl = matches['FL']
            if floor_ct == final_index:
                if floor_fl == final_index - 1:
                    pass
                else:
                    matrix[:, [floor_fl, final_index - 1]] = matrix[:, [final_index - 1, floor_fl]]
                    order_final[floor_fl], order_final[final_index - 1] = order_final[final_index - 1], order_final[
                        floor_fl]
                    matches, _ = self.get_index(order_final)
                    floor_fl = matches['FL']
                    roof = matches['HR']
                if roof != None:
                    matrix[:, [roof, final_index - 2]] = matrix[:, [final_index - 2, roof]]
                    order_final[roof], order_final[final_index - 2] = order_final[final_index - 2], order_final[roof]
                    matches, _ = self.get_index(order_final)
                    floor_fl = matches['FL']
                    roof = matches['HR']
            else:
                matrix[:, [floor_ct, final_index]] = matrix[:, [final_index, floor_ct]]
                order_final[floor_ct], order_final[final_index] = order_final[final_index], order_final[floor_ct]
                matches, _ = self.get_index(order_final)
                floor_fl = matches['FL']
                roof = matches['HR']
                if floor_fl == final_index - 1:
                    pass
                else:
                    matrix[:, [floor_fl, final_index - 1]] = matrix[:, [final_index - 1, floor_fl]]
                    order_final[floor_fl], order_final[final_index - 1] = order_final[final_index - 1], order_final[
                        floor_fl]
                    matches, _ = self.get_index(order_final)
                    floor_fl = matches['FL']
                    roof = matches['HR']
                if roof != None:
                    matrix[:, [roof, final_index - 2]] = matrix[:, [final_index - 2, roof]]
                    order_final[roof], order_final[final_index - 2] = order_final[final_index - 2], order_final[roof]
                    matches, _ = self.get_index(order_final)
                    floor_fl = matches['FL']
                    roof = matches['HR']
        else:
            if roof != None:
                matrix[:, [roof, final_index - 2]] = matrix[:, [final_index - 2, roof]]
                order_final[roof], order_final[final_index - 2] = order_final[final_index - 2], order_final[roof]
                matches, _ = self.get_index(order_final)
                floor_fl = matches['FL']
                roof = matches['HR']
        return matrix, order_final

    def order(self):
        ##Funcion para corregir el orden de los elementos que lo necesiten
        data = self.espesor
        espesor, ordenfinal = self.swap_cols(data, self.orientation_copy)

        data = self.cp
        data2 = self.orientation.copy()
        cp, ordenfinal = self.swap_cols(data, data2)
        data = self.conductividad
        data2 = self.orientation.copy()
        conductividad, ordenfinal = self.swap_cols(data, data2)
        data = self.densidad
        data2 = self.orientation.copy()
        densidad, ordenfinal = self.swap_cols(data, data2)

        temperaturapared = []
        area = []
        for i in range(0, len(self.areas)):
            for j in range(0, len(self.areas)):
                if ordenfinal[i] == self.areas.iloc[j, 1]:
                    area.append(self.areas.iloc[j, 2])
                    temperaturapared.append(self.areas.iloc[j, 3])
        self.calculated_area = np.append(area, self.area_ventana)
        temperaturapared.append(self.parametros.iloc[0, 9])

        Atot = 0.0
        for i in range(0, len(area)):
            Atot += area[i]

        return area, temperaturapared, ordenfinal, Atot

    async def create_vectors(self, params: Parameters):
        # Crea cantidad de nodos y dx para cada muro
        for j in range(params.start, len(self.calculated_area) - 1):
            nodeT = 0
            for i in range(params.start, params.stop):
                if self.conductividad[i, j] != 0:
                    params.Fo_L[i] = (self.conductividad[i, j] / (self.densidad[i, j] * self.cp[i, j])) * (
                            params.dt / (self.espesor[i, j] ** 2))
                    min_nodos = 5 if self.densidad[i, j] * self.cp[i, j] * self.espesor[i, j] >= 75000 else 1
                    params.Nd[i, j] = max(min_nodos, int(sqrt(params.F_ref / params.Fo_L[i]) + 0.999999))
                    params.dx[i, j] = self.espesor[i, j] / params.Nd[i, j]
                    nodeT += int(params.Nd[i, j])
            params.nodos[j] = int(nodeT)
        return params.nodos

    async def calc_resistances_coefficients(self,params: Parameters,variables:SanitizeVariablesDTO,ordenfinal,temperaturapared):
        """
        Calcula las resistencias térmicas (rt), coeficientes de conductividad (kp),
        coeficientes de transferencia de calor (hpl, kpl) y otros valores relacionados.

        Parámetros:
        - lenpared: Número de paredes.
        - start, stop: Límites de iteración para los nodos.
        - nodos: Vector con el número de nodos por pared.
        - dx: Espaciado entre nodos.
        - conductividad, densidad, cp: Propiedades térmicas de los materiales.
        - T: Datos de entrada (como DataFrame).
        - Rs_ext: Resistencia superficial externa.
        - hre_e, hri: Coeficientes de transferencia de calor radiativa.
        - hci, hce: Coeficientes de transferencia de calor convectiva.
        - ordenfinal: Orden de las paredes.
        - temperaturapared: Tipos de temperatura de las paredes.

        Retorna:
        - rt: Matriz de resistencias térmicas.
        - kp: Matriz de coeficientes de conductividad.
        - hpl: Matriz de coeficientes de transferencia de calor (sin superficies internas/externas).
        - kpl: Matriz de coeficientes de conductividad con aire interior.
        - hi, he: Coeficientes de transferencia de calor para superficies internas y externas.
        """

        lenpared = params.lenpared
        start = params.start
        stop = params.stop
        nodos = params.nodos
        densidad=variables.densidad
        conductividad=variables.conductividad
        dx = params.dx
        cp = variables.cp
        T = variables.T
        Rs_ext = params.Rs_ext
        hre_e = params.hre_e
        hri = params.hri
        hci = params.hci
        hce = params.hce
        Nd = params.Nd
        hre= params.hre
        largo = np.zeros(lenpared)
        for l in range(len(largo)):
            k = 0
            for i in range(start, stop):
                if conductividad[i, l] != 0:
                    k += 1
            largo[l] = k

        rt = np.zeros([(int(max(nodos)) + 1), lenpared])
        kp = np.zeros([int(max(nodos)), lenpared])

        F1 = 0
        F2 = 0
        for l in range(lenpared):
            i = 0
            dx_old = 0.0
            if temperaturapared[l] == "TE" and ordenfinal[l] == "HR":
                F1 = Rs_ext[1, 0]
                F2 = Rs_ext[1, 1]
                hre[l] = hre_e
            elif ordenfinal[l] == "FL":
                F1 = Rs_ext[2, 0]
                F2 = Rs_ext[2, 1]
                hre[l] = hre_e
            elif ordenfinal[l] == "CT":
                F1 = Rs_ext[2, 0]
                F2 = Rs_ext[2, 1]
                hre[l] = 0
            elif temperaturapared[l] == "TE":
                F1 = Rs_ext[0, 0]
                F2 = Rs_ext[0, 1]
                hre[l] = hre_e
            elif temperaturapared[l] in ["ZTC", "ZTU"]:
                F1 = Rs_ext[0, 0]
                F2 = Rs_ext[0, 0]
                hre[l] = hri[1]

            for j in range(start, stop):
                nn = Nd[j, l]
                Dx = dx[j, l]
                for k in range(int(nn)):
                    if k == 0 and j == start:
                        rt[i, l] = F1 + Dx / (2.0 * conductividad[j, l])
                        kp[i, l] = densidad[j, l] * cp[j, l] * Dx
                        i += 1
                    elif k == 0:
                        rt[i, l] = dx_old / (2.0 * conductividad[j - 1, l]) + Dx / (2.0 * conductividad[j, l])
                        kp[i, l] = densidad[j, l] * cp[j, l] * Dx
                        i += 1
                    else:
                        rt[i, l] = Dx / conductividad[j, l]
                        kp[i, l] = densidad[j, l] * cp[j, l] * Dx
                        i += 1

                if j == stop - 1:
                    rt[i, l] = F2 + dx[int(largo[l] - 1), l] / (2.0 * conductividad[int(largo[l] - 1), l])

                dx_old = Dx

        hp = process_shape(rt)
        hi = hp[0, :]
        he = np.zeros(lenpared)
        for i in range(lenpared):
            if ordenfinal[i] == "HR":
                hi[i] = hci[0]
                he[i] = hce[0]
            elif ordenfinal[i] in ["FL", "CT"]:
                hi[i] = hci[1]
                he[i] = hce[2]
            else:
                hi[i] = hci[1]
                he[i] = hce[1]

        hpl = np.delete(hp, 0, 0)
        for i in range(lenpared):
            hpl[int(nodos[i]) - 1, i] = 0
        hpl = np.delete(hpl, int(max(nodos) - 1), 0)

        c_interior = T.iloc[0, 45] * T.iloc[0, 46]

        hpl = hpl[::-1]
        kp = kp[::-1]

        c_int = np.full(lenpared, c_interior)
        kpl = np.vstack([kp, c_int])

        return rt, kp, hpl, kpl, hi, he, c_interior,hp
