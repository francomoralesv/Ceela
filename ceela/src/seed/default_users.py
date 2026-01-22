from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.models.entity.user_table import UserTable
from src.utils.security.password.hash_password import hash_password
from datetime import date


def create_default_users(db: Session):
    admin_emails = ["danieljosuecr8@gmail.com", "drexsword@gmail.com", "maria.rzva@gmail.com"]
    
    existing_emails = {user.email for user in db.query(UserTable.email).all()}

    users_to_insert = []

    for email in admin_emails:
        if email not in existing_emails:
            users_to_insert.append({
                "name": "Administrador",
                "lastname": "Ejemplo",
                "email": email,
                "number_phone": "987654321",
                "birthdate": date(2025, 1, 22),
                "country": "Alemania",
                "ubigeo": "9809",
                "password": hash_password("asdasdasd"),
                "role_id": 1,
            })

    if "danieljosuecr4@gmail.com" not in existing_emails:
        users_to_insert.append({
            "name": "Daniel",
            "lastname": "Cruz",
            "email": "danieljosuecr4@gmail.com",
            "number_phone": "123456789",
            "birthdate": date(2025, 1, 22),
            "country": "Peru",
            "ubigeo": "1234",
            "password": hash_password("87654321"),
            "role_id": 2,
        })

    if users_to_insert:
        try:
            db.bulk_insert_mappings(UserTable, users_to_insert)
            db.commit()
            print(f"{len(users_to_insert)} usuario(s) creado(s) exitosamente.")
        except IntegrityError:
            db.rollback()
            print("Error al insertar los usuarios.")
    else:
        print("Todos los usuarios ya existen.")
    