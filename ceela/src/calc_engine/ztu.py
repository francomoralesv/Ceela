import os

import numpy as np
import pandas as pd

from src.models.entity.detail_part import DetailPart
from src.models.entity.details import Detail
from src.models.entity.formulas import Formulas
from src.services.rnc.rnc_calculator import calculate_rnc_area_u_km_op, calculate_rnc_muro, calculate_rnc_techo, \
    calculate_rnc_piso, _safe_div, AJUSTE_DESFASE_VERTICAL, _safe_round, PORCENTAJE_MAX_RNC_VENTANAS
from src.services.rnc.rnc_horarios import calculate_t_ext, calculate_tabla_horarios_2
from src.services.rnc.rnc_utils import calculate_datos_tabla


class ZtuBuilder:
    def __init__(self, project_id,enclosures, clima_df, current_user:None, db:None):
        self.project_id = project_id
        self.current_user = current_user
        self.db = db
        self.enclosures = enclosures
        self.promedio_flujo_sol=clima_df["flujo_sol"].mean()
        self.clima_df=clima_df
        self.output_dir = os.path.join("public", "rnc_hours", str(project_id))

    def build(self):
        current_user = self.current_user
        project_id = self.project_id
        db = self.db
        calc_area = {k: v for d in calculate_rnc_area_u_km_op(current_user, project_id, db) for k, v in d.items()}
        rnc_muro = {k: v for d in calculate_rnc_muro(current_user, project_id, db) for k, v in d.items()}
        rnc_techo = {k: v for d in calculate_rnc_techo(current_user, project_id, db) for k, v in d.items()}
        rnc_piso = {k: v for d in calculate_rnc_piso(current_user, project_id, db) for k, v in d.items()}
        output_dir = self.output_dir
        for enclosure in self.enclosures:
            enclosure_id = enclosure.id
            enc_id = enclosure.id

            # --- promedios -------------------------------------------------------
            u_promedio_muros = _safe_div(
                calc_area.get(enc_id, {}).get("suma_u_a", 0.0),
                calc_area.get(enc_id, {}).get("suma_area", 0.0)
            )

            kmop_promedio_muros = _safe_div(
                calc_area.get(enc_id, {}).get("suma_km_op", 0.0),
                rnc_muro.get(enc_id, {}).get("suma_area", 0.0)
            )

            kmop_promedio_techumbre = _safe_div(
                rnc_techo.get(enc_id, {}).get("suma_km_op", 0.0),
                rnc_techo.get(enc_id, {}).get("num_roof", 0.0)
            )

            kmop_promedio_piso = _safe_div(
                rnc_piso.get(enc_id, {}).get("suma_km_op", 0.0),
                rnc_piso.get(enc_id, {}).get("num_floor", 0.0)
            )

            # --- techos/pisos adiabáticos --------------------------------------
            techo_adiabatico = "Si" if rnc_techo.get(enc_id, {}).get("exterior_mayor", 1) == 0 else "No"
            piso_adiabatico = "Si" if rnc_piso.get(enc_id, {}).get("exterior_mayor", 1) == 0 else "No"

            # --- aislamiento exterior ------------------------------------------
            try:
                id_mat_max = rnc_muro[enc_id]["id_material_area_maxima"]
                detail_part = db.query(DetailPart).get(id_mat_max)
                details = db.query(Detail).filter(Detail.detail_part_id == detail_part.id).all()
                detail_ids = [d.id for d in details]
                formulas = db.query(Formulas).filter(Formulas.item_id.in_(detail_ids)).all()
                aislacion_ext = "Si" if any(f.atributs.get("position_insulation", 0) > 0 for f in formulas) else "No"
            except Exception:
                aislacion_ext = "No"

            # --- áreas y espesores ---------------------------------------------
            area_recinto = min(rnc_piso.get(enc_id, {}).get("suma_area", 0.0), 20)
            altura_recinto = getattr(enclosure, "height", 0.0)

            suma_area_muro = rnc_muro.get(enc_id, {}).get("suma_area", 0.0)
            espesor_promedio_muros = _safe_div(
                rnc_muro.get(enc_id, {}).get("suma_area_e_total", 0.0),
                suma_area_muro
            )
            espesor_aislacion_promedio_muros = _safe_div(
                rnc_muro.get(enc_id, {}).get("suma_area_e_aislacion", 0.0),
                suma_area_muro
            )

            m2_muros_ext = rnc_muro.get(enc_id, {}).get("suma_exterior", 0.0)
            m2_vent = rnc_muro.get(enc_id, {}).get("suma_area_ventana", 0.0)
            m2_muros_ad = rnc_muro.get(enc_id, {}).get("suma_adiabatico", 0.0)

            renovaciones_aire = AJUSTE_DESFASE_VERTICAL["infiltraciones"]["valor"]

            porcentaje_vent = _safe_div(m2_vent, (m2_muros_ext + m2_vent))
            volumen_recinto = area_recinto * altura_recinto

            u_kmax_vol = _safe_round(
                _safe_div(u_promedio_muros * _safe_div(kmop_promedio_muros, volumen_recinto) *
                          ((espesor_aislacion_promedio_muros / espesor_promedio_muros) + 1 if espesor_promedio_muros else 1),
                          1),
                0
            )

            # kmop promedio envolvente
            try:
                numerador = (
                        kmop_promedio_muros * m2_muros_ad + m2_muros_ext
                        + kmop_promedio_techumbre * area_recinto
                        + kmop_promedio_piso * area_recinto
                )
                denominador = (area_recinto * 2) + m2_muros_ext + m2_muros_ad
                kmop_promedio_envolvente = _safe_round(_safe_div(numerador, denominador), 0)
            except Exception:
                kmop_promedio_envolvente = 0.0

            # kmop adiabático promedio
            try:
                term_c13 = 0.0 if techo_adiabatico.lower() == "no" else kmop_promedio_techumbre * area_recinto
                kmop_ad_promedio = _safe_div(
                    (kmop_promedio_muros * m2_muros_ad) + term_c13,
                    area_recinto + m2_muros_ad
                )
            except Exception:
                kmop_ad_promedio = 0.0

            # límites de ventanas
            maximo_ventanas = (
                PORCENTAJE_MAX_RNC_VENTANAS
                if porcentaje_vent > PORCENTAJE_MAX_RNC_VENTANAS else porcentaje_vent
            )

            if porcentaje_vent == 0:
                flujo_sol = 0
            else:
                flujo_sol = self.promedio_flujo_sol * maximo_ventanas / porcentaje_vent
            os.makedirs(output_dir, exist_ok=True)
            datos_tabla = calculate_datos_tabla(
                aislacion_ext,
                kmop_ad_promedio,
                u_kmax_vol,
                techo_adiabatico,
                piso_adiabatico,
                renovaciones_aire,
                flujo_sol,
                kmop_promedio_envolvente,
                porcentaje_vent)

            filas = []
            for mes in range(1, 13):
                for hora in range(1, 25):
                    # Valores arbitrarios para probar la función
                    mask = (
                            (self.clima_df["month"] == mes) &
                            (self.clima_df["hours/week"] == hora)
                    )
                    # Sacamos la columna "theta_e;air" de todas las filas que coinciden
                    python_I_755_9514 = self.clima_df.loc[mask, "theta_e;air"].tolist()

                    # Si además necesitas las "D" y las "G" reales (mes y hora) repetidas:
                    python_D_755_9514 = [mes] * len(python_I_755_9514)
                    python_G_755_9514 = [hora] * len(python_I_755_9514)

                    t_ext = calculate_t_ext(
                        python_I_755_9514,
                        python_D_755_9514,
                        python_G_755_9514,
                        mes,
                        hora
                    )
                    t_rnc = 0
                    filas.append({
                        "Valor": hora + 18 if hora + 18 < 24 else hora + 18 - 24,
                        "Mes": mes,
                        "Hora": hora,
                        "T Ext": t_ext,
                        "T RNC": t_rnc
                    })
            df_tabla_horarios = pd.DataFrame(filas)
            df_tabla_clima = calculate_tabla_horarios_2(df_tabla_horarios, db, project_id, enclosure_id)
            for idx, row in df_tabla_horarios.iterrows():
                mes = row["Mes"]  # AI11
                valor = row["Valor"]  # AJ11  (clave para el “BUSCARV”)

                # ► Buscar la fila climática correspondiente (simula BUSCARV)
                fila_clima = df_tabla_clima[df_tabla_clima["Numero Mes"] == mes].iloc[0]

                #   Columna 6 de la tabla AO:AW   →  2(Max1 - Min2)/2
                factor = fila_clima["2(Max1 - Min2)/2"]
                #   Columna 8 de la tabla AO:AW   →  2(Max1 + Min2)/2
                offset = fila_clima["2(Max1 + Min2)/2"]

                # ► Traducción literal de la fórmula de Excel
                if valor < (9 + datos_tabla["desfase_horizontal"]):
                    resultado = (
                            factor * datos_tabla["amplitud"] * np.cos(valor * np.pi / (9 + datos_tabla["desfase_horizontal"]))
                            + (datos_tabla["desfase_vertical_c_sol"] + offset)
                    )
                else:
                    resultado = (
                            -factor * datos_tabla["amplitud"] * np.cos(
                        (valor - 10) * np.pi / (13 + datos_tabla["desfase_horizontal"]))
                            + (datos_tabla["desfase_vertical_s_sol"] + offset)
                    )

                # ► Redondeamos a 2 decimales y guardamos (puedes cambiar el nombre de la columna)
                df_tabla_horarios.at[idx, "T RNC"] = round(resultado, 2)
            # 💾 Crear carpeta específica por enclosure_id
            enclosure_dir = os.path.join(output_dir, str(enclosure_id))
            os.makedirs(enclosure_dir, exist_ok=True)
            # 💾 Guardar archivo .parquet dentro de su carpeta
            output_path = os.path.join(enclosure_dir, f"tabla_horas_{enclosure_id}.parquet")
            df_tabla_horarios.to_parquet(output_path, index=False)
    def get_result_by_enclosure(self,enclosure_id)->pd.DataFrame:
        enclosure_dir = os.path.join(self.output_dir, str(enclosure_id))
        os.makedirs(enclosure_dir, exist_ok=True)
        output_path = os.path.join(enclosure_dir, f"tabla_horas_{enclosure_id}.parquet")
        df = pd.read_parquet(output_path)
        return df
    
