import hashlib
import json
import os
from datetime import datetime
from typing import List
from uuid import UUID

import requests
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ...external.logging import Log
from ...models.entity.weather_data import WeatherMetadata
from ...services.database.db_connection import get_db
from src.services.calculator.weather.weather_service import get_weather_data_from_coord, get_weather_geocoding
from src.services.calculator.weather.weather_data_service import WeatherProcessor

route_weather_controller = APIRouter(tags=["Weather"])

UPLOAD_DIR = "public/uploads"
RADIACIONES_DIR = "public/radiaciones"


def calculate_file_hash(file_content: bytes) -> str:
    return hashlib.md5(file_content).hexdigest()


def get_next_version(filename: str, db: Session = None) -> int:
    """
    Get the next version number for a weather file
    If no previous versions exist, returns 1
    """
    base_name = os.path.splitext(filename)[0]
    # Query for files with the same base name
    existing_files = db.query(WeatherMetadata).filter(

        WeatherMetadata.name.ilike(f"{base_name}%")
    ).order_by(WeatherMetadata.version.desc()).first()

    return (existing_files.version + 1) if existing_files else 1


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


def safe_remove_file(file_path: str) -> bool:
    if not file_path:
        return False
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False
@route_weather_controller.post("/upload-by-coordinates", tags=["Weather"])
async def upload_file_by_coordinates(
        file: UploadFile = File(...),
        latitude: float = None,
        longitude: float = None,
        zone: str = "",
        db: Session = Depends(get_db)
):
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(400, "Solo se permiten archivos Excel")

    print(f"Latitude: {latitude}, Longitude: {longitude}")

    country, city, district = get_weather_geocoding(latitude, longitude)

    print(f"Weather metadata: {country} {city} {district}")
    file_content = await file.read()
    content_hash = calculate_file_hash(file_content)

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    current_date = datetime.now().strftime("%d_%m_%Y")
    file_ext = os.path.splitext(file.filename)[1]
    only_name = f"{country}_{city}_{district}_{current_date}"
    new_filename = f"{only_name}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, new_filename)

    # Buscar archivo existente con el mismo lugar, zona y año
    existing_file = db.query(WeatherMetadata).filter(
        WeatherMetadata.country == country,
        WeatherMetadata.city == city,
        WeatherMetadata.district == district,
        WeatherMetadata.zone == zone
    ).first()

    if existing_file:
        # Sobrescribir el archivo existente
        if os.path.exists(existing_file.location):
            os.remove(existing_file.location)
        if existing_file.complementary and os.path.exists(existing_file.complementary):
            os.remove(existing_file.complementary)

        file.file.seek(0)
        with open(file_path, "wb") as f:
            f.write(file_content)

        # Procesar el archivo y actualizar los metadatos existentes
        weather_processor = WeatherProcessor(file_path)
        weather_processor.run()
        print(f" Weather processor {weather_processor}")

        existing_file.location = weather_processor.output_processed_path
        existing_file.version += 1
        existing_file.created_at = datetime.now()
        existing_file.content_hash = content_hash
        existing_file.extension = file_ext
        existing_file.file_size = os.path.getsize(file_path)
        existing_file.complementary = weather_processor.monthly_output_path

        try:
            db.commit()
            db.refresh(existing_file)
        except Exception as e:
            print(e)
            db.rollback()
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                500, f"Error updating metadata in database: {str(e)}")

        return {"message": "File updated successfully", "metadata": existing_file}

    # Si no existe, crear un nuevo registro
    file.file.seek(0)
    with open(file_path, "wb") as f:
        f.write(file_content)

    weather_processor = WeatherProcessor(file_path)
    weather_processor.run()
    print(f" Weather processor {weather_processor}")
    metadata = WeatherMetadata(
        name=only_name,
        location=weather_processor.output_processed_path,
        version=1,
        created_at=datetime.now(),
        country=country,
        city=city,
        district=district,
        content_hash=content_hash,
        extension=file_ext,
        file_size=os.path.getsize(file_path),
        complementary=weather_processor.monthly_output_path,
        zone=zone,
    )

    try:
        db.add(metadata)
        db.commit()
        db.refresh(metadata)
    except Exception as e:
        print(e)
        db.rollback()
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            500, f"Error saving metadata to database: {str(e)}")

    return {"message": "File uploaded successfully", "metadata": metadata}

@route_weather_controller.get("/download/{file_id}", tags=["Weather"])
async def download_file(file_id: int, db: Session = Depends(get_db)):
    metadata = db.query(WeatherMetadata).filter(
        WeatherMetadata.id == file_id).first()
    if not metadata:
        raise HTTPException(404, "File not found")

    if not os.path.exists(metadata.location):
        raise HTTPException(404, "File not found")

    return FileResponse(
        metadata.location,
        filename=f"{os.path.splitext(metadata.name)[0]}_v{metadata.version}.parquet"
    )


@route_weather_controller.delete("/delete/{file_id}", tags=["Weather"])
async def delete_weather_file(file_id: int, db: Session = Depends(get_db)):
    metadata = db.query(WeatherMetadata).filter(
        WeatherMetadata.id == file_id).first()
    if not metadata:
        raise HTTPException(404, "File not found")

    derived_original_path = None
    derived_monthly_path = None
    radiaciones_path = None
    if metadata.location:
        base_filename = os.path.splitext(os.path.basename(metadata.location))[0]
        radiaciones_path = os.path.join(
            RADIACIONES_DIR, f"{base_filename}_promedios.parquet")
        if metadata.location.endswith(".processed.parquet"):
            base_path = metadata.location[: -len(".processed.parquet")]
            derived_original_path = f"{base_path}{metadata.extension or '.xlsx'}"
            derived_monthly_path = f"{base_path}_monthly.processed.parquet"

    upload_original_path = os.path.join(
        UPLOAD_DIR, f"{metadata.name}{metadata.extension}")

    original_deleted = safe_remove_file(upload_original_path)
    if not original_deleted:
        original_deleted = safe_remove_file(derived_original_path)

    monthly_deleted = safe_remove_file(metadata.complementary)
    if not monthly_deleted:
        monthly_deleted = safe_remove_file(derived_monthly_path)

    deleted = {
        "climate": safe_remove_file(metadata.location),
        "monthly": monthly_deleted,
        "original": original_deleted,
        "radiaciones": safe_remove_file(radiaciones_path),
    }

    try:
        db.delete(metadata)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            500, f"Error deleting metadata in database: {str(e)}")

    return {"message": "File deleted successfully", "deleted": deleted}


@route_weather_controller.get("/list", tags=["Weather"], response_model=List[WeatherMetadata])
async def list_weather_files(db: Session = Depends(get_db)):
    """
    Lista todos los archivos meteorológicos que se han subido al sistema
    """
    files = db.query(WeatherMetadata).order_by(
        WeatherMetadata.created_at.desc()).all()
    return files


@route_weather_controller.get("/search", tags=["Weather"], response_model=WeatherMetadata)
async def search_weather_metadata(
        country: str = None,
        city: str = None,
        district: str = None,
        db: Session = Depends(get_db)
):
    """
    Search weather metadata by location parameters.
    All parameters are optional - will return the most recent match if found.
    Performs case-insensitive matching.
    """
    query = db.query(WeatherMetadata)

    if country:
        query = query.filter(WeatherMetadata.country == country)
    if city:
        query = query.filter(WeatherMetadata.city == city)
    if district:
        query = query.filter(WeatherMetadata.district == district)

    result = query.order_by(WeatherMetadata.created_at.desc()).first()
    if not result:
        raise HTTPException(status_code=404, detail="No matching record found")

    return result


class WeatherMetadataResponse(BaseModel):
    name: str
    id: int
    version: int
    location: str
    country: str
    city: str
    extension: str
    zone: str
    created_at: datetime
    content_hash: str
    district: str
    file_size: int
    complementary: str = None


@route_weather_controller.get("/zones", tags=["Weather"], response_model=List[WeatherMetadataResponse])
async def get_thermal_zones(
        latitude: float,
        longitude: float,
        zone: str = None,
        db: Session = Depends(get_db)
):
    
    await Log.save(f"Get thermal zone for latitude: {latitude}, longitude: {longitude}", level='info')
    return get_weather_data_from_coord(db, latitude, longitude, zone)