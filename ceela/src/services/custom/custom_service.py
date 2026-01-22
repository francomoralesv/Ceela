import os
import shutil
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from src.models.entity.custom import Customization


UPLOAD_FOLDER = "src/static/logos"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def is_valid_image(filename: str):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def update_customization(primary_color: str, secondary_color: str, background_color: str, logo: UploadFile, current_user: dict, db: Session):
    if current_user["role_id"] == 2:
        raise HTTPException(status_code=403, detail="No tienes permiso para personalizar la pagina")
    
    if logo:
        if not is_valid_image(logo.filename):
            raise HTTPException(status_code=400, detail="Formato de imagen no permitido. Use PNG, JPG o GIF.")

    settings = db.query(Customization).first()
    if not settings:
        settings = Customization(
            primary_color=primary_color,
            secondary_color=secondary_color,
            background_color=background_color
        )
        db.add(settings)
    else:
        settings.primary_color = primary_color
        settings.secondary_color = secondary_color
        settings.background_color = background_color

    if logo and settings.logo_url:
        old_logo_path = os.path.join(UPLOAD_FOLDER, settings.logo_url.lstrip("/"))  
        if os.path.exists(old_logo_path):
            os.remove(old_logo_path)  

    if logo:
        file_path = os.path.join(UPLOAD_FOLDER, logo.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(logo.file, buffer)
        settings.logo_url = f"/{file_path}"

    try:
        db.commit()
        db.refresh(settings)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al actualizar la configuración") from e

    return {"message": "Configuración actualizada correctamente"}



def get_customization(current_user: dict, db: Session):
    settings = db.query(Customization).first()
    if not settings:
        return {"message": "No hay configuración disponible"}
    return settings