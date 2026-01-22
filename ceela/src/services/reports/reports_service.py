from fastapi import APIRouter, Depends
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import desc
from src.services.database.db_connection import get_db
from src.services.calculation_result.calculation_result_service import get_calculation_results_report


def generate_users_report(db: Session):
    """
    Genera un reporte de la cantidad de usuarios activos e inactivos.

    Retorna:
        dict: Un diccionario con la cantidad de usuarios activos e inactivos.
    """
    query = """
        SELECT active, COUNT(*) as total
        FROM users
        GROUP BY active
    """
    df_users = pd.read_sql(query, db.get_bind())
    df_users['active'] = df_users['active'].map(
        {True: 'Activos', False: 'Inactivos'})
    return df_users.to_dict()


def generate_projects_by_country_report(db: Session):
    """
    Genera un reporte de la cantidad de proyectos por país.

    Retorna:
        dict: Un diccionario con la cantidad de proyectos por país.
    """
    query = """
        SELECT country, COUNT(*) as total
        FROM projects
        GROUP BY country
        ORDER BY total DESC
    """
    df_projects = pd.read_sql(query, db.get_bind())
    return df_projects.to_dict()


def generate_projects_status_report(db: Session):
    """
    Genera un reporte del estado de los proyectos.

    Retorna:
        dict: Un diccionario con la cantidad de proyectos por estado.
    """
    query = """
        SELECT status, COUNT(*) as total
        FROM projects
        GROUP BY status
        ORDER BY total DESC
    """
    df_status = pd.read_sql(query, db.get_bind())
    return df_status.to_dict()


def generate_building_levels_distribution_report(db: Session):
    """
    Genera un reporte de la distribución de niveles de edificios.

    Retorna:
        dict: Un diccionario con la cantidad de edificios por número de niveles.
    """
    query = """
        SELECT number_levels, COUNT(*) as total
        FROM projects
        GROUP BY number_levels
        ORDER BY number_levels
    """
    df_levels = pd.read_sql(query, db.get_bind())
    return df_levels.to_dict()


def generate_total_surface_by_country_report(db: Session):
    """
    Genera un reporte de la superficie total construida por país.

    Retorna:
        dict: Un diccionario con la superficie total construida por país.
    """
    query = """
        SELECT country, SUM(built_surface) as total_surface
        FROM projects
        GROUP BY country
        ORDER BY total_surface DESC
    """
    df_surface = pd.read_sql(query, db.get_bind())
    return df_surface.to_dict()


def generate_building_type_distribution_report(db: Session):
    """
    Genera un reporte de la distribución de tipos de edificios.

    Retorna:
        dict: Un diccionario con la cantidad de proyectos por tipo de edificio.
    """
    query = """
        SELECT building_type, COUNT(*) as total_proyectos
        FROM projects
        WHERE is_deleted = false
        GROUP BY building_type
        ORDER BY total_proyectos DESC;
    """
    df = pd.read_sql(query, db.get_bind())
    return df.to_dict()


def generate_projects_by_user_report(db: Session):
    """
    Genera un reporte del número de proyectos registrados por usuario.

    Retorna:
        None: Muestra un gráfico de barras con la cantidad de proyectos por usuario.
    """
    query = """
        SELECT u.name || ' ' || u.lastname AS usuario, COUNT(p.id) AS total_proyectos
        FROM users u
        LEFT JOIN projects p ON u.id = p.user_id
        WHERE p.is_deleted = false
        GROUP BY usuario
        ORDER BY total_proyectos DESC;
    """
    df = pd.read_sql(query, db.get_bind())
    return df.to_dict()


def generate_projects_by_month_report(db: Session):
    """
    Genera un reporte de la cantidad de proyectos creados o modificados por mes.

    Retorna:
        dict: Un diccionario con la cantidad de proyectos por mes.
    """
    query = """
            SELECT 
                DATE_TRUNC('month', created_at) as month,
                COUNT(*) as total_created,
                COUNT(CASE WHEN updated_at != created_at THEN 1 END) as total_modified
            FROM projects
            WHERE is_deleted = false
            GROUP BY DATE_TRUNC('month', created_at)
            ORDER BY month DESC
        """
    df = pd.read_sql(query, db.get_bind())
    df['month'] = df['month'].dt.strftime('%Y-%m')
    return df.to_dict()


def generate_projects_by_region_report(db: Session):
    """
    Genera un reporte de la cantidad de proyectos por región.

    Retorna:
        dict: Un diccionario con la cantidad de proyectos por región.
    """
    query = """
                SELECT region, COUNT(*) as total_proyectos
                FROM projects
                WHERE is_deleted = false
                GROUP BY region
                ORDER BY total_proyectos DESC;
            """
    df = pd.read_sql(query, db.get_bind())
    return df.to_dict()


def generate_projects_registered_by_month_report(
    db: Session,
    year: int = None,
    country: str = None,
    climate_zone: str = None,
    building_type: str = None
):
    """
    Genera un reporte de la cantidad de proyectos registrados por mes con filtros opcionales.

    Args:
        db: Sesión de base de datos
        year: Año para filtrar los proyectos (opcional)
        country: País para filtrar los proyectos (opcional)
        climate_zone: Zona climática para filtrar los proyectos (opcional)
        building_type: Tipo de edificación para filtrar los proyectos (opcional)

    Returns:
        dict: Un diccionario con la cantidad de proyectos registrados por mes.
    """
    query = """
        SELECT 
            DATE_TRUNC('month', created_at) as month,
            COUNT(*) as total_projects
        FROM projects
        WHERE is_deleted = false
    """

    # Add filter conditions with numbered parameters
    conditions = []
    params = {}
    param_count = 1

    if year is not None:
        conditions.append(
            f"EXTRACT(YEAR FROM created_at) = %(param{param_count})s")
        params[f'param{param_count}'] = year
        param_count += 1

    if country is not None:
        conditions.append(f"country = %(param{param_count})s")
        params[f'param{param_count}'] = country
        param_count += 1

    # Add climate_zone filter using project_metadata->>'zone'
    if climate_zone is not None:
        # conditions.append(f"project_metadata->>'zone' = %(param{param_count})s")
        # params[f'param{param_count}'] = climate_zone
        param_count += 1

    if building_type is not None:
        conditions.append(f"building_type = %(param{param_count})s")
        params[f'param{param_count}'] = building_type

    # Add WHERE clause if there are any conditions
    if conditions:
        query += " AND " + " AND ".join(conditions)

    # Add GROUP BY and ORDER BY
    query += """
        GROUP BY month
        ORDER BY month DESC
    """

    df = pd.read_sql(query, db.get_bind(), params=params)
    # Ensure 'month' is a datetime before using .dt
    if not df.empty and not pd.api.types.is_datetime64_any_dtype(df['month']):
        df['month'] = pd.to_datetime(df['month'])
    if not df.empty:
        df['month'] = df['month'].dt.strftime('%Y-%m')
    return df.to_dict()


def generate_detailed_users_report(db: Session):
    """
    Genera un reporte detallado de usuarios incluyendo sus proyectos.

    Retorna:
        dict: Un diccionario con información detallada de cada usuario.
    """
    query = """
                        SELECT 
                            u.id,
                            u.name,
                            u.email,
                            u.lastname as last_name,
                            u.created_at,
                            u.proffesion,
                            u.active as status,
                            COUNT(p.id) as project_count,
                            array_agg(p.id) as project_ids
                        FROM users u
                        LEFT JOIN projects p ON u.id = p.user_id AND p.is_deleted = false
                        GROUP BY u.id, u.name, u.email, u.lastname, u.created_at, u.active, u.proffesion
                        ORDER BY project_count DESC
                    """
    df = pd.read_sql(query, db.get_bind())
    return df.to_dict('records')


def generate_energy_report(db: Session, year: int = None, country: str = None, zone: str = None, typology: str = None):
    """
    Devuelve un reporte de eficiencia energética con filtros opcionales de año y país,
    basado en los resultados de cálculo.
    """
    # Llama al servicio existente para obtener los datos agregados
    report_data = get_calculation_results_report(db=db, year=year, country=country, zone=zone, building_type=typology)

    if not report_data or report_data["total_resultados"] == 0:
        return []

    # Extraer los datos de demanda y consumo
    demanda_vs_consumo = report_data.get("demanda_vs_consumo", {})
    calefaccion = demanda_vs_consumo.get("calefaccion", {})
    refrigeracion = demanda_vs_consumo.get("refrigeracion", {})

    # Mapear los datos al formato deseado con nombres descriptivos
    formatted_report = {
        "year": year or "Todos los años",
        "country": country or "Todos los países",
        "zone": zone or "Todas las zonas",
        "typology": typology or "Todas las tipologías",
        "demanda_calefaccion": calefaccion.get("demanda", 0),
        "consumo_calefaccion": calefaccion.get("consumo", 0),
        "demanda_refrigeracion": refrigeracion.get("demanda", 0),
        "consumo_refrigeracion": refrigeracion.get("consumo", 0)
    }

    return [formatted_report]
