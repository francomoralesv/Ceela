import numpy as np
from scipy.linalg import lu_factor,lu_solve

from .parameters import Parameters
from .sanitize_variables import SanitizeVariablesDTO

class OutputCalculations:
    def __init__(self, output,T_aire,T_old,T_old4,T_aire2,theta_int_op,theta_int_op2,theta_sup,theta_sup2,pot_max,Rg,theta_H_set,theta_C_set,area,e,nodos2):
        self.output = output
        self.T_aire = T_aire
        self.T_old = T_old
        self.T_old4 = T_old4
        self.T_aire2 = T_aire2
        self.theta_int_op = theta_int_op
        self.theta_int_op2 = theta_int_op2
        self.theta_sup = theta_sup
        self.theta_sup2 = theta_sup2
        self.pot_max = pot_max
        self.Rg = Rg
        self.theta_H_set=theta_H_set
        self.theta_C_set=theta_C_set
        self.area=area
        self.e=e
        self.nodos2=nodos2
class EnergyBalance:


    def __init__(self, sanitized_variables: SanitizeVariablesDTO, parameters: Parameters,area,kpl):
        # Inicialización de variables
        self.sanitized_variables = sanitized_variables
        self.parameters = parameters
        # Variables auxiliares
        self.T_old = None
        self.T_old4 = None
        self.output = None
        self.area=area
        self.kpl=kpl


    async def calculate(self,ordenfinal,hi,hpl,he,Atot):
        print("[Calculator engine] Calculating energy balance")
        # Vector auxiliar para los muros con menos nodos
        lenpared=self.parameters.lenpared
        nodos = self.parameters.nodos
        kpl=self.kpl
        area_ventana=self.sanitized_variables.area_ventana
        T=self.sanitized_variables.T
        L=self.sanitized_variables.L
        area=self.area

        dt = self.parameters.dt
        hre = self.parameters.hre
        hri = self.parameters.hri
        cp=self.sanitized_variables.cp
        densidad=self.sanitized_variables.densidad
        espesor=self.sanitized_variables.espesor
        hce_v = self.parameters.hce_v
        kpl_v = self.parameters.kpl_v
        hpl_v = self.parameters.hpl_v
        hci_v = self.parameters.hci_v
        conductividad=self.sanitized_variables.conductividad
        Nd=self.parameters.Nd
        n = int(sum(nodos)) + int(lenpared)  # Cantidad de nodos
        T_nodos = np.zeros([L, n + 3])
        T_nodos_axu = np.zeros([L, n + 3])
        T_nodos_free = np.zeros([L, n + 3])
        theta_int_op = np.zeros([L])
        theta_int_op2 = np.zeros([L])
        e = np.zeros([n + 3, n + 3])
        e2 = np.zeros([n + 3, n + 3])
        re = np.zeros([n + 3, 1])
        re2 = np.zeros([n + 3, 1])
        T_old = np.zeros([L + 1, n + 3])
        T_old2 = np.zeros([L + 1, n + 3])
        T_old3 = np.zeros([L + 1, n + 3])
        T_old4 = np.zeros([L + 1, n + 3])
        T_aire = np.zeros([L])
        T_aire2 = np.zeros([L])
        T_aire_HC = np.zeros([L])
        y = np.arange(0, len(kpl))
        yy = np.arange(0, n + 3)
        Hve= self.parameters.Hve
        cuenta = np.zeros(lenpared)
        Hve_i=self.parameters.Hve_i
        flu_int=self.parameters.flu_int
        f_sol=self.parameters.f_sol
        flu_sol=self.parameters.flu_sol
        ren=self.parameters.ren
        f_int=self.parameters.f_int
        flu_HC=self.parameters.flu_HC
        f_HC=self.parameters.f_HC
        hce=self.parameters.hce
        t_e=self.parameters.t_e
        Htr=self.parameters.Htr
        dx=self.parameters.dx
        hci=self.parameters.hci
        for i in range(0, lenpared):
            for j in range(0, len(kpl)):
                if kpl[j, i] == 0:
                    cuenta[i] += 1

        for i in yy:
            T_old[0, i] = T.iloc[0, 29]  # Temperatura inicial t=0
            T_old2[0, i] = T.iloc[0, 29]
            T_old3[0, i] = T.iloc[0, 29]
            T_old4[0, i] = T.iloc[0, 29]

        # #Considera la ecuación de balance al final de cada muro
        nodos = nodos + 1

        if area_ventana != 0:
            nodoventana = 3
            nodos2 = np.append(nodos, nodoventana)
        else:
            nodos2 = nodos
        def step2(t_set, t_int_op, t_upper, phi_upper):

            phi_HC_ld_un = phi_upper * (t_set - t_int_op) / (t_upper - t_int_op)
            return phi_HC_ld_un
        pot_max = T.iloc[0, 28]
        theta_H_set = T.iloc[:, 25]
        theta_C_set = T.iloc[:, 26]
        theta_upper = np.zeros([L])
        flu_HC_ld_un = 0  # save numpy array as csv file

        # Funcion para obtener la temperatura del aire que entra por ventilacion en caso de tener un recuperador de calor.
        # aun falta por definir bien la ecuacion
        def ventilacion(rendimiento, theta_aire, theta_e):
            if isinstance(rendimiento, str):
                # Remove % and convert to float
                rendimiento = float(rendimiento.replace('%', ''))
            elif not isinstance(rendimiento, (int, float)):
                print(f"rendimiento type: {type(rendimiento)} value: {rendimiento}")
                raise TypeError("rendimiento must be a number (int or float)")
                
            theta_sup = rendimiento * (theta_aire - theta_e) + theta_e
            return theta_sup

        lambdaground = 2
        Rg = 0.5 / lambdaground
        # if ordenfinal[len(ordenfinal)-1]=="CT":
        #     kpl[int(cuenta[len(cuenta)-1]),kpl.shape[1]-1]=0

        # Generarición de la matriz de coeficientes

        for k in y:
            #   #Ecuacion nodo superficie exterior

            if k == 0:

                axu1 = 0

                for j in range(0, lenpared):

                    if j == lenpared - 1 and ordenfinal[j] == "CT":

                        e[(axu1), (axu1)] = kpl[len(kpl) - int(nodos[j]), j] / dt + hi[j] + hpl[
                            len(hpl) - int(nodos[j]) + 2, j]
                        e[(axu1), (axu1 + 1)] = -hpl[len(hpl) - int(nodos[j]) + 2, j]
                        axu1 = axu1 + int(nodos[j])

                    else:

                        ######## Cambio de hre y he por hri y hi

                        if ordenfinal[j] == "IN" or ordenfinal[j] == "AD":
                            e[(axu1), (axu1)] = kpl[len(kpl) - int(nodos[j]), j] / dt + hi[j] + hpl[
                                len(hpl) - int(nodos[j]) + 2, j]
                            e[(axu1), (axu1 + 1)] = -hpl[len(hpl) - int(nodos[j]) + 2, j]
                            axu1 = axu1 + int(nodos[j])
                        else:
                            e[(axu1), (axu1)] = kpl[len(kpl) - int(nodos[j]), j] / dt + hre[1] + he[j] + hpl[
                                len(hpl) - int(nodos[j]) + 2, j]
                            e[(axu1), (axu1 + 1)] = -hpl[len(hpl) - int(nodos[j]) + 2, j]
                            axu1 = axu1 + int(nodos[j])

                            #   #############################################################################
            #   #############################################################################
            #                                 #####Ecuación nodo superficie interior
            #                                 #####Elementos de la diagonal
            elif k == len(kpl) - 2:

                axu2 = 0
                for j in range(1, lenpared + 1):
                    axu2 += int(nodos[j - 1])
                    e[axu2 - 2, axu2 - 1] = -hi[j - 1]
                    e[axu2 - 2, axu2 - 3] = -hpl[len(hpl) - 1, j - 1]
                    e[axu2 - 2, axu2 - 2] = kpl[k, j - 1] / dt + hi[j - 1] + hpl[len(hpl) - 1, j - 1] + hri[1] - hri[
                        1] * area[j - 1] / Atot

                #                               #Ecuación nodo superficie interior
                #                               #Elementos de la interacción entre muros

                axu3 = 0
                for j in range(1, lenpared + 1):
                    axu3 += int(nodos[j - 1])
                    axu4 = 0
                    for i in range(1, lenpared + 1):
                        axu4 += int(nodos[i - 1])
                        if e[axu3 - 2, axu4 - 2] == 0:
                            e[axu3 - 2, axu4 - 2] = -hri[1] * area[i - 1] / Atot

                #   #############################################################################
                #   #############################################################################
                #                                                             #####Ecuación balance aire interior

                # Elementos que interactuan entre muros

                axu3 = 0
                for j in range(1, lenpared + 1):
                    axu3 += int(nodos[j - 1])
                    axu4 = 0
                    for i in range(1, lenpared + 1):
                        axu4 += int(nodos[i - 1])
                        if e[axu3 - 1, axu4 - 2] == 0:
                            e[axu3 - 1, axu4 - 2] = -hi[i - 1] * area[i - 1]


            #   #############################################################################
            #   #############################################################################

            else:
                axu8 = 0  # Ecuación para los nodos internos, en el muro
                for j in range(0, lenpared):
                    for p in range(1, int(nodos[j]) - 2):
                        axu8 += 1
                        e[axu8, axu8 - 1] = -hpl[int(cuenta[j]) + p - 1, j]
                        e[axu8, axu8] = kpl[int(cuenta[j]) + p, j] / dt + hpl[int(cuenta[j]) + p - 1, j] + hpl[
                            int(cuenta[j]) + p, j]
                        e[axu8, axu8 + 1] = -hpl[int(cuenta[j]) + p, j]

                    axu8 += 3

            #   #############################################################################
            #   #############################################################################

            # Se agrega la ventana ponderada

            # Ventanas
            # Ecuación para nodo exterior
            print(f" Hre: {hre} Hce: {hce_v} Hpl: {hpl_v}")
            e[n, n] = kpl_v[0] / dt + hre[1] + hce_v + hpl_v
            e[n, n + 1] = -hpl_v

            # Ecuacion para nodo interior
            e[n + 1, n] = -hpl_v
            e[n + 1, n + 2] = -hci_v
            e[n + 1, n + 1] = kpl_v[1] / dt + hci_v + hpl_v + hri[1] - hri[1] * area[len(area) - 1] / Atot

            # #Balance de energía interior

            areahci = 0
            for i in range(0, len(area)):
                if i == len(area) - 1:
                    areahci += area[i] * hci_v
                else:
                    areahci += area[i] * hi[i]
            e[n + 2, n + 1] = -hci_v * area[len(area) - 1]

            # Efecto de las ventanas otros muros
            axu9 = 0
            for j in range(1, lenpared + 1):
                axu9 += int(nodos[j - 1])
                e[axu9 - 2, n + 3 - 2] = -hri[1] * area[len(area) - 1] / Atot
                e[axu9 - 1, n + 3 - 2] = -hci_v * area[len(area) - 1]

            axu9 = 0
            for i in range(0, lenpared, 1):
                axu9 += int(nodos[i])
                if e[n + 1, axu9 - 2] != 0:
                    e[n + 1, axu9 - 2] = e[n + 1, axu9 - 2]
                else:
                    e[n + 1, axu9 - 2] = -hri[1] * area[i] / Atot
                    e[n + 2, axu9 - 2] = -hi[i] * area[i]

        # Valores para el posterior calculo en free flow
        e2 = e.copy()

        #############################################################################
        #############################################################################

        # Generabión del vector resultados y luego iteración por paso de tiempo

        areahci = 0
        for i in range(0, len(area)):
            if i == len(area) - 1:
                areahci += area[i] * hci_v
            else:
                areahci += area[i] * hi[i]
        x = np.arange(0, L, 1)

        theta_sup = np.zeros([L])
        theta_sup2 = np.zeros([L])
        auxk = len(kpl) - 1
        k = len(kpl) - 2

        for i in x:

            # Termino de ventilacion para el balance energetico

            axu2 = 0
            for j in range(1, lenpared + 1):
                axu2 += int(nodos[j - 1])
                e[(axu2 - 1), (axu2 - 1)] = kpl[auxk, j - 1] / dt + (Hve[i] + Hve_i[i]) + Htr + areahci

            e[n + 2, n + 2] = kpl_v[2] / dt + (Hve[i] + Hve_i[i]) + Htr + areahci

            # Si se tiene un recuperador de calor
            if ren != 0:
                theta_sup[i] = ventilacion(ren, T_old[i, T_old.shape[1] - 1], t_e[i])
            else:
                theta_sup[i] = t_e[i]

            axu10 = 0
            axu11 = 0
            # Factores dependientes solo de la hora
            # Nodo superficie interior
            b2 = (1.0 / Atot) * ((1.0 - f_int) * flu_int[i] + (1.0 - f_sol) * flu_sol[i] + (1.0 - f_HC) * flu_HC[i])
            # Balance energetico
            c2 = Hve[i] * theta_sup[i] + Hve_i[i] * t_e[i] + Htr * t_e[i] + f_int * flu_int[i] + f_sol * flu_sol[
                i] + f_HC * flu_HC[i]

            ## Vector de resultados para los nodos elementos opacos

            for j in range(0, lenpared):
                # Factores dependentientes de la pared correspondiente
                a1 = T_old[i, axu10] / dt
                b1 = T_old[i, axu10 + int(nodos[j]) - 2] / dt
                c1 = T_old[i, axu10 + int(nodos[j]) - 1] / dt
                if ordenfinal[j] == "N" or ordenfinal[j] == "NE" or ordenfinal[j] == "E" or ordenfinal[j] == "SE" or \
                        ordenfinal[j] == "S" \
                        or ordenfinal[j] == "SO" or ordenfinal[j] == "O" or ordenfinal[j] == "NO" or ordenfinal[
                    j] == "N" or ordenfinal[j] == "HR" \
                        or ordenfinal[j] == "FL":
                    if ordenfinal[j] == "N":
                        a2 = (hre[1] + hce[1]) * t_e[i] + self.parameters.NORTE[i]
                    elif ordenfinal[j] == "NE":
                        a2 = (hre[1] + hce[1]) * t_e[i] + self.parameters.NORESTE[i]
                    elif ordenfinal[j] == "E":
                        a2 = (hre[1] + hce[1]) * t_e[i] + self.parameters.ESTE[i]
                    elif ordenfinal[j] == "SE":
                        a2 = (hre[1] + hce[1]) * t_e[i] + self.parameters.SURESTE[i]
                    elif ordenfinal[j] == "S":
                        a2 = (hre[1] + hce[1]) * t_e[i] + self.parameters.SUR[i]
                    elif ordenfinal[j] == "SO":
                        a2 = (hre[1] + hce[1]) * t_e[i] + self.parameters.SUROESTE[i]
                    elif ordenfinal[j] == "O":
                        a2 = (hre[1] + hce[1]) * t_e[i] + self.parameters.OESTE[i]
                    elif ordenfinal[j] == "NO":
                        a2 = (hre[1] + hce[1]) * t_e[i] + self.parameters.NOROESTE[i]
                    elif ordenfinal[j] == "HR":
                        a2 = (hre[1] + hce[1]) * t_e[i] + self.parameters.HORIZONTAL[i]
                    elif ordenfinal[j] == "FL":
                        a2 = (hre[1] + hce[1]) * t_e[i] + self.parameters.PHISOL_DIF[i]

                ###### Piso ventilado

                elif ordenfinal[j] == "AD":

                    # Reemplazar por temperatura interior T_ZTC[i] por T_old[i,len(e)-1]

                    # ISO=0
                    # a2 = ISO*((hre[1]+hce[1])*T_ZTC[i])
                    a2 = (hci[1]) * T_old[i, len(e) - 1]
                    # a2 = (hre[1]+hce[1])*t_e[i]
                elif ordenfinal[j] == "IN":
                    a2 = (hci[1]) * self.parameters.T_ZTU[i]
                elif ordenfinal[j] == "CT":
                    # a2 = (1/Rg)*T_T[i]
                    a2 = (hci[1]) * self.parameters.T_T[i]

                ###############################################################################
                #####Crea los valores en la matriz de resultados para todos los nodos.
                for k in range(0, int(nodos[j])):

                    # Nodo Exterior
                    if k == 0:
                        re[axu10] = kpl[int(cuenta[j]) + k, j] * a1 + a2
                    # Nodo Interior
                    elif k == int(nodos[j]) - 2:
                        re[axu10 + int(nodos[j]) - 2] = kpl[int(cuenta[j]) + k, j] * b1 + b2
                        # Balance energético
                    elif k == int(nodos[j]) - 1:
                        re[axu10 + int(nodos[j]) - 1] = kpl[int(cuenta[j]) + k, j] * c1 + c2
                        # Nodos interiores
                    else:
                        if int(nodos[j]) > 3:
                            axu11 += 1
                            re[axu11] = kpl[int(cuenta[j]) + k, j] * T_old[i, axu11] / dt

                axu10 += int(nodos[j])
                axu11 += 3
            ###############################################################################

            # Ponderado ventana

            # Superficie externa
            re[n] = kpl_v[0] * T_old[i, n] / dt + (hce_v + hre[1]) * t_e[i] + self.parameters.PHISOL_VENTANA[i]
            # Superficie interna
            re[n + 1] = kpl_v[1] * T_old[i, n + 1] / dt + (1.0 / Atot) * (
                    (1.0 - f_int) * flu_int[i] + (1.0 - f_sol) * flu_sol[i] + (1.0 - f_HC) * flu_HC[i])
            # Balance interior
            re[n + 2] = kpl_v[2] * T_old[i, n + 2] / dt + Hve[i] * theta_sup[i] + Hve_i[i] * t_e[i] + Htr * t_e[
                i] + f_int * flu_int[i] + f_sol * flu_sol[i] + f_HC * flu_HC[i]
            # Despeje de temperatura y guardado de temperaturas
            lu_piv = lu_factor(e)
            t_actual = lu_solve(lu_piv, re)
            T_nodos_free[i, :] = t_actual.T  # Reemplaza la temperatura en t-1 por la última temperatura

            T_old[i + 1, :] = t_actual.T
            T_aire[i] = T_nodos_free[i, len(e) - 1]

            ##########################################################################
            # Operaciones para determinar la demanda energetica
            # calculo de la temperatura operativa
            axu12 = 0
            sumatheta_r_mn = 0

            for j in range(0, len(area)):
                axu12 += int(nodos2[j])
                sumatheta_r_mn += area[j] * T_old[i + 1, axu12 - 2]
            theta_r_mn = sumatheta_r_mn / sum(area)
            theta_int_op[i] = (T_old[i + 1, len(e) - 1] + theta_r_mn) / 2

            if self.parameters.CLIMA[i] == 1:

                # Step 1
                if theta_H_set[i] <= theta_int_op[i] and theta_int_op[i] <= theta_C_set[i]:
                    flu_HC[i] = 0
                    T_nodos[i, :] = t_actual.T

                    # Step 2
                else:
                    if i >= 1:

                        if T_old2[i, 0] == 0:
                            T_old2[i, :] = T_old[i, :]
                            T_old3[i, :] = T_old[i, :]

                    flu_HC_upper = pot_max * area[len(area) - 2]
                    axu10 = 0
                    axu11 = 0
                    # Factores dependientes solo de la hora
                    # Nodo superficie interior
                    b2 = (1.0 / Atot) * (
                            (1.0 - f_int) * flu_int[i] + (1.0 - f_sol) * flu_sol[i] + (1.0 - f_HC) * flu_HC_upper)
                    # Balance energetico
                    c2 = Hve[i] * theta_sup[i] + Hve_i[i] * t_e[i] + Htr * t_e[i] + f_int * flu_int[i] + f_sol * \
                         flu_sol[i] + f_HC * flu_HC_upper

                    ## Vector de resultados para los nodos elementos opacos

                    for j in range(0, lenpared):
                        # Factores dependentientes de la pared correspondiente
                        a1 = T_old[i, axu10] / dt
                        b1 = T_old[i, axu10 + int(nodos[j]) - 2] / dt
                        c1 = T_old[i, axu10 + int(nodos[j]) - 1] / dt
                        if ordenfinal[j] == "N" or ordenfinal[j] == "NE" or ordenfinal[j] == "E" or ordenfinal[
                            j] == "SE" or ordenfinal[j] == "S" \
                                or ordenfinal[j] == "SO" or ordenfinal[j] == "O" or ordenfinal[j] == "NO" or ordenfinal[
                            j] == "N" or ordenfinal[j] == "HR" \
                                or ordenfinal[j] == "FL":
                            if ordenfinal[j] == "N":
                                a2 = (hre[1] + hce[1]) * t_e[i] + self.parameters.NORTE[i]
                            elif ordenfinal[j] == "NE":
                                a2 = (hre[1] + hce[1]) * t_e[i] + self.parameters.NORESTE[i]
                            elif ordenfinal[j] == "E":
                                a2 = (hre[1] + hce[1]) * t_e[i] + self.parameters.ESTE[i]
                            elif ordenfinal[j] == "SE":
                                a2 = (hre[1] + hce[1]) * t_e[i] + self.parameters.SURESTE[i]
                            elif ordenfinal[j] == "S":
                                a2 = (hre[1] + hce[1]) * t_e[i] + self.parameters.SUR[i]
                            elif ordenfinal[j] == "SO":
                                a2 = (hre[1] + hce[1]) * t_e[i] + self.parameters.SUROESTE[i]
                            elif ordenfinal[j] == "O":
                                a2 = (hre[1] + hce[1]) * t_e[i] + self.parameters.OESTE[i]
                            elif ordenfinal[j] == "NO":
                                a2 = (hre[1] + hce[1]) * t_e[i] + self.parameters.NOROESTE[i]
                            elif ordenfinal[j] == "HR":
                                a2 = (hre[1] + hce[1]) * t_e[i] + self.parameters.HORIZONTAL[i]
                            elif ordenfinal[j] == "FL":
                                a2 = (hre[1] + hce[1]) * t_e[i] + self.parameters.PHISOL_DIF[i]

                        ###### Piso ventilado

                        elif ordenfinal[j] == "AD":

                            # Reemplazar por temperatura interior T_ZTC[i] por T_old[len(T_old)-1]

                            # ISO=0
                            # a2 = ISO*((hre[1]+hce[1])*T_ZTC[i])
                            a2 = (hci[1]) * T_old[i, len(e) - 1]
                            # a2 = (hre[1]+hce[1])*t_e[i]
                        elif ordenfinal[j] == "IN":
                            a2 = (hci[1]) * self.parameters.T_ZTU[i]
                        elif ordenfinal[j] == "CT":
                            # a2 = (1/Rg)*T_T[i]
                            a2 = (hci[1]) * self.parameters.T_T[i]
                        ###############################################################################
                        #####Crea los valores en la matriz de resultados para todos los nodos.
                        for k in range(0, int(nodos[j])):

                            # Nodo Exterior
                            if k == 0:
                                re[axu10] = kpl[int(cuenta[j]) + k, j] * a1 + a2
                            # Nodo Interior
                            elif k == int(nodos[j]) - 2:
                                re[axu10 + int(nodos[j]) - 2] = kpl[int(cuenta[j]) + k, j] * b1 + b2
                                # Balance energético
                            elif k == int(nodos[j]) - 1:
                                re[axu10 + int(nodos[j]) - 1] = kpl[int(cuenta[j]) + k, j] * c1 + c2
                                # Nodos interiores
                            else:
                                if int(nodos[j]) > 3:
                                    axu11 += 1
                                    re[axu11] = kpl[int(cuenta[j]) + k, j] * T_old[i, axu11] / dt

                        axu10 += int(nodos[j])
                        axu11 += 3
                    ###############################################################################

                    # Ponderado ventana

                    # Superficie externa
                    re[n] = kpl_v[0] * T_old[i, n] / dt + (hce_v + hre[1]) * t_e[i] + self.parameters.PHISOL_VENTANA[i]
                    # Superficie interna
                    re[n + 1] = kpl_v[1] * T_old[i, n + 1] / dt + (1.0 / Atot) * (
                            (1.0 - f_int) * flu_int[i] + (1.0 - f_sol) * flu_sol[i] + (1.0 - f_HC) * flu_HC_upper)
                    # Balance interior
                    re[n + 2] = kpl_v[2] * T_old[i, n + 2] / dt + Hve[i] * theta_sup[i] + Hve_i[i] * t_e[i] + Htr * t_e[
                        i] + f_int * flu_int[i] + f_sol * flu_sol[i] + f_HC * flu_HC_upper

                    lu_piv = lu_factor(e)
                    t_actual_upper = lu_solve(lu_piv, re)
                    T_nodos_axu[i, :] = t_actual_upper.T  # Reemplaza la temperatura en t-1 por la última temperatura

                    T_old2[i + 1, :] = t_actual_upper.T

                    #     ############
                    axu13 = 0
                    sumatheta_r_mn_upper = 0
                    for j in range(0, len(area)):
                        axu13 += int(nodos2[j])
                        sumatheta_r_mn_upper += area[j] * T_old2[i + 1, axu13 - 2]
                    theta_r_mn_upper = sumatheta_r_mn_upper / sum(area)
                    theta_upper[i] = (T_old2[i + 1, len(e) - 1] + theta_r_mn_upper) / 2

                    if theta_int_op[i] > theta_C_set[i]:
                        theta_int_set = theta_C_set[i]
                        flu_HC_ld_un = step2(theta_int_set, theta_int_op[i], theta_upper[i], flu_HC_upper)


                    elif theta_int_op[i] < theta_H_set[i]:
                        theta_int_set = theta_H_set[i]
                        flu_HC_ld_un = step2(theta_int_set, theta_int_op[i], theta_upper[i], flu_HC_upper)

                    # Step 3
                    # Step 4
                    flu_C_avail = -flu_HC_upper
                    flu_H_avail = flu_HC_upper
                    if flu_C_avail <= flu_HC_ld_un and flu_HC_ld_un <= flu_H_avail:
                        flu_HC[i] = flu_HC_ld_un
                    else:
                        if flu_HC_ld_un > 0:
                            flu_HC[i] = flu_H_avail
                        elif flu_HC_ld_un < 0:
                            flu_HC[i] = flu_C_avail

                    #######     #Finalmente vuelve a resolver el balance energetico para determinar las temperaturas

                    axu10 = 0
                    axu11 = 0
                    # Factores dependientes solo de la hora
                    # Nodo superficie interior
                    b2 = (1.0 / Atot) * (
                            (1.0 - f_int) * flu_int[i] + (1.0 - f_sol) * flu_sol[i] + (1.0 - f_HC) * flu_HC[i])
                    # Balance energetico
                    c2 = Hve[i] * theta_sup[i] + Hve_i[i] * t_e[i] + Htr * t_e[i] + f_int * flu_int[i] + f_sol * \
                         flu_sol[i] + f_HC * flu_HC[i]

                    ## Vector de resultados para los nodos elementos opacos

                    for j in range(0, lenpared):
                        # Factores dependentientes de la pared correspondiente
                        a1 = T_old[i, axu10] / dt
                        b1 = T_old[i, axu10 + int(nodos[j]) - 2] / dt
                        c1 = T_old[i, axu10 + int(nodos[j]) - 1] / dt
                        if ordenfinal[j] == "N" or ordenfinal[j] == "NE" or ordenfinal[j] == "E" or ordenfinal[
                            j] == "SE" or ordenfinal[j] == "S" \
                                or ordenfinal[j] == "SO" or ordenfinal[j] == "O" or ordenfinal[j] == "NO" or ordenfinal[
                            j] == "N" or ordenfinal[j] == "HR" \
                                or ordenfinal[j] == "FL":
                            if ordenfinal[j] == "N":
                                a2 = (hre[1] + hce[1]) * t_e[i] +  self.parameters.NORTE[i]
                            elif ordenfinal[j] == "NE":
                                a2 = (hre[1] + hce[1]) * t_e[i] +  self.parameters.NORESTE[i]
                            elif ordenfinal[j] == "E":
                                a2 = (hre[1] + hce[1]) * t_e[i] +  self.parameters.ESTE[i]
                            elif ordenfinal[j] == "SE":
                                a2 = (hre[1] + hce[1]) * t_e[i] +  self.parameters.SURESTE[i]
                            elif ordenfinal[j] == "S":
                                a2 = (hre[1] + hce[1]) * t_e[i] +  self.parameters.SUR[i]
                            elif ordenfinal[j] == "SO":
                                a2 = (hre[1] + hce[1]) * t_e[i] +  self.parameters.SUROESTE[i]
                            elif ordenfinal[j] == "O":
                                a2 = (hre[1] + hce[1]) * t_e[i] +  self.parameters.OESTE[i]
                            elif ordenfinal[j] == "NO":
                                a2 = (hre[1] + hce[1]) * t_e[i] +  self.parameters.NOROESTE[i]
                            elif ordenfinal[j] == "HR":
                                a2 = (hre[1] + hce[1]) * t_e[i] +  self.parameters.HORIZONTAL[i]
                            elif ordenfinal[j] == "FL":
                                a2 = (hre[1] + hce[1]) * t_e[i] + self.parameters.PHISOL_DIF[i]

                        ###### Piso ventilado

                        elif ordenfinal[j] == "AD":

                            # Reemplazar por temperatura interior T_ZTC[i] por T_old[len(T_old)-1]

                            # ISO=0
                            # a2 = ISO*((hre[1]+hce[1])*T_ZTC[i])
                            a2 = (hci[1]) * T_old[i, len(e) - 1]
                            # a2 = (hre[1]+hce[1])*t_e[i]
                        elif ordenfinal[j] == "IN":
                            a2 = (hci[1]) * self.parameters.T_ZTU[i]
                        elif ordenfinal[j] == "CT":
                            # a2 = (1/Rg)*T_T[i]
                            a2 = (hci[1]) * self.parameters.T_T[i]
                        ###############################################################################
                        #####Crea los valores en la matriz de resultados para todos los nodos.
                        for k in range(0, int(nodos[j])):

                            # Nodo Exterior
                            if k == 0:
                                re[axu10] = kpl[int(cuenta[j]) + k, j] * a1 + a2
                            # Nodo Interior
                            elif k == int(nodos[j]) - 2:
                                re[axu10 + int(nodos[j]) - 2] = kpl[int(cuenta[j]) + k, j] * b1 + b2
                                # Balance energético
                            elif k == int(nodos[j]) - 1:
                                re[axu10 + int(nodos[j]) - 1] = kpl[int(cuenta[j]) + k, j] * c1 + c2
                                # Nodos interiores
                            else:
                                if int(nodos[j]) > 3:
                                    axu11 += 1
                                    re[axu11] = kpl[int(cuenta[j]) + k, j] * T_old[i, axu11] / dt

                        axu10 += int(nodos[j])
                        axu11 += 3
                    ###############################################################################

                    # Ponderado ventana

                    # Superficie externa
                    re[n] = kpl_v[0] * T_old[i, n] / dt + (hce_v + hre[1]) * t_e[i] + self.parameters.PHISOL_VENTANA[i]
                    # Superficie interna
                    re[n + 1] = kpl_v[1] * T_old[i, n + 1] / dt + (1.0 / Atot) * (
                            (1.0 - f_int) * flu_int[i] + (1.0 - f_sol) * flu_sol[i] + (1.0 - f_HC) * flu_HC[i])
                    # Balance interior
                    re[n + 2] = kpl_v[2] * T_old[i, n + 2] / dt + Hve[i] * theta_sup[i] + Hve_i[i] * t_e[i] + Htr * t_e[
                        i] + f_int * flu_int[i] + f_sol * flu_sol[i] + f_HC * flu_HC[i]

                    lu_piv = lu_factor(e)
                    t_actual = lu_solve(lu_piv, re)
                    T_nodos[i, :] = t_actual.T  # Reemplaza la temperatura en t-1 por la última temperatura
                    T_old3[i + 1, :] = t_actual.T
                    T_aire_HC[i] = T_nodos[i, len(e) - 1]

                    axu12 = 0
                    sumatheta_r_mn = 0

                    for j in range(0, len(area)):
                        axu12 += int(nodos2[j])
                        sumatheta_r_mn += area[j] * T_old3[i + 1, axu12 - 2]
                    theta_r_mn = sumatheta_r_mn / sum(area)
                    theta_int_op[i] = (T_old3[i + 1, len(e) - 1] + theta_r_mn) / 2
                    T_old[i + 1, :] = T_old3[i + 1, :]
                    T_old2[i + 1, :] = T_old3[i + 1, :]

        T_aire = T_old[1:L + 1, len(e) - 1]


        for i in x:

            # Termino de ventilacion para el balance energetico

            axu2 = 0
            for j in range(1, lenpared + 1):
                axu2 += int(nodos[j - 1])
                e2[(axu2 - 1), (axu2 - 1)] = kpl[auxk, j - 1] / dt + (Hve[i] + Hve_i[i]) + Htr + areahci

            e2[n + 2, n + 2] = kpl_v[2] / dt + (Hve[i] + Hve_i[i]) + Htr + areahci

            # Si se tiene un recuperador de calor
            if ren != 0:
                theta_sup2[i] = ventilacion(ren, T_old4[i, T_old4.shape[1] - 1], t_e[i])
            else:
                theta_sup2[i] = t_e[i]

            axu10 = 0
            axu11 = 0
            # Factores dependientes solo de la hora
            # Nodo superficie interior
            b2 = (1.0 / Atot) * ((1.0 - f_int) * flu_int[i] + (1.0 - f_sol) * flu_sol[i])
            # Balance energetico
            c2 = Hve[i] * theta_sup2[i] + Hve_i[i] * t_e[i] + Htr * t_e[i] + f_int * flu_int[i] + f_sol * flu_sol[i]

            ## Vector de resultados para los nodos elementos opacos

            for j in range(0, lenpared):
                # Factores dependentientes de la pared correspondiente
                a1 = T_old4[i, axu10] / dt
                b1 = T_old4[i, axu10 + int(nodos[j]) - 2] / dt
                c1 = T_old4[i, axu10 + int(nodos[j]) - 1] / dt
                if ordenfinal[j] == "N" or ordenfinal[j] == "NE" or ordenfinal[j] == "E" or ordenfinal[j] == "SE" or \
                        ordenfinal[j] == "S" \
                        or ordenfinal[j] == "SO" or ordenfinal[j] == "O" or ordenfinal[j] == "NO" or ordenfinal[
                    j] == "N" or ordenfinal[j] == "HR" \
                        or ordenfinal[j] == "FL":
                    if ordenfinal[j] == "N":
                        a2 = (hre[1] + hce[1]) * t_e[i] + self.parameters.NORTE[i]
                    elif ordenfinal[j] == "NE":
                        a2 = (hre[1] + hce[1]) * t_e[i] + self.parameters.NORESTE[i]
                    elif ordenfinal[j] == "E":
                        a2 = (hre[1] + hce[1]) * t_e[i] + self.parameters.ESTE[i]
                    elif ordenfinal[j] == "SE":
                        a2 = (hre[1] + hce[1]) * t_e[i] + self.parameters.SURESTE[i]
                    elif ordenfinal[j] == "S":
                        a2 = (hre[1] + hce[1]) * t_e[i] + self.parameters.SUR[i]
                    elif ordenfinal[j] == "SO":
                        a2 = (hre[1] + hce[1]) * t_e[i] + self.parameters.SUROESTE[i]
                    elif ordenfinal[j] == "O":
                        a2 = (hre[1] + hce[1]) * t_e[i] + self.parameters.OESTE[i]
                    elif ordenfinal[j] == "NO":
                        a2 = (hre[1] + hce[1]) * t_e[i] + self.parameters.NOROESTE[i]
                    elif ordenfinal[j] == "HR":
                        a2 = (hre[1] + hce[1]) * t_e[i] + self.parameters.HORIZONTAL[i]
                    elif ordenfinal[j] == "FL":
                        a2 = (hre[1] + hce[1]) * t_e[i] + self.parameters.PHISOL_DIF[i]

                ###### Piso ventilado

                elif ordenfinal[j] == "AD":

                    # Reemplazar por temperatura interior T_ZTC[i] por T_old[i,len(e)-1]

                    # ISO=0
                    # a2 = ISO*((hre[1]+hce[1])*T_ZTC[i])
                    a2 = (hci[1]) * T_old4[i, len(e) - 1]
                    # a2 = (hre[1]+hce[1])*t_e[i]
                elif ordenfinal[j] == "IN":
                    a2 = (hci[1]) * self.parameters.T_ZTU[i]
                elif ordenfinal[j] == "CT":
                    # a2 = (1/Rg)*T_T[i]
                    a2 = (hci[1]) * self.parameters.T_T[i]
                ###########################################################################
                #####Crea los valores en la matriz de resultados para todos los nodos.
                for k in range(0, int(nodos[j])):

                    # Nodo Exterior
                    if k == 0:
                        re2[axu10] = kpl[int(cuenta[j]) + k, j] * a1 + a2
                    # Nodo Interior
                    elif k == int(nodos[j]) - 2:
                        re2[axu10 + int(nodos[j]) - 2] = kpl[int(cuenta[j]) + k, j] * b1 + b2
                        # Balance energético
                    elif k == int(nodos[j]) - 1:
                        re2[axu10 + int(nodos[j]) - 1] = kpl[int(cuenta[j]) + k, j] * c1 + c2
                        # Nodos interiores
                    else:
                        if int(nodos[j]) > 3:
                            axu11 += 1
                            re2[axu11] = kpl[int(cuenta[j]) + k, j] * T_old4[i, axu11] / dt

                axu10 += int(nodos[j])
                axu11 += 3
            ###########################################################################

            # Ponderado ventana

            # Superficie externa
            re2[n] = kpl_v[0] * T_old4[i, n] / dt + (hce_v + hre[1]) * t_e[i] + self.parameters.PHISOL_VENTANA[i]
            # Superficie interna
            re2[n + 1] = kpl_v[1] * T_old4[i, n + 1] / dt + (1.0 / Atot) * (
                    (1.0 - f_int) * flu_int[i] + (1.0 - f_sol) * flu_sol[i])
            # Balance interior
            re2[n + 2] = kpl_v[2] * T_old4[i, n + 2] / dt + Hve[i] * theta_sup2[i] + Hve_i[i] * t_e[i] + Htr * t_e[
                i] + f_int * flu_int[i] + f_sol * flu_sol[i]
            # Despeje de temperatura y guardado de temperaturas
            lu_piv2 = lu_factor(e2)
            t_actual2 = lu_solve(lu_piv2, re2)
            T_old4[i + 1, :] = t_actual2.T

            ###########################################################################
            # Operaciones para determinar la demanda energetica
            # calculo de la temperatura operativa
            axu12 = 0
            sumatheta_r_mn = 0

            for j in range(0, len(area)):
                axu12 += int(nodos2[j])
                sumatheta_r_mn += area[j] * T_old4[i + 1, axu12 - 2]
            theta_r_mn = sumatheta_r_mn / sum(area)
            theta_int_op2[i] = (T_old4[i + 1, len(e) - 1] + theta_r_mn) / 2

        T_aire2 = T_old4[1:L + 1, len(e) - 1]

        T_old = np.round(T_old, 2)
        T_old4 = np.round(T_old4, 2)
        valor = 0
        valor += T_old.shape[1] + T_old4.shape[1]
        valor += len(e)
        valor += 23 + 3 + 14 + 2 + 7 + 3 + 4
        valor += conductividad.shape[1] + cp.shape[1] + densidad.shape[1] + espesor.shape[1] + dx.shape[1] + \
                 kpl.shape[
                     1] + hpl.shape[1] + Nd.shape[1]

        output = np.zeros([L, valor])
        return OutputCalculations(output,T_aire,T_old,T_old4,T_aire2,theta_int_op,theta_int_op2,theta_sup,theta_sup2,pot_max,Rg, theta_H_set,theta_C_set,area,e,nodos2)

    def get_result(self):
        # Devuelve el resultado calculado
        return self.output
