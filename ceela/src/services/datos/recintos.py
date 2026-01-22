from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.models.entity.enclosure_general import EnclosureGenerals
from src.models.entity.project_table import Project
from src.models.entity.floor import FloorEnclosure
from src.models.entity.enclosure import Enclosure


def get_enclosure_by_id(enclosure_id: int, db: Session):
    """
    Obtiene información básica de un enclosure específico por su ID.

    Args:
        enclosure_id: ID del recinto/enclosure a consultar
        db: Sesión de base de datos

    Returns:
        Dict con la información básica del enclosure o None si no existe
    """
    enclosure = db.query(EnclosureGenerals).filter(
        EnclosureGenerals.id == enclosure_id,
        EnclosureGenerals.is_deleted == False
    ).first()
    if not enclosure:
        raise HTTPException(
            status_code=404,
            detail="Enclosure no encontrado"
        )

    # Sumar el área total de los pisos
    pisos = db.query(FloorEnclosure).filter(
        FloorEnclosure.enclosure_id == enclosure_id
    ).all()
    total_area = 0.0
    for piso in pisos:
        try:
            total_area += float(getattr(piso, "area", 0.0))
        except Exception:
            total_area += 0.0

    # Obtener información del perfil de ocupación
    profile_id = getattr(enclosure, "occupation_profile_id", None)
    profile_name = None
    if profile_id:
        profile = db.query(Enclosure).filter(
            Enclosure.id == profile_id
        ).first()
        if profile:
            profile_name = profile.name

    # Generar los 4 casos "propuestos" (ej. EnclosureName-Base0°, etc.)
    angles = [0, 90, 180, 270]
    proposed_cases = []
    for angle in angles:
        case_name = f"{enclosure.name_enclosure}-Base{angle}°"
        proposed_cases.append({
            "name": case_name,
            "area": total_area,
            "occupation_profile_id": profile_id,
            "occupation_profile_name": profile_name,
            "altura": enclosure.height
        })

    enclosure_data = {
        "altura": enclosure.height,
        "enclosure_id": enclosure.id,
        "name": enclosure.name_enclosure,
        "area": total_area,
        "occupation_profile_id": profile_id,
        "occupation_profile_name": profile_name,
        "proposed_cases": proposed_cases
    }
    return enclosure_data


def get_info_recinto(project_id: int, current_user: dict=None, db: Session=None, enclosure_id: int = None):
    """
    Obtiene enclosures asociados a un proyecto. Si se especifica un enclosure_id, se obtiene solo ese enclosure;
    de lo contrario, se obtienen todos los enclosures del proyecto. Para cada uno:
      - Suma el área de todos los pisos (consultados en la tabla FloorEnclosure).
      - Obtiene el occupation_profile_id y consulta la tabla Enclosure para extraer el nombre del perfil.
      - Genera 4 "casos" propuestos con sufijos -Base0°, -Base90°, -Base180°, -Base270°.

    :param project_id: Identificador del proyecto.
    :param current_user: Diccionario con la info del usuario actual (project.user_id).
    :param db: Sesión de base de datos (SQLAlchemy Session).
    :param enclosure_id: (Opcional) Identificador de un enclosure específico.
    :return: Lista de diccionarios con la información de cada enclosure (o un único diccionario si se especifica enclosure_id).
    """

    # Verificar que el proyecto pertenezca al usuario actual
    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=400,
            detail="El proyecto no pertenece al usuario actual"
        )

    # Si se especifica un enclosure_id, se filtra por él; de lo contrario se traen todos los enclosures del proyecto
    query = db.query(EnclosureGenerals).filter(
        EnclosureGenerals.project_id == project_id
    )
    if enclosure_id is not None:
        query = query.filter(EnclosureGenerals.id == enclosure_id)

    enclosures = query.all()

    if enclosure_id is not None and not enclosures:
        raise HTTPException(
            status_code=404,
            detail="Enclosure no encontrado en el proyecto"
        )

    enclosures_info = []

    for enclosure in enclosures:
        # 1) Sumar el área total de los pisos que pertenecen a este enclosure
        pisos = db.query(FloorEnclosure).filter(
            FloorEnclosure.enclosure_id == enclosure.id
        ).all()

        total_area = 0.0
        for piso in pisos:
            try:
                total_area += float(getattr(piso, "area", 0.0))
            except Exception:
                total_area += 0.0

        # 2) Obtener occupation_profile_id y consultar la tabla Enclosure para extraer el nombre del perfil
        profile_id = getattr(enclosure, "occupation_profile_id", None)
        profile_name = None
        if profile_id:
            profile = db.query(Enclosure).filter(
                Enclosure.id == profile_id
            ).first()
            if profile:
                profile_name = profile.name

        # 3) Generar los 4 casos "propuestos" (ej. EnclosureName-Base0°, etc.)
        angles = [0, 90, 180, 270]
        proposed_cases = []
        for angle in angles:
            case_name = f"{enclosure.name_enclosure}-Base{angle}°"
            proposed_cases.append({
                "name": case_name,
                "area": total_area,  # Se asume que usan la misma área
                "occupation_profile_id": profile_id,
                "occupation_profile_name": profile_name,
                "altura": enclosure.height
            })

        # Construir el diccionario con la info del enclosure
        enclosure_data = {
            "altura": enclosure.height,
            "enclosure_id": enclosure.id,
            "name": enclosure.name_enclosure,
            "area": total_area,
            "occupation_profile_id": profile_id,
            "occupation_profile_name": profile_name,
            "proposed_cases": proposed_cases
        }

        enclosures_info.append(enclosure_data)

    return enclosures_info
