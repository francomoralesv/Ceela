from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.services.sol.sol import calcular_parametros_solares_parquet
from src.services.sol.sol_recinto import calcular_parametros_solares_recinto_parquet
from src.services.sol.sol_obstruction import convert_parquet_obstruction_project
from src.services.sol.sol_elements import convert_parquet_window_project, convert_parquet_door_project
from src.services.sol.promedio import read_parquet_and_export_radiations
from src.services.database.db_connection import get_db
from src.utils.security.token.jwt_login import verify_token

router_sol_parameter = APIRouter()


@router_sol_parameter.get("/calculate-sol-parameters/{project_id}/", tags=["SOL"])
async def calculate_sol_parameters(
    file_path: str,
    project_id: int,
    db: Session = Depends(get_db)
):
    try:
        return calcular_parametros_solares_parquet(file_path, db, project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router_sol_parameter.get("/calculate-sol-parameters-recinto/{project_id}/", tags=["SOL"])
async def calculate_sol_parameters_recinto(
    project_id: int,
    db: Session = Depends(get_db)
):
    return calcular_parametros_solares_recinto_parquet(db, project_id)



@router_sol_parameter.get("/calculate-sol-parameters-obstruction/{project_id}/", tags=["SOL"])
async def calculate_sol_parameters_obstruction(
    project_id: int,
    db: Session = Depends(get_db)
):
    return convert_parquet_obstruction_project(db, project_id)



@router_sol_parameter.get("/calculate-sol-parameters-windows/{project_id}/", tags=["SOL"])
async def calculate_sol_parameters_elements(
    project_id: int,
    db: Session = Depends(get_db)
):
    return convert_parquet_window_project(db, project_id)




@router_sol_parameter.get("/calculate-sol-parameters-doors/{project_id}/", tags=["SOL"])
async def calculate_sol_parameters_doors(
    project_id: int,
    db: Session = Depends(get_db)
):
    return convert_parquet_door_project(db, project_id)



@router_sol_parameter.get("/calculate-sol-parameters-radiations/", tags=["SOL"])
async def calculate_sol_parameters_radiations(
    file_path: str,
):
    return read_parquet_and_export_radiations(file_path)

