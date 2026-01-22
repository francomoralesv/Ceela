from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from src.models.entity.constant import Constant

def create_constants_type_details(db: Session):
    """Inserta constantes de detalles generales si no existen en la base de datos."""
    
    existing = db.query(Constant).filter_by(type="details", name="generals").first()
    
    if existing:
        print("⚠️ Los datos ya existen, no se insertarán nuevamente.")
        return  

    atributs = {
        "scantillon_location": ["Muro", "Techo", "Piso"],
        "Fourier": {
            "dt_Fourier": 3600,
            "F_ref": 0.5
        },
        "is_wood": [
            {"name": "lambda_min_mad", "value": 0.08, "metric": "W/mK"},
            {"name": "lambda_max_mad", "value": 0.08, "metric": "W/mK"},
            {"name": "p_min_mad", "value": 0.08, "metric": "kg/m3"},
            {"name": "p_max_mad", "value": 1200, "metric": "kg/m3"},
            {"name": "Cp_min_mod", "value": 1400, "metric": "J/kgK"},
            {"name": "e_min_mad", "value": 5.0, "metric": "cm"},
            {"name": "km:op_max", "value": 1.5, "metric": "veces"}
        ],
        "is_insulation": [
            {"name": "lambda_max_ais", "value": 0.10, "metric": "W/mK"},
            {"name": "p_max_ais", "value": 250, "metric": "kg/m3"}
        ],
        "light_for_edge_layer": 0.35,
        "insulation_position": {
            1: "ci",
            3: "ce",
            2: "cm",
            0: "sa"
        },
        "surface_color": {
            "Claro": 0.30,
            "Intermedio": 0.60,
            "Oscuro": 0.90
        },
        "cp_limit": [
            {"represents": "Elemento de Madera", "category": "EM", "value": 50000},
            {"represents": "Elemento Liviano", "category": "EL", "value": 75000},
            {"represents": "Elemento Intermedio", "category": "EI", "value": 110000},
            {"represents": "Elemento Pesado", "category": "EP", "value": 175000},
            {"represents": "", "category": "", "value": 250000}
        ]
    }

    try:
        db.execute(insert(Constant).values(
            type="details",
            name="generals",
            create_status="default",
            atributs=atributs
        ).on_conflict_do_nothing())  

        db.commit()
        print("✅ Datos insertados correctamente.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error al insertar datos: {e}")
        
        

def create_constants_type_elements(db: Session):
    """Inserta constantes de elementos generales si no existen en la base de datos."""
    
    existing = db.query(Constant).filter_by(type="elements", name="generals").first()
    
    if existing:
        print("⚠️ Los datos ya existen, no se insertarán nuevamente.")
        return  

    atributs = {
        "window_closure": ["Abatir", "Corredera", "Guillotina", "Proyectante", "Fila"],
        "frame_material": ["Madera Sin RPT", "PVC Sin RPT", "Metalico Sin RPT", "Madera Con RPT", "PVC Con RPT", "Metalico Con RPT", "Fierro"],
        "thermal_resistances": {
            "rsi_wall": 0.13,
            "rse_wall": 0.04,
            "rsi_roof": 0.09,
            "rse_roof": 0.04,
            "rsi_floor": 0.17,
            "rse_floor": 0.04
        }
    }

    try:
        db.execute(insert(Constant).values(
            type="elements",
            name="generals",
            create_status="default",
            atributs=atributs
        ).on_conflict_do_nothing())  

        db.commit()
        print("✅ Datos insertados correctamente.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error al insertar datos: {e}")


def create_constants_acs_occupancy(db: Session):
    """Inserta constantes de tipo de ocupación ACS si no existen en la base de datos. Tipo_de_ocupación_ACS en tabla Resumen del excel CEEUP V.1.0. Resultados"""
    
    print("Iniciando la inserción de constantes de ocupación ACS...")
    existing = db.query(Constant).filter_by(type="acs", name="occupancy").first()
    
    if existing:
        print("⚠️ Los datos ya existen, no se insertarán nuevamente.")
        return  

    atributs = {
        "tipo_de_ocupacion_acs": {
            "Hospitales y clínicas": 80,
            "Ambulatorio y centros de salud": 60,
            "Hotel 5 Estrellas": 100,
            "Hotel 4 Estrellas": 80,
            "Hotel 3 Estrellas / Apart Hotel": 60,
            "Hotel/Hostal/Apart Hotel": 50,
            "Hostal/Pensión/Apart hotel": 40,
            "Camping/campamentos": 30,
            "Residencia": 60,
            "Centro penitenciario": 40,
            "Albergue": 35,
            "Vestuarios": 30,
            "Escuela sin duchas": 6,
            "Escuela con duchas": 30,
            "Cuarteles": 40,
            "Fábricas": 30,
            "Oficinas": 3,
            "Gimnasios": 30,
            "Restaurantes": 12,
            "Cafeterías": 2
        }
    }

    try:
        db.execute(insert(Constant).values(
            type="acs",
            name="occupancy",
            create_status="default",
            atributs=atributs
        ).on_conflict_do_nothing())  

        db.commit()
        print("✅ Datos insertados correctamente.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error al insertar datos: {e}")


def create_constants_enclosure(db: Session):
    existing = db.query(Constant).filter_by(type="enclosures", name="enclosures").first()
    
    if existing:
        print("⚠️ Los datos ya existen, no se insertarán nuevamente.")
        return  
    
    atributs = {
        "co2_pers": {
            "Sedentario": 19,
            "Ejercicio Bajo": 50,
            "Ejercicio Medio": 100,
            "Ejercicio Alto": 170,
            "Jardin Infantil": 18,
            "Colegio": 19 
        },
        "idas": {
            "ida1": 400,
            "ida2": 600,
            "ida3": 1000,
            "ida4": 0
        },
        "estrategia_iluminacion": {
            "Sin estrategia": 0,
            "Dimmer": 0.20,
            "Sectorizacion": 0.35,
            "Sensor de Luz Nat": 0.55
        },
        "funcionamiento_semanal": {
            "7x0": "Lunes-Domingo",
            "6x1": "Lunes-Sabado",
            "5x2": "Lunes-Viernes",
            "4x3": "4 dias a la semana laboral",
            "3x4": "3 dias a la semana laboral",
            "2x5": "2 dias a la semana laboral",
            "1x6": "1 dias a la semana laboral",
            "0x7": "0 dias a la semana laboral"
        }
    }
    
    try:
        db.execute(insert(Constant).values(
            type="enclosures",
            name="enclosures",
            create_status="default",
            atributs=atributs
        ).on_conflict_do_nothing())  

        db.commit()
        print("✅ Datos insertados correctamente.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error al insertar datos: {e}")

def create_constants_energy_and_systems(db: Session):
    """Inserta constantes relacionadas con energía y sistemas en la base de datos."""

    existing = db.query(Constant).filter_by(type="energy_systems", name="general").first()
    print(f"Iniciando la inserción de constantes de energía y sistemas... {existing}")

    if existing:
        print("⚠️ Los datos ya existen, no se insertarán nuevamente.")
        return  

    atributs = {
        "combustibles": [
            {"name": "Electricidad", "code": "Elect", "fep": 1.90},
            {"name": "Petróleo", "code": "Pet", "fep": 1.10},
            {"name": "Gas natural", "code": "GN", "fep": 1.10},
            {"name": "Gas licuado", "code": "GL", "fep": 1.10},
            {"name": "Kerosene domestico", "code": "Keros", "fep": 1.10},
            {"name": "Leña", "code": "Leña", "fep": 1.10},
            {"name": "Pellets de madera", "code": "Pellets", "fep": 1.10},
            {"name": "Carbón", "code": "Carbón", "fep": 1.10}
        ],
        "rendimiento_acs": [
            {"name": "Sistema por defecto - No se dispone de sistema de ACS", "code": "Sin Sist", "value": 0.70},
            {"name": "Sistema de calentamiento de agua directo a gas", "code": "Directo-gas", "value": 0.70},
            {"name": "Sistema de calentamiento de agua directo a electricidad", "code": "Directo-Elect", "value": 1.00},
            {"name": "Sistema de calentamiento de agua con estanque eléctrico", "code": "Estanque-Elect", "value": 1.00},
            {"name": "Sistema de calentamiento de agua con caldera convencional", "code": "Caldera-Conv", "value": 0.70},
            {"name": "Sistema de calentamiento de agua con caldera a condensación", "code": "Caldera-Cond", "value": 0.80},
            {"name": "Calentamiento de agua con bomba de calor tradicional agua - agua", "code": "Bom-Cal Ag-Ag", "value": 1.80},
            {"name": "Calentamiento de agua con bomba de calor de flujo de refrigerante variable agua - agua", "code": "V.R.V Ag-Ag", "value": 2.00},
            {"name": "Calentamiento de agua con bomba de calor aire - agua", "code": "Bom-Cal Ai-Ag", "value": 1.80},
            {"name": "Calentamiento de agua con bomba de calor de flujo de refrigerante variable aire - agua", "code": "V.R.V Ai-Ag", "value": 2.00}
        ],
        "distribucion_acs": [
            {"name": "Red de cañerías con aislación", "code": "Con Ais", "value": 1.00},
            {"name": "Red de cañerías sin aislación", "code": "Sin Ais", "value": 0.90},
            {"name": "No tiene sistema de ACS", "code": "No tiene sistema de ACS", "value": 1.00}
        ],
        "control_acs": [
            {"name": "Sistema de control por potencia", "code": "Sistema de control por potencia", "value": 0.92},
            {"name": "Control automático basado en la medición de la temperatura del agua", "code": "Automático base a T° agua", "value": 1.00}
        ],
        "rendimiento_calef": [
            {"name": "Sistema por defecto - No se dispone de sistema de calefacción", "code": "Sin Sist", "value": 0.45},
            {"name": "Caldera a gas sin condensación encendido piloto control on/of", "code": "Caldera-Encendido Piloto", "value": 0.71},
            {"name": "Caldera a gas sin condensación encendido electrónico control on/of", "code": "Caldera-Encendido Electronico", "value": 0.75},
            {"name": "Caldera a gas con condensación encendido electrónico control modulado", "code": "Caldera-Cond-Encendido electrónico", "value": 0.85},
            {"name": "Caldera a petróleo", "code": "Caldera a petróleo", "value": 0.80},
            {"name": "Equipo localizado sin evacuación de gases al exterior", "code": "Gas-Sin Evac Exterior", "value": 0.45},
            {"name": "Calefactor electrico por resistencia fijo", "code": "Calefactor electrico por resistencia fijo", "value": 1.00},
            {"name": "Equipo localizado a gas con evacuación de gases", "code": "Equipo Loc. gas con Evac. gases", "value": 0.62},
            {"name": "Calefactor localizado a leña", "code": "Calefactor localizado a leña", "value": 0.45},
            {"name": "Calefactor a pellet", "code": "Calefactor a pellet", "value": 0.60},
            {"name": "Caldera a leña", "code": "Caldera a leña", "value": 0.55},
            {"name": "Caldera a pellet", "code": "Caldera a pellet", "value": 0.65},
            {"name": "Bomba de Calor por aire", "code": "Bom-Cal Ai-Ai <40kW", "value": 3.30},
            {"name": "Bomba de Calor por aire", "code": "Bom-Cal Ai-Ai >40kW- <70kW", "value": 3.20},
            {"name": "Bomba de Calor por aire", "code": "Bom-Cal Ai-Ai >70kW", "value": 3.10},
            {"name": "Bomba de Calor por agua o evaporación", "code": "Bom-Cal Ag-Ag <40kW", "value": 4.20},
            {"name": "Bomba de Calor por agua o evaporación", "code": "Bom-Cal Ag-Ag >40kW- <70kW", "value": 3.60},
            {"name": "Bomba de Calor por agua o evaporación", "code": "Bom-Cal Ag-Ag >70kW", "value": 3.10}
        ],
        "rendimiento_ref": [
            {"name": "Bomba de Calor por aire", "code": "Bom-Cal Ai-Ai <40kW", "value": 3.10},
            {"name": "Bomba de Calor por aire", "code": "Bom-Cal Ai-Ai >40kW- <70kW", "value": 3.00},
            {"name": "Bomba de Calor por aire", "code": "Bom-Cal Ai-Ai >70kW", "value": 2.70},
            {"name": "Bomba de Calor por agua o evaporación", "code": "Bom-Cal Ag-Ag <40kW", "value": 3.30},
            {"name": "Bomba de Calor por agua o evaporación", "code": "Bom-Cal Ag-Ag >40kW- <70kW", "value": 3.10},
            {"name": "Bomba de Calor por agua o evaporación", "code": "Bom-Cal Ag-Ag >70kW", "value": 2.60},
            {"name": "Tornillo enfriado por agua", "code": "Tornillo <528kW", "value": 5.20},
            {"name": "Tornillo enfriado por agua", "code": "Tornillo >528kW - <1055kW", "value": 5.60},
            {"name": "Tornillo enfriado por agua", "code": "Tornillo >1055kW", "value": 6.15},
            {"name": "Compresor centrifugo enfriado por agua", "code": "Comp. Cent. <528kW", "value": 5.25},
            {"name": "Compresor centrifugo enfriado por agua", "code": "Comp. Cent. >528kW - <1055kW", "value": 5.90},
            {"name": "Compresor centrifugo enfriado por agua", "code": "Comp. Cent. >1055kW", "value": 6.40}
        ],
        "distribucion_hvac": [
            {"name": "Sistema unitario autocontenido", "code": "Sistema unitario autocontenido", "value": 1.00},
            {"name": "Edificio con sistema centralizado", "code": "Sist Centralizado", "value": 0.95},
            {"name": "Sistema de calefacción distrital", "code": "Calef distrital", "value": 0.80},
            {"name": "Valor por defecto si no tiene sistema de calefacción", "code": "Sin Sistema", "value": 1.00}
        ],
        "control_hvac": [
            {"name": "Control automático", "code": "Control automático", "value": 1.00},
            {"name": "Control manual", "code": "Control manual", "value": 0.80},
            {"name": "Sin sistema de calefacción", "code": "Sin Sistema", "value": 0.80}
        ],
        "consumos_por_fuente_de_energia": [
            {"name": "Electricidad", "code": "Elect", "co2_eq": 0.31},
            {"name": "Petróleo", "code": "Pet", "co2_eq": 0.24},
            {"name": "Gas natural", "code": "GN", "co2_eq": 0.20},
            {"name": "Gas licuado", "code": "GL", "co2_eq": 0.23},
            {"name": "Kerosene domestico", "code": "Keros", "co2_eq": 0.26},
            {"name": "Leña", "code": "Leña", "co2_eq": None},
            {"name": "Pellets de madera", "code": "Pellets", "co2_eq": None},
            {"name": "Carbón", "code": "Carbón", "co2_eq": 0.50}
        ]
    }

    try:
        db.execute(insert(Constant).values(
            type="energy_systems",
            name="general",
            create_status="default",
            atributs=atributs
        ).on_conflict_do_nothing())  

        db.commit()
        print("✅ Datos insertados correctamente.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error al insertar datos: {e}")




def create_constants_t_red(db: Session):
            """Inserta constantes de temperatura de red por mes."""
            
            existing = db.query(Constant).filter_by(type="temperature", name="red").first()
            
            if existing:
                print("⚠️ Los datos ya existen, no se insertarán nuevamente.")
                return  

            atributs = {
                "monthly": {
                    "january": 17.5,
                    "february": 16.0,
                    "march": 16.0,
                    "april": 14.0,
                    "may": 12.0,
                    "june": 11.0,
                    "july": 11.0,
                    "august": 11.7,
                    "september": 12.5,
                    "october": 14.4,
                    "november": 15.5,
                    "december": 17.0
                }
            }

            try:
                db.execute(insert(Constant).values(
                    type="temperature",
                    name="red",
                    create_status="default",
                    atributs=atributs
                ).on_conflict_do_nothing())

                db.commit()
                print("✅ Datos insertados correctamente.")
            except Exception as e:
                db.rollback()
                print(f"❌ Error al insertar datos: {e}")
                
                
                
def create_constants_month_water(db: Session):
                    """Inserta constantes de consumo de agua por mes."""
                    
                    existing = db.query(Constant).filter_by(type="water", name="monthly").first()
                    
                    if existing:
                        print("⚠️ Los datos ya existen, no se insertarán nuevamente.")
                        return  

                    atributs = {
                        "monthly": {
                            "january": 3720,
                            "february": 3360,
                            "march": 3720,
                            "april": 3600,
                            "may": 3720,
                            "june": 3600,
                            "july": 3720,
                            "august": 3720,
                            "september": 3600,
                            "october": 3720,
                            "november": 3600,
                            "december": 3720
                        }
                    }

                    try:
                        db.execute(insert(Constant).values(
                            type="water",
                            name="monthly", 
                            create_status="default",
                            atributs=atributs
                        ).on_conflict_do_nothing())

                        db.commit()
                        print("✅ Datos insertados correctamente.")
                    except Exception as e:
                        db.rollback()
                        print(f"❌ Error al insertar datos: {e}")
                        
                        
                        
def create_constants_human_activity(db: Session):
                            """Inserta constantes para actividad humana."""
                            
                            existing = db.query(Constant).filter_by(type="human_activity", name="water_production").first()
                            
                            if existing:
                                print("⚠️ Los datos ya existen, no se insertarán nuevamente.")
                                return  

                            atributs = {
                                "activity_levels": [
                                    {"name": "Sedentario", "gr_water_hour": 45, "kg_water_sec": 0.000013},
                                    {"name": "Ejercicio Bajo", "gr_water_hour": 100, "kg_water_sec": 0.000028},
                                    {"name": "Ejercicio Medio", "gr_water_hour": 160, "kg_water_sec": 0.000044},
                                    {"name": "Ejercicio Alto", "gr_water_hour": 250, "kg_water_sec": 0.000069},
                                    {"name": "Jardin Infantil", "gr_water_hour": 40, "kg_water_sec": 0.000011},
                                    {"name": "Colegio", "gr_water_hour": 45, "kg_water_sec": 0.000013}
                                ]
                            }

                            try:
                                db.execute(insert(Constant).values(
                                    type="human_activity",
                                    name="water_production",
                                    create_status="default", 
                                    atributs=atributs
                                ).on_conflict_do_nothing())

                                db.commit()
                                print("✅ Datos insertados correctamente.")
                            except Exception as e:
                                db.rollback()
                                print(f"❌ Error al insertar datos: {e}")