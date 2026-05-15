import json
import logging  # Add this import for logging
import os
import shutil  # Add this import for file existence check

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import FileResponse
from requests import Session
from starlette.responses import JSONResponse, StreamingResponse

from src.calc_engine.enclosure_processor import EnclosureProcessor
from src.calc_engine.input_data_calculator import InputDataCalculator
from src.controllers.calculator.datos import get_all_walls_with_layers
from src.services.calculation_result.calculation_result_service import upsert_calculation_result
from src.services.calculator.heating_config_service import HeatingConfigService
from src.services.calculator.results.result_calculator import ResultCalculator
from src.services.calculator.results.validation_utils import validate_project_requirements
from src.services.database.db_connection import get_db
from src.services.project.project_service import (get_project_by_id)
from src.utils.security.token.jwt_login import verify_token

from fastapi import File, UploadFile
from typing import List

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

calculator_router = APIRouter()


@calculator_router.get("/calculator/{project_id}", tags=["Calculator"])
async def calculator(
        request: Request,
        project_id: int,
        force_calculation: bool = False,
        db: Session = Depends(get_db),
        current_user: dict = Depends(verify_token),
):
    project = get_project_by_id(current_user, project_id, db)
    if project.project_metadata is None:
        raise HTTPException(
            status_code=400, detail="No se ha seleccionado una zona correctamente."
        )

    redis = request.app.state.redis_pool
    lock_key = f"calculation_lock:{project_id}"
    if await redis.exists(lock_key) and not force_calculation:
        await redis.delete(lock_key)
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe un cálculo en curso para el proyecto {project_id}. Espera a que termine antes de iniciar otro.",
        )
    validation_result = validate_project_requirements(project_id, db)
    is_valid = validation_result[0]
    enclosure_counts = validation_result[1]

    logger.info(
        f"Project Requirements id: {project_id} validation: {is_valid}, enclosure_counts: {enclosure_counts}")
    if not is_valid:
        await redis.delete(lock_key)
        # Buscar los recintos que no cumplen
        failed = [
            f"Recinto {eid}: {data['walls']} muros, {data['windows']} ventanas, {data['floors']} pisos"
            for eid, data in enclosure_counts.items()
            if data['walls'] < 3 or data['windows'] < 1 or data['floors'] < 1
        ]
        detail_msg = (
                "El proyecto no cumple con los requisitos mínimos por recinto. "
                "Cada recinto debe tener al menos 3 muros, 1 ventana y 1 piso. "
                "Recintos que no cumplen: " + "; ".join(failed)
        )
        raise HTTPException(
            status_code=400,
            detail=detail_msg
        )
    # Delete project uploads directory if force calculation is requested
    if force_calculation:
        project_uploads_dir = os.path.join(
            "public", "uploads", str(project_id))
        if os.path.exists(project_uploads_dir):
            try:
                shutil.rmtree(project_uploads_dir)
                logger.info(
                    f"Deleted project directory for force calculation: {project_uploads_dir}")
            except Exception as e:
                logger.error(f"Failed to delete project directory: {str(e)}")
    await redis.set(lock_key, "1", ex=300)

    await redis.enqueue_job(
        "calculation_task",
        project_id,
        user=current_user,
        force_calculation=force_calculation,
    )
    return {
        "enqueued": True,
        "message": f"Proceso de cálculo encolado para el proyecto {project_id}.",
    }


@calculator_router.get("/calculator/download/{project_id}", tags=["Calculator"])
async def download_files(project_id: int,
                         db: Session = Depends(get_db),
                         current_user: dict = Depends(verify_token)):
    import io
    from zipfile import ZipFile

    # Ruta de la carpeta específica del proyecto
    project_folder = os.path.join("public", "uploads", str(project_id))

    # Verificar si la carpeta existe
    if not os.path.exists(project_folder):
        raise HTTPException(
            status_code=404, detail=f"No se encontró la carpeta para el proyecto {project_id}.")

    # Crear un archivo ZIP en memoria
    zip_buffer = io.BytesIO()
    with ZipFile(zip_buffer, "w") as zip_file:
        # Recorrer todos los archivos en la carpeta del proyecto
        for root, _, files in os.walk(project_folder):
            for file in files:
                file_path = os.path.join(root, file)
                zip_file.write(file_path, arcname=os.path.relpath(
                    file_path, project_folder))

    # Preparar la respuesta con el archivo ZIP
    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={project_id}_files.zip"}
    )


@calculator_router.get("/calculator/download/{project_id}/{enclosure_id}", tags=["Calculator"])
async def download_enclosure_file(project_id: int,
                                  enclosure_id: int,
                                  db: Session = Depends(get_db),
                                  current_user: dict = Depends(verify_token)):
    # Verify access to the project before serving files
    get_project_by_id(current_user, project_id, db)

    file_path = os.path.join("public", "uploads", str(project_id), f"{enclosure_id}.data.xlsx")
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail=f"No se encontró el archivo del recinto {enclosure_id} para el proyecto {project_id}."
        )

    return FileResponse(
        file_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"proj_{project_id}_rec_{enclosure_id}.data.xlsx",
    )


@calculator_router.get("/calculator/walls/{project_id}", tags=["Calculator"])
async def get_walls(project_id: int,
                    db: Session = Depends(get_db),
                    current_user: dict = Depends(verify_token)):
    try:
        walls_data = get_all_walls_with_layers(db, project_id)
        return {"walls": walls_data}
    except Exception as e:
        logger.error(f"Error getting walls data: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Error retrieving walls data")


@calculator_router.get("/validate-requirements/{project_id}", tags=["Calculator"])
async def validate_project(
        project_id: int,
        check_climate_file: bool = False,
        force_data: bool = Query(False, description="Forzar recálculo de datos"),
        db: Session = Depends(get_db),
        current_user: dict = Depends(verify_token),
):
    """
    Valida los requisitos de un proyecto para verificar si está listo para cálculos.

    Args:
        project_id: ID del proyecto a validar
        check_climate_file: Si es True, también valida la existencia de archivos climáticos

    Returns:
        dict: Resultado de la validación con detalles
    """
    try:
        # Verificar si el usuario tiene acceso al proyecto
        project = get_project_by_id(current_user, project_id, db)
        if not project:
            raise HTTPException(status_code=404, detail="Proyecto no encontrado")

        # Ejecutar validación de requisitos
        validation_result = validate_project_requirements(project_id, db, check_climate_file)
        is_valid = validation_result[0]
        enclosure_counts = validation_result[1]
        additional_validations = validation_result[2] if len(validation_result) > 2 else {}

        # Construir respuesta detallada
        response = {
            "valid": is_valid,
            "enclosures": enclosure_counts,
            "additional_validations": additional_validations,
            "precalculated": False
        }

        # Agregar detalles de los enclosures que fallan
        if not is_valid:
            failed_enclosures = []
            for eid, data in enclosure_counts.items():
                if data['walls'] < 3 or data['windows'] < 1 or data['floors'] < 1:
                    failed_enclosures.append({
                        "enclosure_id": eid,
                        "walls": data['walls'],
                        "windows": data['windows'],
                        "floors": data['floors'],
                        "requirements": {
                            "walls": "Al menos 3 muros",
                            "windows": "Al menos 1 ventana",
                            "floors": "Al menos 1 piso"
                        }
                    })

            if failed_enclosures:
                response["failed_enclosures"] = failed_enclosures

        # Si es valido precalcular los resultados
        #
        # calculator = ResultCalculator(project_id)
        # calculator.prepare()
        # if not force_data:
        #     calculator.clear()
        # await calculator.execute_v2(
        #         db=db,
        #         force_data=False
        #     )
        # response["precalculated"] = True

        return JSONResponse(content=response)
    except Exception as e:
        logger.error(f"Error validando proyecto {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error validando proyecto: {str(e)}")

@calculator_router.get("/calculate_v2/{project_id}", tags=["Calculator"])
async def calculatev2(
    project_id: int,
    db: Session = Depends(get_db),
    force_data: bool = Query(False, description="Forzar recálculo de datos"),
):
    """
    Endpoint para iniciar el cálculo de un proyecto.
    Args:
        project_id: ID del proyecto a calcular
    Returns:
        dict: Resultado del cálculo
    """
    try:
        logger.info(f"force_data value: {force_data} (type: {type(force_data)})")
        calculator = ResultCalculator(project_id)
        calculator.prepare()
        if not force_data:
            calculator.clear()
        response = await calculator.execute_v2(
            db=db,
            force_data=force_data
        )
        return JSONResponse(content=response)
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"Error calculando proyecto {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error calculando proyecto: {str(e)}")


@calculator_router.get("/calculate_v3/{project_id}", tags=["Calculator"])
async def calculatev3(project_id: int,
                      db: Session = Depends(get_db),
                      current_user: dict = Depends(verify_token)):
    """
    Endpoint para iniciar el cálculo de un proyecto.
    """
    try:
        calculator = ResultCalculator(project_id)
        response = await calculator.execute_v3(db=db, current_user=current_user)

        # ⬇️ solo enclosures con is_base == False en result_by_enclosure
        if isinstance(response, dict) and "result_by_enclosure" in response:
            response["result_by_enclosure"] = [
                item for item in (response.get("result_by_enclosure") or [])
                if not item.get("is_base", False)
            ]

        return JSONResponse(content=response)

    except Exception as e:
        logger.error(f"Error calculando proyecto v3 {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error calculando proyecto: {str(e)}")


@calculator_router.get("/calculate_final_unificado/{project_id}", tags=["Calculator"])
async def calculate_final_unificado(
    project_id: int,
    db: Session = Depends(get_db),
    force_data: bool = Query(False, description="Forzar recálculo de datos"),
    current_user: dict = Depends(verify_token),
):
    """
    Endpoint unificado que ejecuta la lógica de v2 (procesamiento de recintos)
    y v3 (cálculo de indicadores) en un solo flujo, sin depender del cache de Redis.
    """
    try:
        logger.info(f"[UNIFICADO] force_data={force_data} (type: {type(force_data)})")

        # ── PASO 1: Preparar carpetas (lógica de v2) ──
        calculator = ResultCalculator(project_id)
        calculator.prepare()
        if not force_data:
            calculator.clear()

        # ── PASO 2: Procesar recintos – lógica de execute_v2 ──
        input_data = InputDataCalculator(project_id=project_id, db=db)
        enclosure_processor = EnclosureProcessor(data=input_data, db=db)
        await enclosure_processor.process_enclosures(force_data)
        enclosure_processor.post_process_enclosures()
        logger.info("[UNIFICADO] Procesamiento de recintos completado.")

        # ── PASO 3: Obtener datos directamente de memoria (sin cache) – lógica de execute_v3 ──
        superficie_dict = {}
        df_list = []
        df_list_base = []

        for enclosure in input_data.enclosures:
            # Área desde la memoria del processor (no Redis)
            area = enclosure_processor.area_results.get(enclosure.id)
            superficie_dict[enclosure.id] = area

            # DataFrame de demanda desde la memoria del processor (no Redis)
            df_r = enclosure_processor.demand_results.get(enclosure.id)
            if df_r is None:
                logger.warning(f"[UNIFICADO] Sin datos de demanda para recinto {enclosure.id}, se omite.")
                continue

            if isinstance(df_r, pd.DataFrame):
                df_r = df_r.copy()
                df_r['ID_Recinto'] = enclosure.id
            else:
                try:
                    df_r = pd.DataFrame(df_r)
                    df_r['ID_Recinto'] = enclosure.id
                except Exception:
                    logger.warning(f"[UNIFICADO] No se pudo convertir DF de recinto {enclosure.id}")
                    continue

            if enclosure.is_base:
                df_list_base.append(df_r)
            else:
                df_list.append(df_r)

        if not df_list:
            logger.warning("[UNIFICADO] No hay DF de recintos propuestos.")
            return JSONResponse(content={"final_indicators": {}, "result_by_enclosure": []})

        df_resultado_all = pd.concat(df_list, ignore_index=True)

        # ── PASO 4: Calcular resultados por recinto – lógica de execute_v3 ──
        coef_consumo = HeatingConfigService.get_consumo_heating_config_constant(project_id, db)
        SER = 2.95
        coef_combustible = HeatingConfigService.get_combustible_heating_config_constant(project_id, db)
        SCOP = 1.0

        result_by_enclosure_v2 = calculator.calculate_result_by_enclosure_v2(
            df_resultado_all, input_data.monthly_processed_data_df, superficie_dict,
            SCOP=SCOP, coef_consumo=coef_consumo, coef_combustible=coef_combustible,
            SER=SER, db=db
        )
        if isinstance(result_by_enclosure_v2, str):
            result_by_enclosure_v2 = json.loads(result_by_enclosure_v2)

        proposed_list = [r for r in result_by_enclosure_v2 if not r.get("is_base", False)]

        # Procesar recintos base si existen
        base_list = []
        if df_list_base:
            df_base_all = pd.concat(df_list_base, ignore_index=True)
            result_by_enclosure_base = calculator.calculate_result_by_enclosure_v2(
                df_base_all, input_data.monthly_processed_data_df, superficie_dict,
                SCOP=SCOP, coef_consumo=coef_consumo, coef_combustible=coef_combustible,
                SER=SER, db=db
            )
            if isinstance(result_by_enclosure_base, str):
                result_by_enclosure_base = json.loads(result_by_enclosure_base)
            base_list = [r for r in result_by_enclosure_base if r.get("is_base", False)]

        # ── PASO 5: Indicadores finales ──
        co2_eq_energia_primaria = calculator.get_co2_eq_energia_primaria(project_id, db=db)
        demanda_acs = calculator.get_demand_acs(project_id, db=db)

        final_indicators = calculator.calculate_final_indicators(
            proposed_list, base_list if base_list else None,
            co2_eq_energia_primaria, demanda_acs
        )

        all_enclosures = proposed_list + base_list
        result = {
            "final_indicators": final_indicators,
            "result_by_enclosure": all_enclosures,
            "base_by_enclosure": base_list,
            "co2_eq_energia_primaria": co2_eq_energia_primaria,
        }

        # ── PASO 6: Guardar en BD ──
        if current_user:
            try:
                co2_eq = {"total": co2_eq_energia_primaria}
                calculation_result = upsert_calculation_result(
                    project_id=project_id,
                    final_indicators=final_indicators,
                    result_by_enclosure=all_enclosures,
                    co2_eq=co2_eq,
                    current_user=current_user,
                    db=db,
                )
                logger.info(f"[UNIFICADO] Resultado guardado con ID {calculation_result.get('id')}")
            except Exception as e:
                import traceback
                traceback.print_exc()
                logger.error(f"[UNIFICADO] Error guardando resultado: {str(e)}")

        # Filtrar is_base para la respuesta (igual que v3)
        if isinstance(result, dict) and "result_by_enclosure" in result:
            result["result_by_enclosure"] = [
                item for item in (result.get("result_by_enclosure") or [])
                if not item.get("is_base", False)
            ]

        return JSONResponse(content=result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"[UNIFICADO] Error calculando proyecto {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error calculando proyecto: {str(e)}")


@calculator_router.post("/calculator/upload/{project_id}", tags=["Calculator"])
async def upload_files(
    project_id: int,
    files: List[UploadFile] = File(...),
    current_user: dict = Depends(verify_token)
):
    """
    Sube uno o más archivos a la carpeta uploads/<idproyecto>/
    """
    import os
    upload_dir = os.path.join("public", "uploads", str(project_id))
    os.makedirs(upload_dir, exist_ok=True)
    # Borrar todos los archivos existentes en la carpeta
    for existing_file in os.listdir(upload_dir):
        file_path = os.path.join(upload_dir, existing_file)
        if os.path.isfile(file_path):
            os.remove(file_path)
    saved_files = []
    for file in files:
        file_location = os.path.join(upload_dir, file.filename)
        with open(file_location, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        saved_files.append(file.filename)
    return {"message": "Archivos subidos correctamente", "files": saved_files}



__all__ = ["calculator_router"]
