from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.models.schemas.elements_enclosure.roof import RoofEnclosureCreate
from src.models.entity.roof import RoofEnclosure
from src.models.entity.detail_part import DetailPart
from src.models.entity.enclosure_general import EnclosureGenerals
from src.models.entity.project_table import Project
from src.services.tablas_py.tablas_py import calculate_tablas_py
from src.services.base.caso_base import create_caso_base
from src.services.base.create_base.base import create_obj_base, delete_obj_base, update_obj_base

def create_roof_enclosure(enclosure_id: int, roof: RoofEnclosureCreate, current_user: dict, db: Session):
    try:
        # Obtener el project_id a partir del enclosure_id
        project_id = db.query(EnclosureGenerals.project_id).filter(
            EnclosureGenerals.id == enclosure_id
        ).scalar()
        if not project_id:
            raise HTTPException(status_code=404, detail="No se encontró el proyecto asociado al enclosure_id.")

        user_id = current_user["user_id"]
        # Verificar que el proyecto pertenezca al usuario actual
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == user_id  
        ).first()
        if not project:
            raise HTTPException(status_code=403, detail="No se encontró el proyecto o no tienes permisos para modificarlo.")

        # Validar el detail del techo usando roof.roof_id
        roof_detail = db.query(DetailPart).filter(
            DetailPart.id == roof.roof_id,
            DetailPart.project_id == project_id
        ).first()
        if not roof_detail:
            raise HTTPException(status_code=404, detail="El roof_id no pertenece al proyecto.")
        if roof_detail.type != "Techo":
            raise HTTPException(status_code=400, detail="El roof_id debe corresponder a un registro de tipo 'Techo'.")

        # Obtener el value_u del detail
        u = getattr(roof_detail, "value_u", None)

        # Crear la instancia de RoofEnclosure con el value_u calculado
        new_roof = RoofEnclosure(
            **roof.model_dump(),
            u=u,
            enclosure_id=enclosure_id
        )

        try:
            db.add(new_roof)
            db.commit()
            db.refresh(new_roof)
            my_roof = new_roof.model_dump()
            calculate_tablas_py("techo", new_roof.id, enclosure_id, db)
            create_obj_base(enclosure_obj=new_roof, db=db)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=404, detail="Ocurrió un error al crear el techo en el recinto")
            
        return my_roof

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la creación del techo: {str(e)}")
    
    

def update_roof_enclosure(roof_id: int, roof_update: RoofEnclosureCreate, current_user: dict, db: Session):
    try:
        # Buscar el techo a actualizar
        roof = db.query(RoofEnclosure).filter(RoofEnclosure.id == roof_id).first()
        if not roof:
            raise HTTPException(status_code=404, detail="Techo no encontrado.")

        # Verificar permisos: obtener el project_id del enclosure asociado al techo
        project_id = db.query(EnclosureGenerals.project_id).filter(
            EnclosureGenerals.id == roof.enclosure_id
        ).scalar()
        if not project_id:
            raise HTTPException(status_code=404, detail="No se encontró el proyecto asociado al techo.")

        user_id = current_user["user_id"]
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == user_id
        ).first()
        if not project:
            raise HTTPException(status_code=403, detail="No tienes permisos para modificar este techo.")

        # Obtener los campos a actualizar
        roof_data = roof_update.model_dump(exclude_unset=True)

        # Si se actualiza el roof_id, recalcular el value_u
        if "roof_id" in roof_data:
            new_detail = db.query(DetailPart).filter(
                DetailPart.id == roof_data["roof_id"],
                DetailPart.project_id == project_id
            ).first()
            if not new_detail:
                raise HTTPException(status_code=404, detail="El roof_id no pertenece al proyecto.")
            if new_detail.type != "Techo":
                raise HTTPException(status_code=400, detail="El roof_id debe corresponder a un registro de tipo 'Techo'.")
            roof.u = getattr(new_detail, "value_u", None)
            roof.roof_id = roof_data["roof_id"]

        # Actualizar otros campos
        for key, value in roof_data.items():
            if key != "roof_id":
                setattr(roof, key, value)

        db.commit()
        db.refresh(roof)
        my_roof = roof.model_dump()
        calculate_tablas_py("techo", roof.id, roof.enclosure_id, db)
        update_obj_base(original_obj=roof, db=db)
        return my_roof

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar el techo: {str(e)}")


def delete_roof_enclosure(roof_id: int, current_user: dict, db: Session):
    try:
        # Buscar el techo a eliminar
        roof = db.query(RoofEnclosure).filter(RoofEnclosure.id == roof_id).first()
        if not roof:
            raise HTTPException(status_code=404, detail="Techo no encontrado.")

        # Verificar permisos: obtener el project_id asociado al enclosure del techo
        project_id = db.query(EnclosureGenerals.project_id).filter(
            EnclosureGenerals.id == roof.enclosure_id
        ).scalar()
        if not project_id:
            raise HTTPException(status_code=404, detail="No se encontró el proyecto asociado al techo.")

        user_id = current_user["user_id"]
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == user_id
        ).first()
        if not project:
            raise HTTPException(status_code=403, detail="No tienes permisos para eliminar este techo.")

        db.delete(roof)
        db.commit()
        delete_obj_base(original_obj=roof, db=db)
        return {"mensaje": "Techo eliminado exitosamente."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar el techo: {str(e)}")
    
    
def get_roof_enclosures(enclosure_id: int, current_user: dict, db: Session, skip_permission_check: bool = False):
    try:
        # Obtener el project_id asociado al enclosure_id
        project_id = db.query(EnclosureGenerals.project_id).filter(
            EnclosureGenerals.id == enclosure_id
        ).scalar()
        if not project_id:
            raise HTTPException(status_code=404, detail="No se encontró el proyecto asociado al enclosure_id.")

        # Verificar permisos: si el usuario no es admin, el proyecto debe pertenecer al usuario actual
        if not skip_permission_check and current_user.get("role_id") != 1:
            user_id = current_user["user_id"]
            project = db.query(Project).filter(
                Project.id == project_id,
                Project.user_id == user_id
            ).first()
            if not project:
                raise HTTPException(status_code=403, detail="No tienes permisos para acceder a este proyecto.")

        # Obtener todos los techos asociados al enclosure
        roofs = db.query(RoofEnclosure).filter(
            RoofEnclosure.enclosure_id == enclosure_id
        ).all()

        roofs_with_details = []
        for roof in roofs:
            # Se consulta en DetailPart usando roof.roof_id y se asegura que sea de tipo "Techo"
            detail = db.query(DetailPart).filter(
                DetailPart.id == roof.roof_id,
                DetailPart.type == "Techo"
            ).first()
            roof_name = detail.name_detail if detail else None

            roofs_with_details.append({
                **roof.model_dump(),
                "name": roof_name
            })

        return roofs_with_details

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener los techos: {str(e)}")
