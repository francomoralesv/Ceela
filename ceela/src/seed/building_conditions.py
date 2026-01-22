import pandas as pd
from sqlalchemy.orm import Session
from src.models.entity.building_conditions import BuildingCondition
from src.services.calculator.calculator_enclosures import calculate_potencia_propuesta, calculate_r_pers

def safe_get_value(row, col_tuple):
    """ Obtiene el valor de una celda y maneja valores NaN. """
    value = row[col_tuple]

    if pd.isna(value):  
        return 0  

    return value.item() if hasattr(value, "item") else value

def import_building_conditions(file_path: str, db: Session):
    try:
        if db.query(BuildingCondition).first():
            print("Datos ya insertados")
            return {"message": "Los datos ya han sido importados previamente."}

        df = pd.read_excel(
            file_path,
            sheet_name="2. Perfiles de ocupacion",
            engine="openpyxl",
            skiprows=11,
            nrows=30,
            header=[0, 1]
        ).iloc[:, 23:41].fillna(0)

        section_mapping = {
            "ventilation_flows": {
                "cauldal_min_salubridad": {
                    "r_pers": ("R-pers", "[L/s]"),
                    "ida": ("IDA", "Unnamed: 24_level_1"),
                    "ocupacion": ("Ocupacion", "Unnamed: 25_level_1")
                },
                "caudal_impuesto": {"vent_noct": ("Vent Noct ", "[1/h]")},
                "infiltraciones": ("aciones", "[1/h]"),
                "recuperador_calor": (" de calor", "[%]")
            },
            "lightning": {
                "potencia_base": ("Base", "[W/m2]"),
                "estrategia": ("Estrategia", "Unnamed: 30_level_1"),
                "potencia_propuesta": ("Propuesta", "[W/m2]")
            },
            "internal_loads": {
                "usuarios": ("Propuesta", "[m2/pers]"),
                "calor_latente": ("Latente", "[W/pers].1"),
                "calor_sensible": ("Sensible", "[W/pers].1"),
                "equipos": ("Sensible", "[W/m2]"),
                "horario": {
                    "funcionamiento_semanal": ("Funcionamiento", "Semanal"),
                    "laboral": {"inicio": ("Laboral", "Ti"), "fin": ("Laboral", "Tf")}
                }
            },
            "schedule_weather": {
                "recinto": {
                    "climatizado": ("Climatizado", "Si/No"),
                    "desfase_clima": ("Hrs Desfase", "Clima (Inv)")
                }
            }
        }

        def extract_value(row, path):
            """ Extrae el valor del DataFrame con seguridad. """
            return row.get(path[0], {}).get(path[1], 0) if isinstance(path, tuple) else row.get(path, 0)

        records = []
        for idx, row in df.iterrows():
            attributes = {
                section: {
                    key: (
                        extract_value(row, value)
                        if not isinstance(value, dict)
                        else {
                            sub_key: (
                                extract_value(row, sub_value)
                                if not isinstance(sub_value, dict)
                                else {k: extract_value(row, v) for k, v in sub_value.items()}
                            )
                            for sub_key, sub_value in value.items()
                        }
                    )
                    for key, value in values.items()
                }
                for section, values in section_mapping.items()
            }

            try:
                attributes["ventilation_flows"]["cauldal_min_salubridad"]["r_pers"] = calculate_r_pers(
                    str(attributes["ventilation_flows"]["cauldal_min_salubridad"].get("ida")),
                    str(attributes["ventilation_flows"]["cauldal_min_salubridad"].get("ocupacion")),
                    db
                )
            except Exception as e:
                print(f"Error en R-Pers en fila {idx}: {str(e)}")

            try:
                attributes["lightning"]["potencia_propuesta"] = calculate_potencia_propuesta(
                    float(attributes["lightning"].get("potencia_base", 0)),
                    str(attributes["lightning"].get("estrategia", "")),
                    db
                )
            except Exception as e:
                print(f"Error en Potencia Propuesta en fila {idx}: {str(e)}")

            records.extend(
                {"enclosure_id": idx + 1, "type": section, "attributes": attributes[section], "created_status": "default"}
                for section in attributes if attributes[section]
            )

        db.bulk_insert_mappings(BuildingCondition, records)
        db.commit()

        return {"message": f"{len(records)} registros importados correctamente"}

    except Exception as e:
        db.rollback()
        print(f"Error en la importación: {str(e)}")
