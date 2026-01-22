import math


def calcular_amplitud(aislacion_ext: str, kmop_ad_promedio: float) -> float:
    # Constantes de la tabla de referencia
    CALCULO_AMPLITUD = {
        "Pendiente": -76.1,
        "Coef Posición": 1170,
        "Amplitud max": 0.45,
        "Amplitud min": 0.2
    }
    EK11 = CALCULO_AMPLITUD["Pendiente"]
    EK12 = CALCULO_AMPLITUD["Coef Posición"]
    EK13 = CALCULO_AMPLITUD["Amplitud max"]
    EK14 = CALCULO_AMPLITUD["Amplitud min"]

    if kmop_ad_promedio == 0:
        return EK13

    if aislacion_ext.lower() == "si":
        try:
            base = EK11 * math.log(kmop_ad_promedio) + EK12
            valor = base / 1000

            # Limitar entre EK14 y EK13
            if valor > EK13:
                valor = EK13
            if valor < EK14:
                valor = EK14

            # Redondear al múltiplo más cercano de 0.05
            return round(valor / 0.05) * 0.05

        except (ValueError, ZeroDivisionError):
            return EK13  # Manejo de errores matemáticos
    else:
        return EK13


def calculate_amplitude_table(u_kmax_vol: float, amplitud_original: float):
    DATOS_TABLA = []

    DATOS_DESFASE_VERTICAL = [
        {"amplitud": 0.2, "pendiente": -0.00007, "coef_posicion_exp": 7.7194},
        {"amplitud": 0.25, "pendiente": -0.00008, "coef_posicion_exp": 7.7148},
        {"amplitud": 0.3, "pendiente": -0.0002, "coef_posicion_exp": 7.8254},
        {"amplitud": 0.35, "pendiente": -0.0008, "coef_posicion_exp": 8.5333},
        {"amplitud": 0.4, "pendiente": 44.666, "coef_posicion_exp": -0.22},
        {"amplitud": 0.45, "pendiente": 43.762, "coef_posicion_exp": -0.299},
    ]

    # Lookup rápido por amplitud
    params_por_amp = {
        fila["amplitud"]: (fila["pendiente"], fila["coef_posicion_exp"])
        for fila in DATOS_DESFASE_VERTICAL
    }

    # Normaliza la amplitud original a 2 decimales (evita 0.3000000000006 vs 0.3)
    amp_ref = round(float(amplitud_original), 2)
    u_kmax_vol = float(u_kmax_vol)

    # Construcción de la tabla
    for amplitud in [0.2, 0.25, 0.3, 0.35, 0.4, 0.45]:
        match = (amplitud == amp_ref)
        if match:
            u_kmop_vol_ea_em = u_kmax_vol
            pendiente, coef_posicion_exp = params_por_amp.get(amplitud, (0.0, 0.0))
            # redondeo a 1 decimal
            desfase_vertical = round(pendiente * u_kmop_vol_ea_em + coef_posicion_exp, 1)
        else:
            u_kmop_vol_ea_em = 0.0
            pendiente, coef_posicion_exp = 0.0, 0.0
            desfase_vertical = 0.0

        DATOS_TABLA.append({
            "amplitud": amplitud,
            "match": match,
            "pendiente": pendiente,
            "coef_posicion_exp": coef_posicion_exp,
            "u_kmop_vol_ea_em": u_kmop_vol_ea_em,
            "desfase_vertical": desfase_vertical
        })

    # ---- DEBUG: impresión en formato tabla ----
    print(f"[DEBUG] Tabla de amplitudes (amplitud_original={amplitud_original} -> ref={amp_ref:.2f})")
    print("[DEBUG] {:>9} | {:>5} | {:>12} | {:>17} | {:>17} | {:>17}".format(
        "amplitud", "match", "pendiente", "coef_posicion_exp", "u_kmop_vol_ea_em", "desfase_vertical"
    ))
    print("[DEBUG] " + "-" * 106)
    for fila in DATOS_TABLA:
        print("[DEBUG] {:>9.2f} | {:>5} | {:>12.6f} | {:>17.6f} | {:>17.6f} | {:>17.1f}".format(
            fila["amplitud"],
            "SI" if fila["match"] else "NO",
            fila["pendiente"],
            fila["coef_posicion_exp"],
            fila["u_kmop_vol_ea_em"],
            fila["desfase_vertical"]
        ))

    return DATOS_TABLA


def calculate_desfase_vertical_ajustado(u_kmax_vol: float, amplitud_original: float, techo_adiabatico: str,
                                        piso_adiabatico: str, renovaciones_aire: float, flujo_sol: float):
    """
    Calcula el resultado equivalente a la fórmula de Excel proporcionada.
    """

    print(f"u_kmax_vol: {u_kmax_vol}")
    print(f"amplitud_original: {amplitud_original}")
    print(f"techo_adiabatico: {techo_adiabatico}")
    print(f"piso_adiabatico: {piso_adiabatico}")
    print(f"renovaciones_aire: {renovaciones_aire}")
    print(f"flujo_sol: {flujo_sol}")

    calculate_defase_vertical = calculate_amplitude_table(u_kmax_vol, amplitud_original)
    valores_defase_vertical = [item["desfase_vertical"] for item in calculate_defase_vertical]

    print(f"🤞🤞calculate_defase_vertical {calculate_defase_vertical}")
    max_v = max(valores_defase_vertical)
    ajuste_desfase_vertical = {
        "Cargas Internas [W/m2]": {"valor": 0.0, "pendiente": 0.3181, "coef_posicion": -0.0029},
        "Sol [W/m2]": {"valor": 0, "pendiente": 0.0016, "coef_posicion": -0.0276},
        "Infiltraciones [1/h]": {"valor": 1.5, "pendiente": 2.1513, "coef_posicion": 2.8145}
    }

    cargas_internas = (ajuste_desfase_vertical["Cargas Internas [W/m2]"]["pendiente"]
                       * ajuste_desfase_vertical["Cargas Internas [W/m2]"]["valor"]
                       + ajuste_desfase_vertical["Cargas Internas [W/m2]"]["coef_posicion"])
    sol = (ajuste_desfase_vertical["Sol [W/m2]"]["pendiente"] * flujo_sol
           + ajuste_desfase_vertical["Sol [W/m2]"]["coef_posicion"])
    infiltraciones = (renovaciones_aire * math.log(ajuste_desfase_vertical["Infiltraciones [1/h]"]["valor"])
                      + ajuste_desfase_vertical["Infiltraciones [1/h]"]["coef_posicion"])

    suma_total = max_v + (cargas_internas + sol - infiltraciones)

    # 👉 Redondeo a 1 decimal
    redondeado = round(suma_total, 1)

    ajuste_techo = 1 if techo_adiabatico.lower() == "si" else -1
    ajuste_piso = 1 if piso_adiabatico.lower() == "si" else -1

    print(f"Desfase vertical ajustado: {redondeado:.1f} + {ajuste_techo} + {ajuste_piso}")
    return redondeado + ajuste_techo + ajuste_piso


def create_tabla_categoria_prom_envolvente(kmop_promedio_envolvente: float, porcentaje_ventanas: float):
    """
    Genera y devuelve una tabla con las categorías de envolvente
    y calcula dinámicamente el % de ventanas y el desfase horizontal
    según lógica definida.
    """

    ventanas_max_desf_horiz = {
        "Pesado": 0.6,
        "Intermedio Pesado": 0.4,
        "Intermedio": 0.4,
        "Intermedio Liviano": 0.3,
        "Liviano": 0.2,
        "Super Liviano": 0.1
    }

    categorias_kmop = {
        "Pesado": {
            "min": 400.000,
            "max": 0
        },
        "Intermedio Pesado": {
            "min": 250.000,
            "max": 400.000
        },
        "Intermedio": {
            "min": 100.000,
            "max": 250.000
        },
        "Intermedio Liviano": {
            "min": 60.000,
            "max": 100.000
        },
        "Liviano": {
            "min": 25.000,
            "max": 60.000
        },
        "Super Liviano": {
            "min": 0,
            "max": 25.000
        }
    }

    calculo_desf_horizontal = {
        "Pesado": {"pendiente": -4.963, "coef_posicion": 3.496},
        "Intermedio Pesado": {"pendiente": -7.8593, "coef_posicion": 3.3876},
        "Intermedio": {"pendiente": -4.9385, "coef_posicion": 2.3976},
        "Intermedio Liviano": {"pendiente": -7.0, "coef_posicion": 2.3},
        "Liviano": {"pendiente": -10.0, "coef_posicion": 2.0},
        "Super Liviano": {"pendiente": -10.0, "coef_posicion": 1.0}
    }

    categorias = [
        "Pesado",
        "Intermedio Pesado",
        "Intermedio",
        "Intermedio Liviano",
        "Liviano",
        "Super Liviano"
    ]

    tabla = {}

    for categoria in categorias:
        # Lógica ejemplo: solo Intermedio tiene valores
        if kmop_promedio_envolvente >= categorias_kmop[categoria]["min"]:
            porcentaje_ventanas_tabla = porcentaje_ventanas
        else:
            porcentaje_ventanas_tabla = 0

        if porcentaje_ventanas_tabla >= ventanas_max_desf_horiz[categoria]:
            desfase_horizontal = 0
        else:
            desfase_horizontal = round(calculo_desf_horizontal[categoria]["pendiente"] * porcentaje_ventanas_tabla +
                                       calculo_desf_horizontal[categoria]["coef_posicion"], 1)

        tabla[categoria] = {
            "porcentaje_ventanas": porcentaje_ventanas_tabla,
            "desfase_horizontal": desfase_horizontal
        }

    return tabla


def calculate_datos_tabla(aislacion_ext: str, kmop_ad_promedio: float, u_kmax_vol: float, techo_adiabatico: str,
                          piso_adiabatico: str, renovaciones_aire: float, flujo_sol: float,
                          kmop_promedio_envolvente: float, porcentaje_ventanas: float):
    amplitud = calcular_amplitud(aislacion_ext, kmop_ad_promedio)
    desfase_vertical_c_sol = calculate_desfase_vertical_ajustado(u_kmax_vol, amplitud, techo_adiabatico,
                                                                 piso_adiabatico, renovaciones_aire, flujo_sol)
    desfase_vertical_s_sol = desfase_vertical_c_sol

    categorias = create_tabla_categoria_prom_envolvente(kmop_promedio_envolvente, porcentaje_ventanas)

    lista_desfase_horizontal = [categoria["desfase_horizontal"] for categoria in categorias.values()]
    desfase_horizontal = max(lista_desfase_horizontal)

    return {
        "amplitud": amplitud,
        "desfase_vertical_c_sol": desfase_vertical_c_sol,
        "desfase_vertical_s_sol": desfase_vertical_s_sol,
        "desfase_horizontal": desfase_horizontal
    }
