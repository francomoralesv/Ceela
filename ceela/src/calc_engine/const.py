
def get_muros(nodos,ordenfinal,area_ventana,e):
    muros = []
    for i in range(0, len(ordenfinal)):
        for j in range(0, int(nodos[i])):
            muros.append(ordenfinal[i])
    if area_ventana != 0:
        for i in range(0, 3):
            muros.append("V")

    for i in range(0, len(ordenfinal)):
        for j in range(0, int(nodos[i])):
            muros.append(ordenfinal[i])
    if area_ventana != 0:
        for i in range(0, 3):
            muros.append("V")

    muros.append("ID_Recinto")
    muros.append("Hora")
    muros.append("Dia")
    muros.append("Mes")
    muros.append("Temperatura_aire_interior_con_clima")
    muros.append("Temperatura_aire_interior_free_float")
    muros.append("Temperatura_aire_exterior")
    muros.append("Temperatura_interior_operativa_con_clima")
    muros.append("Temperatura_interior_operativa_free_float")
    muros.append("Temperatura_ventilacion_con_clima")
    muros.append("Temperatura_ventilacion_free_float")
    muros.append("Demanda")
    muros.append("Cargas_internas")
    muros.append("Flujo_solar_ventana")
    muros.append("Coeficiente_ventilacion")
    muros.append("Coeficiente_infiltraciones")
    muros.append("Factor_solar_Norte")
    muros.append("Factor_solar_Noreste")
    muros.append("Factor_solar_Este")
    muros.append("Factor_solar_Sureste")
    muros.append("Factor_solar_Sur")
    muros.append("Factor_solar_Suroeste")
    muros.append("Factor_solar_Oeste")
    muros.append("Factor_solar_Noroeste")
    muros.append("Factor_solar_Horizontal")
    muros.append("Factor_solar_Difuso")
    muros.append("Factor_solar_Ventana_exterior")
    muros.append("Temperatura_seteo_calefaccion")
    muros.append("Temperatura_seteo_refrigeracion")
    muros.append("Areas")
    for i in range(0, len(nodos)):
        muros.append("Conductividad")
    for i in range(0, len(nodos)):
        muros.append("Cp")
    for i in range(0, len(nodos)):
        muros.append("Espesor")
    for i in range(0, len(nodos)):
        muros.append("Densidad")
    muros.append("Capacidad_terminca_ambiente_interior")
    muros.append("dt")
    muros.append("Coeficiente_de_absorcion_solar")
    for i in range(0, len(nodos)):
        muros.append("dx")
    for i in range(0, len(e)):
        muros.append("Matriz")
    muros.append("Fraccion_convectiva_H/C")
    muros.append("Fraccion_convectiva_ganancias_internas")
    muros.append("Numero_de_fourier_referencia")
    muros.append("Factor_de_sombreamiento")
    muros.append("Fraccion_convectiva_radiacion_solar")
    muros.append("hce")
    muros.append("hce_ventana")
    muros.append("hci")
    muros.append("hci_ventana")
    muros.append("hre")
    muros.append("hri")
    muros.append("Htr_(puentes_termicos)")
    muros.append("he")
    muros.append("hi")
    for i in range(0, len(nodos)):
        muros.append("hpl")
    for i in range(0, len(nodos)):
        muros.append("kpl")
    muros.append("hpl_ventana")
    muros.append("kpl_ventana")
    for i in range(0, len(nodos)):
        muros.append("Nodos")
    muros.append("Nodos_por_muro")
    muros.append("Potencia_disponible_clima_m2")
    muros.append("Rendimiento_recuperador_calor")
    muros.append("Resistencia_termica_capa_virtual_tierra")
    muros.append("Resistencia_superficial_aire_interior")
    muros.append("Resistencia_superficial_aire_exterior")
    muros.append("Coeficiente_transferencia_calor")
    return muros

muros2 = [
    "ID_Recinto",
    "Hora",
    "Dia",
    "Mes",
    "Temperatura_exterior",
    "Temperatura_operativa_free_float",
    "Temperatura_operativa_con_clima",
    "Demanda",
    "Sol",
    "G_HU",
    "G_DHU",
    "x_int_aire"
]
muros3 = [
    "ID_Recinto",
    "Mes",
    "Hora",
    "Temperatura_exterior",
    "Temperatura_operativa_free_float",
    "Temperatura_operativa_con_clima",
    "Demanda",
    "G_HU",
    "G_DHU"
]

muros4 = [
    "ID_Recinto",
    "Hora",
    "dia",
    "Mes",
    "Presión_saturacion",
    "x_set_min",
    "x_set_max",
    "x_int_aire",
    "G_HU",
    "G_DHU"
]

output_format= ".txt"