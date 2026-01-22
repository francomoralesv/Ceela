from fastapi import HTTPException

ORIENTACIONES_EXTERIORES = {'N', 'NE', 'E', 'SE', 'S', 'SO', 'O', 'NO'}
ORIENTACIONES_INTERIORES = {'AD', 'IN'}
ORIENTACIONES_TECHO = {'HR'}
ORIENTACIONES_PISO = {'CT', 'FL'}

CHARACTERISTICS_VALID_WALL = {
    'Exterior',
    'Interior climatizado',
    'Interior no climatizado'
}

CHARACTERISTICS_VALID_ROOF = {
    'Exterior',
    'Interior no climatizado'
}

CHARACTERISTICS_VALID_FLOOR = {
    'Exterior',
    'Interior no climatizado'
}

def validate_wall_orientation_characteristics(orientation: str, characteristics: str) -> None:
    """
    Valida que la combinación de orientación y características sea correcta.

    Reglas:
    - Orientaciones interiores (AD, IN) NO pueden ser 'Exterior'
    - Nota: Si usas orientación exterior con characteristics interior,
      el sistema usará la characteristic (se ignora la orientación geográfica)

    Raises:
        HTTPException: Si la validación falla
    """

    if characteristics not in CHARACTERISTICS_VALID_WALL:
        raise HTTPException(
            status_code=400,
            detail=f"Características inválidas: '{characteristics}'. Debe ser una de: {', '.join(CHARACTERISTICS_VALID_WALL)}"
        )

    # Solo validar que orientaciones interiores NO sean marcadas como Exterior
    # (se eliminó la restricción inversa para permitir flexibilidad)
    if orientation in ORIENTACIONES_INTERIORES:
        if characteristics == 'Exterior':
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Error de configuración: Un muro con orientación '{orientation}' "
                    f"NO puede ser 'Exterior'. "
                    f"Debe ser 'Interior climatizado' o 'Interior no climatizado'. "
                    f"Las orientaciones interiores (AD: adyacente climatizado, IN: interior no climatizado) "
                    f"representan muros que dan a espacios interiores y no reciben radiación solar directa."
                )
            )


def validate_wall_has_solar_absorption(orientation: str, characteristics: str) -> dict:
    """
    Verifica si un muro tendrá absorción solar después de ser creado.
    Retorna información útil para el usuario.

    Returns:
        dict con:
        - has_solar_absorption: bool
        - warning_message: str (opcional)
    """
    result = {
        'has_solar_absorption': False,
        'warning_message': None
    }

    if orientation in ORIENTACIONES_EXTERIORES and characteristics == 'Exterior':
        result['has_solar_absorption'] = True
    elif orientation in ORIENTACIONES_INTERIORES or characteristics != 'Exterior':
        result['has_solar_absorption'] = False
        result['warning_message'] = (
            f"Este muro NO tendrá ganancias solares porque: "
            f"Orientación: {orientation}, Características: {characteristics}. "
            f"Si este muro da al exterior y recibe sol, considera cambiar "
            f"la orientación a una exterior (N, NE, E, SE, S, SO, O, NO) "
            f"y las características a 'Exterior'."
        )

    return result


def validate_roof_characteristics(characteristic: str) -> None:
    """
    Valida que las características de un techo sean correctas.

    Reglas:
    - Solo puede ser 'Exterior' o 'Interior no climatizado'

    Raises:
        HTTPException: Si la validación falla
    """
    if characteristic not in CHARACTERISTICS_VALID_ROOF:
        raise HTTPException(
            status_code=400,
            detail=f"Característica inválida para techo: '{characteristic}'. Debe ser 'Exterior' o 'Interior no climatizado'"
        )


def validate_floor_characteristics(characteristic: str) -> None:
    """
    Valida que las características de un piso sean correctas.

    Reglas:
    - Solo puede ser 'Exterior' o 'Interior no climatizado'

    Raises:
        HTTPException: Si la validación falla
    """
    if characteristic not in CHARACTERISTICS_VALID_FLOOR:
        raise HTTPException(
            status_code=400,
            detail=f"Característica inválida para piso: '{characteristic}'. Debe ser 'Exterior' o 'Interior no climatizado'"
        )
