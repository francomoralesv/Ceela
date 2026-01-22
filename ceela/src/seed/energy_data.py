from sqlmodel import Session
from src.models.entity.energy_data import EnergyData  # Ajusta la importación a tu estructura de proyecto

def seed_energy_data(db: Session):
    """
    Inserta en la tabla 'energy_data' los datos de:
      - combustible
      - rendimiento_acs
      - distribucion_acs
      - control_acs
      - rendimiento_calef
      - rendimiento_ref
      - distribucion_hvac
      - control_hvac
      - co2_eq

    Si ya existen registros de alguno de estos 'type', no se insertan duplicados.
    """

    # Tipos que se van a insertar
    types_to_seed = [
        "combustible", 
        "rendimiento_acs", 
        "distribucion_acs", 
        "control_acs",
        "rendimiento_calef",
        "rendimiento_ref",
        "distribucion_hvac",
        "control_hvac",
        "co2_eq"
    ]

    # Verificamos si ya existe al menos un registro con alguno de estos types
    existing = db.query(EnergyData).filter(EnergyData.type.in_(types_to_seed)).first()
    if existing:
        print("⚠️ Los datos de seed ya existen, no se insertarán nuevamente.")
        return

    # Datos a insertar, agrupados por 'type'
    data_seed = {
        "combustible": [
            {"name": "Elect",   "value": 1.90},
            {"name": "Pet",     "value": 1.00},
            {"name": "GN",      "value": 1.10},
            {"name": "GL",      "value": 1.10},
            {"name": "Keros",   "value": 1.10},
            {"name": "Leña",    "value": 0.90},
            {"name": "Pellets", "value": 1.10},
            {"name": "Carbón",  "value": 1.10}
        ],
        "rendimiento_acs": [
            {"name": "Sin Sist",       "value": 0.70},
            {"name": "Directo-gas",    "value": 0.90},
            {"name": "Directo-Elect",  "value": 1.00},
            {"name": "Estanque-Elect", "value": 1.00},
            {"name": "Caldera-Conv",   "value": 0.80},
            {"name": "Caldera-Cond",   "value": 0.80},
            {"name": "V.R.V Ag-Ag",    "value": 0.80},
            {"name": "Bom-Cal Ag-Ag",  "value": 0.80}
        ],
        "distribucion_acs": [
            {"name": "Con Ais",                 "value": 1.00},
            {"name": "Sin Ais",                 "value": 0.90},
            {"name": "No tiene sistema de ACS", "value": 1.00}
        ],
        "control_acs": [
            {"name": "Sistema de control por potencia", "value": 0.92},
            {"name": "Automático base a T° agua",       "value": 1.00}
        ],
        "rendimiento_calef": [
            {"name": "Sin Sist",                          "value": 0.45},
            {"name": "Caldera-Encendido Piloto",          "value": 0.70},
            {"name": "Caldera-Encendido Electronico",     "value": 0.71},
            {"name": "Caldera-Cond-Encendido electrónico", "value": 0.73},
            {"name": "Caldera a petróleo",                "value": 0.81},
            {"name": "Gas-Sin Evac Exterior",             "value": 0.86},
            {"name": "Equipo Loc. gas con Evac. gases",   "value": 0.79},
            {"name": "Calefactor localizado a leña",      "value": 0.79},
            {"name": "Caldera a leña",                    "value": 0.85},
            {"name": "Caldera a pellet",                  "value": 0.85}
        ],
        "rendimiento_ref": [
            {"name": "Bom-Cal Ai-Ai <40kW", "value": 3.10},
            {"name": "Bom-Cal Ai-Ai <70kW", "value": 3.00},
            {"name": "Bom-Cal Ai-Ag <40kW", "value": 3.10},
            {"name": "Bom-Cal Ai-Ag <70kW", "value": 3.00},
            {"name": "Tornillo <=528kW",    "value": 1.05},
            {"name": "Tornillo <=1055kW",   "value": 1.05},
            {"name": "Comp. Cent. <=528kW", "value": 1.05},
            {"name": "Comp. Cent. >1055kW", "value": 1.05}
        ],
        "distribucion_hvac": [
            {"name": "Sistema unitario autocontenido", "value": 1.00},
            {"name": "Sist Centralizado",              "value": 0.95},
            {"name": "Calef distrital",                 "value": 0.90},
            {"name": "Sin Sistema",                     "value": 1.00}
        ],
        "control_hvac": [
            {"name": "Control automático", "value": 1.00},
            {"name": "Control manual",     "value": 0.90},
            {"name": "Sin Sistema",        "value": 1.00}
        ],
        "co2_eq": [
            {"name": "Elect",   "value": 0.31},
            {"name": "Pet",     "value": 0.29},
            {"name": "GN",      "value": 0.25},
            {"name": "GL",      "value": 0.25},
            {"name": "Keros",   "value": 0.26},
            {"name": "Leña",    "value": 0.15},
            {"name": "Pellets", "value": 0.20},
            {"name": "Carbón",  "value": 0.29}
        ]
    }

    # Generamos todos los registros a insertar con una sola comprensión de lista
    registros = [
        EnergyData(type=data_type, name=record["name"], value=record["value"])
        for data_type, records in data_seed.items()
        for record in records
    ]

    # Insertamos de forma masiva
    db.add_all(registros)

    try:
        db.commit()
        print("✅ Datos insertados correctamente.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error al insertar datos: {e}")