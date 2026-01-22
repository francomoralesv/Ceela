from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.models.entity.levels import Level


def create_levels_seed(db: Session):
    """
    Crea 100 niveles (Nivel_001 a Nivel_100) en la tabla 'levels',
    sólo si actualmente está vacía.
    """
    try:
        # Verificar si ya existen niveles
        existing_levels = db.query(Level).first()

        if existing_levels:
            return {
                "message": "La tabla 'levels' ya contiene datos. No se realizó ningún cambio.",
                "status": "skipped"
            }

        # Crear 100 niveles
        for i in range(1, 16):
            nombre_nivel = f"Nivel_{i:03}"  # Nivel_001, Nivel_002, etc.
            descripcion = f"Este es el {nombre_nivel}"

            nuevo_nivel = Level(
                name=nombre_nivel,
                description=descripcion
            )
            db.add(nuevo_nivel)

        # Confirmar la transacción
        db.commit()

        return {
            "message": "Se crearon los 100 niveles correctamente.",
            "total_rows": 100,
            "status": "created"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear los niveles: {str(e)}"
        )