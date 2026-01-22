import io
import csv
import json
from sqlalchemy.orm import Session 
from src.models.entity.project_table import Project
from src.models.entity.resultados_finales import ResultadosPorRecinto
from src.models.schemas.resultados.resultados_por_recinto import ResultadosPorRecintoSave
from src.models.entity.enclosure_general import EnclosureGenerals
from src.models.entity.enclosure import Enclosure
from typing import List, Optional


def save_results_by_enclosure(recintos: List[ResultadosPorRecintoSave], type: str, project_id: int, current_user: dict, db: Session):
    try:
        for recinto in recintos:
            enclosure_id = db.query(EnclosureGenerals.id).filter(
                EnclosureGenerals.project_id == project_id,
                EnclosureGenerals.name_enclosure == recinto.recinto,
                EnclosureGenerals.is_deleted == False
            ).scalar()
            
            if enclosure_id is None:
                raise Exception(f"Recinto '{recinto.recinto}' no encontrado en el proyecto {project_id}")
            
            perfil_id = db.query(Enclosure.id).filter(
                Enclosure.user_id == current_user["user_id"],
                Enclosure.name == recinto.perfil_uso,
                Enclosure.is_deleted == False
            ).scalar()

            if perfil_id is None:
                raise Exception(f"Perfil de uso '{recinto.perfil_uso}' no válido para el usuario actual")

            nuevo_registro = ResultadosPorRecinto(
                perfil_id=perfil_id,
                enclosure_id=enclosure_id,
                project_id=project_id,
                recinto=recinto.recinto,
                perfil_uso=recinto.perfil_uso,
                superficie=recinto.superficie,
                type=type,
                categorias=recinto.categorias
            )
            db.add(nuevo_registro)

        db.commit()
        return {"mensaje": f"{len(recintos)} recintos guardados correctamente"}
    
    except Exception as e:
        db.rollback()
        print(f"❌ Error al guardar resultados: {e}")
        raise Exception(str(e))



def get_results_by_enclosure(
    type: Optional[str],
    project_id: int,
    current_user: dict,
    db: Session
) -> List:
    # Verificar acceso al proyecto
    proyecto_q = db.query(Project).filter(Project.id == project_id)
    if current_user["role_id"] != 1:
        proyecto_q = proyecto_q.filter(Project.user_id == current_user["user_id"])
    if proyecto_q.first() is None:
        raise Exception(f"Proyecto '{project_id}' no encontrado o no accesible")

    # Armar query de resultados
    q = db.query(ResultadosPorRecinto).filter(
        ResultadosPorRecinto.project_id == project_id
    )
    if type:
        q = q.filter(ResultadosPorRecinto.type == type)
    return q.all()
    
    
    
def export_results_to_csv(
    type: Optional[str],
    project_id: int,
    current_user: dict,
    db: Session
) -> str:
    registros = get_results_by_enclosure(type, project_id, current_user, db)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['recinto', 'perfil_uso', 'superficie', 'categorias'])

    for r in registros:
        writer.writerow([
            r.recinto,
            r.perfil_uso,
            r.superficie,
            json.dumps(r.categorias, ensure_ascii=False)
        ])

    return output.getvalue()