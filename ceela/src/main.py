import asyncio
import datetime
import json
import logging
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import Dict, Optional

import redis
from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.responses import JSONResponse
from sqlalchemy import text
from src.controllers.agua_caliente.agua_caliente_controller import router_agua_caliente
from src.controllers.angle_azimut.angle_azimut import router_angle_azimut_controller
from src.controllers.auth.auth_controller import router_auth_controller
from src.controllers.auth.password_controller import router_password_controller
from src.controllers.calculator.calculator_controller import calculator_router
from src.controllers.calculator.heating_config_controller import heating_config_router
from src.controllers.calculation_result.calculation_result_controller import router_calculation_result_controller
from src.controllers.caso_base.caso_base import router_caso_base
from src.controllers.constants.constants_controller import router_constants_controller
from src.controllers.custom.custom_controller import router_customer_controller
from src.controllers.datos.datos import router_controller_datos
from src.controllers.datos.recintos import router_controller_recinto
from src.controllers.datos.suma_puentes import router_suma_puentes
from src.controllers.details.details_controller import router_controller_details
from src.controllers.details.details_part_controller import (
    router_detail_part_controller,
)
from src.controllers.elements.elements_controller import router_elements_controller
from src.controllers.elements_enclosures.elements_enclosures_controller import (
    router_elements_enclosures_controller,
)
from src.controllers.elements_enclosures.thermal_bridges_wall import (
    router_thermals_bridges_controller,
)
from src.controllers.enclosures.enclosures_controller import (
    router_enclosures_controller,
)
from src.controllers.enclosures_generals.enclosures_form_controller import (
    router_enclosure_generals_controller,
)
from src.controllers.energy_data.energy_data import router_controller_energy_data
from src.controllers.indicadores_finales.indicadores_finales import (
    router_indicadores_finales,
)
from src.controllers.obstruction.division_controller import router_division_controller
from src.controllers.obstruction.obstruction_tables_controller import (
    router_obstruction_controller,
)
from src.controllers.obstruction.orientation_controller import (
    router_orientation_controller,
)
from src.controllers.project.project_controller import router_project_controller
from src.controllers.regiones.regiones_controller import router_regiones_controller
from src.controllers.reports.reports_controller import router_reports_controller
from src.controllers.resultados.resultados import router_resultados_finales
from src.controllers.rnc.rnc_datos import router_rnc_datos
from src.controllers.rnc.rnc_horarios import router_rnc_horarios
from src.controllers.schedules.schedules_services import router_scheule_controllers
from src.controllers.sol.sol import router_sol_parameter
from src.controllers.user.user_controller import router_user_controller
from src.controllers.weather.weather_controller import route_weather_controller
from src.external.logging import Log
from src.seed.angulos_azimut import create_azimut_constants
from src.seed.building_conditions import import_building_conditions
from src.seed.calculation import calculate_all_doors, calculation_default_details
from src.seed.constant import (
    create_constants_acs_occupancy,
    create_constants_enclosure,
    create_constants_energy_and_systems,
    create_constants_human_activity,
    create_constants_month_water,
    create_constants_t_red,
    create_constants_type_details,
    create_constants_type_elements,
)
from src.seed.details import create_details_generals_default, calculate_details_part_seed
from src.seed.elements import create_elements_door, create_elements_windows
from src.seed.enclosures import create_enclosures_default
from src.seed.energy_data import seed_energy_data
from src.seed.levels import create_levels_seed
from src.seed.materials import create_materials_from_excel
from src.seed.regiones_comunas import regiones_from_excel
from src.seed.schedule import seed_default_daily_schedules
from src.seed.thermal_bridges import thermal_bridges_from_excel
from src.services.database.db_connection import create_tables, engine, get_db
from src.utils.redis_utils import check_redis_health, get_redis

import warnings
logging.basicConfig(
    filename=f"public/logging/{datetime.datetime.now().strftime('%Y-%m-%d')}.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

REDIS_SEED_KEY = "seed_executed"
SEED_EXPIRATION_SECONDS = int(timedelta(days=1).total_seconds())
warnings.simplefilter(action='ignore', category=FutureWarning)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    create_tables()

    db_gen = get_db()
    db = next(db_gen)

    redis = await get_redis()
    seed_executed = await redis.get(REDIS_SEED_KEY)

    if not seed_executed:
        print("Running seeding functions...")
        # Llamada secuencial a funciones de semilla con manejo de errores
        seed_functions = [
            # ("create_default_users", lambda: create_default_users(db)),
            ("create_materials_from_excel", lambda: create_materials_from_excel(
                "src/data/01. CEEUP v1.01.xlsm", db)),
            ("create_constants_type_details",
             lambda: create_constants_type_details(db)),
            ("create_constants_type_elements",
             lambda: create_constants_type_elements(db)),
            ("create_constants_enclosure", lambda: create_constants_enclosure(db)),
            ("create_elements_windows", lambda: create_elements_windows(
                "src/data/01. CEEUP v1.01.xlsm", db)),
            ("create_elements_door", lambda: create_elements_door(
                "src/data/01. CEEUP v1.01.xlsm", db)),
            ("calculate_all_doors", lambda: calculate_all_doors(db)),
            ("create_details_generals_default", lambda: create_details_generals_default(
                "src/data/01. CEEUP v1.01.xlsm", db)),
            
            ("create_enclosures_default", lambda: create_enclosures_default(
                "src/data/01. CEEUP v1.01.xlsm", db)),
            ("import_building_conditions", lambda: import_building_conditions(
                "src/data/01. CEEUP v1.01.xlsm", db)),
            ("regiones_from_excel", lambda: regiones_from_excel(
                "src/data/01. CEEUP v1.01.xlsm", db)),
            ("create_azimut_constants", lambda: create_azimut_constants(
                "src/data/01. CEEUP v1.01.xlsm", db)),
            ("seed_default_daily_schedules",
             lambda: seed_default_daily_schedules(db)),
            ("thermal_bridges_from_excel", lambda: thermal_bridges_from_excel(
                "src/data/01. CEEUP v1.01.xlsm", db)),
            ("seed_energy_data", lambda: seed_energy_data(db)),
            ("create_constants_acs_occupancy",
             lambda: create_constants_acs_occupancy(db)),
            ("create_constants_energy_and_systems",
             lambda: create_constants_energy_and_systems(db)),
            ("create_constants_t_red", lambda: create_constants_t_red(db)),
            ("create_constants_month_water",
             lambda: create_constants_month_water(db)),
            ("create_constants_human_activity",
             lambda: create_constants_human_activity(db)),
            ("create_levels_seed", lambda: create_levels_seed(db)),
        ]

        success_count = 0
        failure_count = 0

        for name, func in seed_functions:
            print(f"Running seed function: {name}")
            try:
                # Create a new session for each seed function to prevent carrying over issues
                session_gen = get_db()
                fresh_db = next(session_gen)
                func()  # Execute the seed function
                success_count += 1
                print(f"✅ Seed function completed: {name}")
            except Exception as e:
                failure_count += 1
                print(f"❌ Error in seed function {name}: {str(e)}")
                logger.error(f"Seed function {name} failed: {str(e)}")

        # Mark seeding as completed even if some functions failed
        await redis.setex(REDIS_SEED_KEY, SEED_EXPIRATION_SECONDS, "true")
        print(
            f"Seeding process finished. Success: {success_count}, Failed: {failure_count}")
    else:
        print("Seeding functions skipped (already executed today).")
    yield
    print("Shutting down...")


class NotificationRequest(BaseModel):
    message: str
    notification_type: str = "info"
    payload: Optional[Dict] = None


app = FastAPI(title="Proyecto Eficiencia Energetica Chile", lifespan=lifespan)


@app.post("/api/notify/{user_id}")
async def send_notification(
    user_id: str,
    request: NotificationRequest,
    redis_client: redis.Redis = Depends(get_redis)
):
    """
    Send a notification to a specific user
    - user_id: ID of the user to send notification to
    - request: Notification data containing message, type, and payload
    """
    # Format the notification as expected by the client
    notification = {
        "type": "notification",
        "message": request.message,
        "notificationType": request.notification_type,
        "payload": request.payload
    }

    notification_json = json.dumps(notification)

    await redis_client.publish(f"user:{user_id}", notification_json)
    return {"status": "sent"}


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    app.state.connections[user_id] = websocket

    print(f"Client connected: {user_id}")
    redis_client = await get_redis()
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(f"user:{user_id}")

    async def receive_from_redis():
        try:
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    # Forward Redis message to WebSocket
                    message_data = message['data']
                    if isinstance(message_data, bytes):
                        message_data = message_data.decode('utf-8')
                    await websocket.send_text(message_data)
        except Exception as e:
            print(f"Redis subscription error: {str(e)}")

    redis_task = asyncio.create_task(receive_from_redis())

    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        print(f"Client disconnected: {user_id}")
        if user_id in app.state.connections:
            del app.state.connections[user_id]
        redis_task.cancel()
        await pubsub.unsubscribe()
    except Exception as e:
        print(f"Error in websocket: {str(e)}")
        # Clean up on error
        if user_id in app.state.connections:
            del app.state.connections[user_id]
        redis_task.cancel()
        await pubsub.unsubscribe()


@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    logger.error(f"Error: {exc}", exc_info=True)
    await Log.save(f"Error: {exc}", level='error')
    return JSONResponse(
        status_code=500,
        content={"detail": "Ocurrió un error interno en el servidor."},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    logger.error(f"Validation Error: {exc.errors()}", exc_info=True)
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
app.include_router(router_auth_controller)
app.include_router(router_user_controller)
app.include_router(router_password_controller)
app.include_router(router_project_controller)
app.include_router(router_constants_controller)
app.include_router(router_customer_controller)
app.include_router(router_controller_details)
app.include_router(router_elements_controller)
app.include_router(router_enclosures_controller)
app.include_router(router_regiones_controller)
app.include_router(router_enclosure_generals_controller)
app.include_router(router_elements_enclosures_controller)
app.include_router(router_angle_azimut_controller)
app.include_router(router_thermals_bridges_controller)
app.include_router(router_reports_controller)
app.include_router(router_scheule_controllers)
app.include_router(router_division_controller)
app.include_router(router_orientation_controller)
app.include_router(router_obstruction_controller)
app.include_router(router_controller_energy_data)
app.include_router(route_weather_controller)
app.include_router(calculator_router)
app.include_router(heating_config_router)
app.include_router(router_controller_datos)
app.include_router(router_controller_recinto)
app.include_router(router_detail_part_controller)
app.include_router(router_rnc_datos)
app.include_router(router_rnc_horarios)
app.include_router(router_sol_parameter)
app.include_router(router_agua_caliente)
app.include_router(router_resultados_finales)
app.include_router(router_indicadores_finales)
app.include_router(router_suma_puentes)
app.include_router(router_caso_base)
app.include_router(router_calculation_result_controller)
# app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])


@app.get("/healthz")
async def healthz():
    """Simple health check endpoint for container orchestration"""
    return {"status": "ok"}


@app.get("/health/redis")
async def health_check_redis():
    """Health check endpoint for Redis connection"""
    is_healthy, message = await check_redis_health()
    if is_healthy:
        return {"status": "ok", "message": message}
    else:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "message": message}
        )


@app.get("/health")
async def health_check():
    """Overall health check endpoint"""
    results = {}

    # Check Redis health
    redis_healthy, redis_message = await check_redis_health()
    results["redis"] = {
        "status": "ok" if redis_healthy else "error", "message": redis_message}

    # Check database health
    db_healthy = True
    db_message = "Database connection is working"
    try:
        db_gen = get_db()
        db = next(db_gen)
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_healthy = False
        db_message = f"Database connection failed: {str(e)}"
    finally:
        if 'db' in locals():
            db.close()

    results["database"] = {
        "status": "ok" if db_healthy else "error", "message": db_message}

    # Overall status
    overall_status = "ok" if all(
        result["status"] == "ok" for result in results.values()) else "error"

    if overall_status == "ok":
        return {"status": overall_status, "components": results}
    else:
        return JSONResponse(
            status_code=503,
            content={"status": overall_status, "components": results}
        )

