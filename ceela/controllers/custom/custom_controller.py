from fastapi import APIRouter, Depends, Form, File, UploadFile
from sqlalchemy.orm import Session
from src.services.database.db_connection import get_db
from src.utils.security.token.jwt_login import verify_token
from src.services.custom.custom_service import update_customization, get_customization

router_customer_controller = APIRouter()

@router_customer_controller.put("/customizer", tags=["Customer"])
def update_customization_endpoint(primary_color: str = Form(), secondary_color: str = Form(), background_color: str = Form(), logo: UploadFile = File(None), current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return update_customization(primary_color, secondary_color, background_color, logo, current_user, db)


@router_customer_controller.get("/customization", tags=["Customer"])
def get_customization_endpoint(current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_customization(current_user, db)