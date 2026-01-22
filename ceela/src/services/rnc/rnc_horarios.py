import os
import numpy as np
from sqlalchemy.orm import Session
from src.services.calculator.weather.weather_service import get_weather_data_from_coord_one
from src.services.datos.materials import get_nodos_area_by_orientation, get_translucent_window_area_by_enclosure
from src.services.project.project_service import get_project_by_id_only
from src.services.rnc.rnc_calculator import datos_rnc
from src.services.rnc.rnc_utils import calculate_datos_tabla
from src.services.calculator.python.process_python_input import PyProcessInput
import pandas as pd

from src.models.entity.enclosure_general import EnclosureGenerals
from src.utils.processor import read_parquet_file


def calculate_tabla_horarios_1(db: Session, current_user: dict, project_id: int):
    enclosures = db.query(EnclosureGenerals).filter(
        EnclosureGenerals.project_id == project_id
    ).all()

    datos_rnc_list = datos_rnc(current_user, project_id, db)

    # ✅ Lista de dicts -> dict {enclosure_id: datos}
    datos_rnc_dict = {
        enclosure_id: data
        for dic in datos_rnc_list
        for enclosure_id, data in dic.items()
    }

    resultados_por_enclosure = {}

    # ✅ Carpeta del proyecto
    output_dir = os.path.join("public", "rnc_hours", str(project_id))
    os.makedirs(output_dir, exist_ok=True)

    project = get_project_by_id_only(project_id, db)
    zone = project.project_metadata.get("zone")
    weather_metadata = get_weather_data_from_coord_one(
        db, project.latitude, project.longitude, zone
    )
    weather_path = weather_metadata.location
    print("weather_path: ", weather_path)
    weather_processed_df = read_parquet_file(weather_path)
    monthly_processed_data_df = read_parquet_file(weather_metadata.complementary)

    for enclosure in enclosures:
        enclosure_id = enclosure.id
        if enclosure_id not in datos_rnc_dict:
            continue  # No hay datos para este recinto

        datos_tabla = calculate_datos_tabla(
            datos_rnc_dict[enclosure_id]["aislacion_ext"],
            datos_rnc_dict[enclosure_id]["kmop_ad_promedio"],
            datos_rnc_dict[enclosure_id]["u_kmax_vol"],
            datos_rnc_dict[enclosure_id]["techo_adiabatico"],
            datos_rnc_dict[enclosure_id]["piso_adiabatico"],
            datos_rnc_dict[enclosure_id]["renovaciones_aire"],
            datos_rnc_dict[enclosure_id]["flujo_sol"],
            datos_rnc_dict[enclosure_id]["kmop_promedio_envolvente"],
            datos_rnc_dict[enclosure_id]["porcentaje_vent"],
        )

        def get_sol_file(enclosure_id: int):
            route_sol = f"public/sol_recinto/{project_id}/"
            return os.path.join(route_sol, f"{enclosure_id}_sol_recinto.parquet")

        sol_file = get_sol_file(enclosure_id)

        areas_for_py = get_nodos_area_by_orientation(enclosure.id, db=db)
        areas_for_py = pd.DataFrame(areas_for_py).drop(
            columns=["Absorcion", "item_id", "type"], errors="ignore"
        )

        py_process_input = PyProcessInput(
            project,
            enclosure.id,
            weather_processed_df,
            monthly_processed_data_df,
            areas_for_py=areas_for_py,
            sol_file=sol_file,
            db=db
        )

        tupla = py_process_input.build(weather_processed_df, monthly_processed_data_df)
        resultado_df = tupla[2].reset_index(drop=True)

        # ================================
        # 🧠 PROMEDIO estilo AVERAGEIFS sobre TODO el DF
        # ================================
        def _to_num(series):
            return pd.to_numeric(series, errors="coerce")

        def lookup_t_ext(mes: int, hora: int) -> float:
            m_col = _to_num(resultado_df["month"])
            h_col = _to_num(resultado_df["hours/week"])
            v_col = _to_num(resultado_df["theta_e;air"])
            mask = (m_col == mes) & (h_col == hora)
            vals = v_col[mask]
            return float(vals.mean()) if mask.any() else 0.0

        # Debug para verificar
        MES_TEST, HORA_TEST = 1, 1
        debug_val = lookup_t_ext(MES_TEST, HORA_TEST)
        debug_cnt = (
                (pd.to_numeric(resultado_df["month"], errors="coerce") == MES_TEST) &
                (pd.to_numeric(resultado_df["hours/week"], errors="coerce") == HORA_TEST)
        ).sum()
        print(f"[DEBUG] (mes={MES_TEST}, hora={HORA_TEST}) promedio_total={debug_val} filas_usadas={int(debug_cnt)}")

        # ================================
        # 🌀 Generar tabla base (Mes/Hora/T Ext)
        # ================================
        filas = []
        for mes in range(1, 13):  # 1..12
            for hora in range(1, 25):  # 1..24
                valor = hora + 18 if (hora + 18) < 24 else (hora + 18 - 24)
                t_ext = lookup_t_ext(mes, hora)
                filas.append({
                    "Valor": valor,
                    "Mes": mes,
                    "Hora": hora,
                    "T Ext": t_ext,
                    "T RNC": 0.0
                })

        df_tabla_horarios = pd.DataFrame(filas)

        # ================================
        # 🌦️ Tabla de clima complementaria
        # ================================
        df_tabla_clima = calculate_tabla_horarios_2(
            df_tabla_horarios, db, project_id, enclosure_id
        )

        # ================================
        # 🧮 Cálculo de T RNC (tu Excel literal)
        # ================================
        for idx_row, row in df_tabla_horarios.iterrows():
            mes = row["Mes"]
            valor = row["Valor"]

            fila_clima = df_tabla_clima[df_tabla_clima["Numero Mes"] == mes].iloc[0]

            factor = fila_clima["2(Max1 - Min2)/2"]
            offset = fila_clima["2(Max1 + Min2)/2"]

            if valor < (9 + datos_tabla["desfase_horizontal"]):
                resultado = (
                        factor * datos_tabla["amplitud"] *
                        np.cos(valor * np.pi / (9 + datos_tabla["desfase_horizontal"])) +
                        (datos_tabla["desfase_vertical_c_sol"] + offset)
                )
            else:
                resultado = (
                        -factor * datos_tabla["amplitud"] *
                        np.cos((valor - 10) * np.pi / (13 + datos_tabla["desfase_horizontal"])) +
                        (datos_tabla["desfase_vertical_s_sol"] + offset)
                )

            df_tabla_horarios.at[idx_row, "T RNC"] = round(float(resultado), 2)

        # 💾 Guardado
        enclosure_dir = os.path.join(output_dir, str(enclosure_id))
        os.makedirs(enclosure_dir, exist_ok=True)
        output_path = os.path.join(enclosure_dir, f"tabla_horas_{enclosure_id}.parquet")
        df_tabla_horarios.to_parquet(output_path, index=False)

        resultados_por_enclosure[enclosure_id] = {
            "datos_tabla": datos_tabla,
            "tabla_horarios": df_tabla_horarios.to_dict(orient="records")
        }

    print(f"✅ Tabla de horarios guardada en: public/rnc_hours/{project_id}/<enclosure_id>/")
    return resultados_por_enclosure


# (Opcional) Helper estilo AVERAGEIFS por si lo necesitas suelto.
def calculate_t_ext(
        python_I_755_9514,  # Valores (I)
        python_D_755_9514,  # Condición 1 (D) = month
        python_G_755_9514,  # Condición 2 (G) = hours/week
        rnc_AJ11,  # Mes 1..12
        rnc_AK11  # Hora 1..24
) -> float:
    """
    =PROMEDIO.SI.CONJUNTO(I, D, AJ11, G, AK11)
    """
    suma = 0.0
    n_ok = 0
    for v, d, g in zip(python_I_755_9514, python_D_755_9514, python_G_755_9514):
        if pd.isna(v) or pd.isna(d) or pd.isna(g):
            continue
        if int(d) == int(rnc_AJ11) and int(g) == int(rnc_AK11):
            suma += float(v)
            n_ok += 1
    return (suma / n_ok) if n_ok else 0.0


def calculate_tabla_horarios_2(
        df_datos: pd.DataFrame,
        db: Session,
        project_id: int,
        enclosure_id: int
):
    """
    Recibe un DataFrame con columnas 'T Ext' y 'Mes',
    y guarda la tabla climatológica completa como 'tabla.parquet'
    en la carpeta correspondiente al proyecto y recinto.
    """
    meses = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]

    filas = []

    for i in range(12):
        tmin = df_datos[df_datos["Mes"] == i + 1]["T Ext"].min()
        tmax = df_datos[df_datos["Mes"] == i + 1]["T Ext"].max()
        mes = meses[i]

        amplitud_diaria_1 = -1 * (tmax - tmin) / 2
        amplitud_cruzada_1 = (tmax - tmin) / 2
        promedio_termico_1 = (tmax + tmin) / 2
        promedio_cruzado_1 = (tmax + tmin) / 2

        fila = {
            "Numero Mes": i + 1,
            "Mes": mes,
            "Día": 0,
            "Tmin": tmin,
            "Tmax": tmax,
            "1(Max1 - Min1)/2": amplitud_diaria_1,
            "2(Max1 - Min2)/2": amplitud_cruzada_1,
            "1(Max1 + Min1)/2": promedio_termico_1,
            "2(Max1 + Min2)/2": promedio_cruzado_1,
        }

        filas.append(fila)

    df_resultado = pd.DataFrame(filas)

    # 📁 Ruta al directorio del enclosure dentro del proyecto
    output_dir = os.path.join("public", "rnc_hours", str(project_id), str(enclosure_id))
    os.makedirs(output_dir, exist_ok=True)

    # 💾 Guardar el archivo tabla.parquet
    output_path = os.path.join(output_dir, f"tabla_clim_{enclosure_id}.parquet")
    df_resultado.to_parquet(output_path, index=False)

    print(f"✅ Tabla climatológica guardada en: {output_path}")
    return df_resultado


def calcular_t_rnc(hora, amplitud, promedio, desfase_horizontal):
    """
    Calcula T RNC a partir de hora, amplitud, promedio y desfase horizontal (AG11).
    Traducción directa de la fórmula Excel con funciones coseno.
    """
    if hora < (9 + desfase_horizontal):
        return round(
            amplitud * np.cos(hora * np.pi / (9 + desfase_horizontal)) + promedio,
            2
        )
    else:
        return round(
            -amplitud * np.cos((hora - 10) * np.pi / (13 + desfase_horizontal)) + promedio,
            2
        )
