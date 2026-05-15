from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.utils.security.token.jwt_login import verify_token
from src.services.database.db_connection import get_db
from src.services.reports.reports_service import (
    generate_projects_by_month_report,
    generate_projects_by_region_report,
    generate_projects_by_user_report,
    generate_projects_registered_by_month_report,
    generate_users_report,
    generate_projects_by_country_report,
    generate_projects_status_report,
    generate_building_levels_distribution_report,
    generate_total_surface_by_country_report,
    generate_building_type_distribution_report,
    generate_detailed_users_report,
    generate_energy_report,
)

router_reports_controller = APIRouter()


@router_reports_controller.get("/reports/users", tags=["Reports"], summary="Generar reporte de usuarios activos e inactivos")
def get_users_report_endpoint(current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    try:
        report = generate_users_report(db)
        return {"message": "Reporte de usuarios generado", "status": "success", "data": report}
    except Exception as e:
        return {"message": "Error al generar el reporte de usuarios", "status": "error", "data": str(e)}


@router_reports_controller.get("/reports/projects_by_country", tags=["Reports"], summary="Generar reporte de proyectos por país")
def get_projects_by_country_report_endpoint(current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    try:
        report = generate_projects_by_country_report(db)
        return {"message": "Reporte de proyectos por país generado", "status": "success", "data": report}
    except Exception as e:
        return {"message": "Error al generar el reporte de proyectos por país", "status": "error", "data": str(e)}


@router_reports_controller.get("/reports/projects_status", tags=["Reports"], summary="Generar reporte de estado de proyectos")
def get_projects_status_report_endpoint(current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    try:
        report = generate_projects_status_report(db)
        return {"message": "Reporte de estado de proyectos generado", "status": "success", "data": report}
    except Exception as e:
        return {"message": "Error al generar el reporte de estado de proyectos", "status": "error", "data": str(e)}


@router_reports_controller.get("/reports/building_levels_distribution", tags=["Reports"], summary="Generar reporte de distribución de niveles de edificios")
def get_building_levels_distribution_report_endpoint(current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    try:
        report = generate_building_levels_distribution_report(db)
        return {"message": "Reporte de distribución de niveles de edificios generado", "status": "success", "data": report}
    except Exception as e:
        return {"message": "Error al generar el reporte de distribución de niveles de edificios", "status": "error", "data": str(e)}


@router_reports_controller.get("/reports/total_surface_by_country", tags=["Reports"], summary="Generar reporte de superficie total construida por país")
def get_total_surface_by_country_report_endpoint(current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    try:
        report = generate_total_surface_by_country_report(db)
        return {"message": "Reporte de superficie total construida por país generado", "status": "success", "data": report}
    except Exception as e:
        return {"message": "Error al generar el reporte de superficie total construida por país", "status": "error", "data": str(e)}


@router_reports_controller.get("/reports/building_type_distribution", tags=["Reports"], summary="Generar reporte de distribución de tipos de edificios")
def get_building_type_distribution_report_endpoint(current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    try:
        report = generate_building_type_distribution_report(db)
        return {"message": "Reporte de distribución de tipos de edificios generado", "status": "success", "data": report}
    except Exception as e:
        return {"message": "Error al generar el reporte de distribución de tipos de edificios", "status": "error", "data": str(e)}


@router_reports_controller.get("/reports/projects_by_user", tags=["Reports"], summary="Generar reporte de proyectos por usuario")
def get_projects_by_user_report_endpoint(current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    try:
        report = generate_projects_by_user_report(db)
        return {"message": "Reporte de proyectos por usuario generado", "status": "success", "data": report}
    except Exception as e:
        return {"message": "Error al generar el reporte de proyectos por usuario", "status": "error", "data": str(e)}


@router_reports_controller.get("/reports/projects_by_month", tags=["Reports"], summary="Generar reporte de proyectos por mes")
def get_projects_by_month_report_endpoint(current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    try:
        report = generate_projects_by_month_report(db)
        return {"message": "Reporte de proyectos por mes generado", "status": "success", "data": report}
    except Exception as e:
        return {"message": "Error al generar el reporte de proyectos por mes", "status": "error", "data": str(e)}


@router_reports_controller.get("/reports/projects_by_region", tags=["Reports"], summary="Generar reporte de proyectos por región")
def get_projects_by_region_report_endpoint(current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    try:
        report = generate_projects_by_region_report(db)
        return {"message": "Reporte de proyectos por región generado", "status": "success", "data": report}
    except Exception as e:
        return {"message": "Error al generar el reporte de proyectos por región", "status": "error", "data": str(e)}


@router_reports_controller.get("/reports/projects_registered_by_month", tags=["Reports"], summary="Generar reporte de proyectos registrados por mes")
def get_projects_registered_by_month_report_endpoint(
    year: int = None,
    country: str = None,
    climate_zone: str = None,
    building_type: str = None,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Genera un reporte de proyectos registrados por mes con filtros opcionales.

    Parámetros:
    - year: Año para filtrar (opcional)
    - country: País para filtrar (opcional)
    - climate_zone: Zona climática para filtrar (opcional)
    - building_type: Tipo de edificación para filtrar (opcional)
    """
    try:
        report = generate_projects_registered_by_month_report(
            db=db,
            year=year,
            country=country,
            climate_zone=climate_zone,
            building_type=building_type
        )
        return {
            "message": "Reporte de proyectos registrados por mes generado",
            "status": "success",
            "data": report,
            "filters": {
                "year": year,
                "country": country,
                "climate_zone": climate_zone,
                "building_type": building_type
            }
        }
    except Exception as e:
        return {
            "message": "Error al generar el reporte de proyectos registrados por mes",
            "status": "error",
            "data": str(e)
        }


@router_reports_controller.get("/reports/users/detailed", tags=["Reports"], summary="Generar reporte detallado de usuarios con sus proyectos")
def get_detailed_users_report_endpoint(current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    try:
        report = generate_detailed_users_report(db)
        return {"message": "Reporte detallado de usuarios generado", "status": "success", "data": report}
    except Exception as e:
        return {"message": "Error al generar el reporte detallado de usuarios", "status": "error", "data": str(e)}


@router_reports_controller.get("/reports/energy", tags=["Reports"], summary="Reporte de eficiencia energética")
def get_energy_report_endpoint(
    year: int = Query(None, description="Año para filtrar"),
    country: str = Query(None, description="País para filtrar"),
    zone: str = Query(None, description="Zona para filtrar"),
    typology: str = Query(None, description="Tipología para filtrar"),
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Devuelve un reporte de eficiencia energética con filtros opcionales de año y país.
    """
    data = generate_energy_report(db=db, year=year, country=country, zone=zone, typology=typology)
    return {
        "message": "Reporte de eficiencia energética generado",
        "status": "success",
        "data": data,
        "filters": {"year": year, "country": country, "zone": zone, "typology": typology}
    }
