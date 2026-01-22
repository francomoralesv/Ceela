from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import or_, func
from datetime import datetime, timezone
from sqlalchemy.orm import Session 
from src.models.entity.user_table import UserTable
from src.models.schemas.users.user_update import UserUpdate, UserUpdateAdminRole, UserUpdateAdminActive


from datetime import datetime, timezone


def list_users(value: str, limit: int, num_pag: int, db: Session, user: dict):
    """
    Lista todos los usuarios con filtros opcionales por nombre, apellido y correo electrónico, 
    ordenados por ID ascendente, excluyendo al usuario que realiza la solicitud.
    """
    if user["role_id"] == 2:
        raise HTTPException(
            status_code=400,
            detail="No tienes permisos suficientes para acceder a esta información"
        )

    filtered_query = db.query(UserTable).filter(
        UserTable.is_deleted == False,
        UserTable.id != user["user_id"]  
    )

    if value:
        filtered_query = filtered_query.filter(
            or_(
                UserTable.name.ilike(f"%{value}%"),
                UserTable.lastname.ilike(f"%{value}%"),
                UserTable.email.ilike(f"%{value}%"),
                func.concat(UserTable.name, ' ', UserTable.lastname).ilike(f"%{value}%"),
                UserTable.country.ilike(f"%{value}%")
            )
        )

    total_results = filtered_query.count()
    offset = (num_pag - 1) * limit

    paginated_users = (
        filtered_query.order_by(UserTable.id.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    users_list = [jsonable_encoder(u, exclude={"password", "is_deleted"}) for u in paginated_users]

    return {
        "total_results": total_results,
        "total_pages": (total_results // limit) + (1 if total_results % limit != 0 else 0),
        "current_page": num_pag,
        "per_page": limit,
        "users": users_list
    }


def list_user_by_id(db: Session, user_table: dict, id: int):
    """
    Obtiene usuario por id
    """
    if id and user_table["role_id"] == 2:
        raise HTTPException(
            status_code=400,
            detail="No tienes permisos necesarios para acceder a esta informacion"
        ) 
        
    if not id:
        id = user_table["role_id"]
     
            
    exist_user = db.query(UserTable).filter(
        UserTable.id == id,
        UserTable.is_deleted == False,
    ).first()
    
    if not exist_user:
        raise HTTPException(
            status_code=400,
            detail="Usuario no encontrado"
        )
    
    user = jsonable_encoder(exist_user, exclude={"password"})
    return user



def delete_user(id: int, db: Session, user: dict):
    """
    Borra usuario
    """
    if user["role_id"] == 2:
        raise HTTPException(
            status_code=403,
            detail="No tienes los permisos necesarios para eliminar usuarios"
        )
    
    exist_user = db.query(UserTable).filter(
        UserTable.id == id,
        UserTable.is_deleted == False
    ).first()
    
    if not exist_user:
        raise HTTPException(
            status_code=400,
            detail="Usuario no encontrado"
        )
        
    if exist_user.role_id == 1:
        raise HTTPException(
            status_code=403,
            detail="No puedes eliminar un usuario con rol admin"
        )
    
    exist_user.is_deleted = True
    exist_user.active = False
    
    try:
        db.add(exist_user)
        db.commit()
        db.refresh(exist_user)
        return {"message": f"Usuario con ID {id} eliminado correctamente."}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ocurrió un error al intentar eliminar el usuario: {str(e)}"
        )
        

def update_user_by_admin(id: int, user_update: UserUpdateAdminRole, db: Session, user: dict):
    """
    Actualiza Usuario
    """
    exist_user = db.query(UserTable).filter(
        UserTable.id == id,
        UserTable.is_deleted == False,
    ).first()
    
    if not exist_user:
        raise HTTPException(
            status_code=400,
            detail="Usuario no encontrado"
        )
    
    if user["user_id"] == id:
        raise HTTPException(
            status_code=403,
            detail="Un administrador no puede editar su propio perfil aquí."
        )
        
    if user["role_id"] == 2:
        raise HTTPException(
            status_code=403,
            detail="No tienes los permisos necesarios para actualizar usuarios"
        )
    
    # Usamos el objeto UserUpdateAdmin para modificar los atributos
    if user_update.role_id is not None:
        exist_user.role_id = user_update.role_id
    
    exist_user.updated_at = datetime.now(tz=timezone.utc)
    
    # Guardar los cambios en la base de datos
    try:
        db.commit()
        db.refresh(exist_user)
        return {"message": f"Usuario con ID {id} actualizado correctamente."}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ocurrió un error al intentar actualizar el usuario: {str(e)}"
        )
        
        
def update_user_status(id: int, user_update: UserUpdateAdminActive, db: Session, user: dict):
    """
    Actualiza el estado de un usuario (activo/inactivo)
    """
    exist_user = db.query(UserTable).filter(
        UserTable.id == id,
        UserTable.is_deleted == False
    ).first()

    if not exist_user:
        raise HTTPException(status_code=400, detail="Usuario no encontrado")

    if user["role_id"] == 2: 
        raise HTTPException(status_code=403, detail="No tienes permisos para actualizar el estado del usuario.")

    if exist_user.role_id == 1:
        raise HTTPException(status_code=403, detail="No puedes cambiar el estado de un administrador.")
        
    exist_user.active = user_update.active
    exist_user.updated_at = datetime.now(tz=timezone.utc)

    try:
        db.commit()
        db.refresh(exist_user)
        return {"message": f"Estado del usuario con ID {id} actualizado a {'activo' if user_update.active else 'inactivo'}."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar el estado del usuario: {str(e)}")
    


def update_user_by_user(user_update: UserUpdate, db: Session, user: dict):
    id = user["user_id"]
    
    exist_user = db.query(UserTable).filter(
        UserTable.id == id,
        UserTable.is_deleted == False,
        UserTable.active == True
    ).first()
    
    if user_update.name is not None:
        exist_user.name = user_update.name
    if user_update.lastname is not None:
        exist_user.lastname = user_update.lastname
    if user_update.number_phone is not None:
        exist_user.number_phone = user_update.number_phone
    if user_update.country is not None:
        exist_user.country = user_update.country
    if user_update.ubigeo is not None:
        exist_user.ubigeo = user_update.ubigeo
        
    exist_user.updated_at = datetime.now(tz=timezone.utc)
    
    try:
        db.commit()
        db.refresh(exist_user)
        return {"message": f"Usuario con ID {id} actualizado correctamente."}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ocurrió un error al intentar actualizar el usuario: {str(e)}"
        )


def delete_user_and_dependencies(id: int, db: Session):
    """
    Elimina un usuario y todas sus dependencias de forma forzada (sin autenticación).
    """
    exist_user = db.query(UserTable).filter(
        UserTable.id == id
    ).first()
    if not exist_user:
        raise HTTPException(status_code=400, detail="Usuario no encontrado")

    # Aquí puedes agregar la lógica para eliminar dependencias relacionadas.
    # Por ejemplo, si hay tablas relacionadas como perfiles, roles, etc., elimínalas aquí.
    # Ejemplo:
    # db.query(ProfileTable).filter(ProfileTable.user_id == id).delete()
    # db.query(OtherTable).filter(OtherTable.user_id == id).delete()

    exist_user.is_deleted = True
    exist_user.active = False
    try:
        db.add(exist_user)
        db.commit()
        db.refresh(exist_user)
        return {"message": f"Usuario con ID {id} y sus dependencias eliminados correctamente."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al intentar eliminar el usuario y sus dependencias: {str(e)}")

