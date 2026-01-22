
from sqlmodel import Session, select

from src.models.entity.constant import Constant
from src.models.entity.heating_config import HeatingConfig


class HeatingConfigService:
    @staticmethod
    def get_heating_config(project_id: int, db: Session):
        statement = select(HeatingConfig).where(
            HeatingConfig.project_id == project_id)
        result = db.execute(statement)
        return result.scalars().first()

    @staticmethod
    def create_heating_config(project_id: int, data: dict, db: Session):
        # Check if heating config exists
        existing_config = HeatingConfigService.get_heating_config(
            project_id, db)
        if existing_config:
            # Update existing config
            for key, value in data.items():
                setattr(existing_config, key, value)
            db.commit()
            db.refresh(existing_config)
            return existing_config
        else:
            # Create new config
            heating_config = HeatingConfig(**data)
            db.add(heating_config)
            db.commit()
            db.refresh(heating_config)
            return heating_config

    @staticmethod
    def get_consumo_heating_config_constant(project_id: int, db: Session):
        try:
            existing = db.query(Constant).filter_by(type="energy_systems", name="general").first()
            consumos_por_fuente_de_energia = existing.atributs.get('consumos_por_fuente_de_energia')
            config=HeatingConfigService.get_heating_config(project_id, db)
            consumos_por_fuente_de_energia = next((x for x in consumos_por_fuente_de_energia if x['code'] == config.combustible_codigo), None)
            return consumos_por_fuente_de_energia.get('co2_eq', 0.31)
        except Exception:
            return 0.31 #Electricidad

    @staticmethod
    def get_combustible_heating_config_constant(project_id: int, db: Session):
        try:
            existing = db.query(Constant).filter_by(type="energy_systems", name="general").first()
            combustible = existing.atributs.get('combustibles')
            config=HeatingConfigService.get_heating_config(project_id, db)
            combustible = next((x for x in combustible if x['code'] == config.combustible_codigo), None)
            return combustible.get('fep', 1.9)
        except Exception:
            return 1.9 #Electricidad