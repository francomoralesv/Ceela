from collections import defaultdict
import io
import tempfile
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from src.utils.security.token.jwt_login import verify_token
from src.services.database.db_connection import get_db
from src.services.resultados import export_results_to_csv, save_results_by_enclosure, get_results_by_enclosure
from src.models.schemas.resultados.resultados_por_recinto import ResultadosPorRecintoSave 
from typing import List, Optional

router_resultados_finales = APIRouter()


@router_resultados_finales.post('/final-results/{project_id}/{type}', tags=['Final Results'])
def save_resultados_finales(recintos: List[ResultadosPorRecintoSave], type: str, project_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return save_results_by_enclosure(recintos, type, project_id, current_user, db)



@router_resultados_finales.get('/get-final-result/{project_id}/{type}', tags=['Final Results'])
def get_resultados_finales(type: str, project_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_results_by_enclosure(type, project_id, current_user, db)



@router_resultados_finales.get('/projects/{project_id}/results/download', tags=['Final Results'])
def download_results_csv(
    project_id: int,
    type: Optional[str] = Query(
        None,
        title="Type",
        description="Filtrar por type; si no se especifica, incluye todos"
    ),
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db),
):
    try:
        csv_data = export_results_to_csv(type, project_id, current_user, db)
        filename = f"{project_id}_results_project" + (f"_{type}" if type else "") + ".csv"

        return StreamingResponse(
            io.StringIO(csv_data),
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    
    
@router_resultados_finales.get("/projects/{project_id}/results/export-excel", tags=['Final Results'])
def export_results_excel(
    project_id: int,
    type: Optional[str] = Query(None, description="Filtrar por tipo (opcional)"),
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db),
):
    try:
        # 1. Obtener registros
        registros = get_results_by_enclosure(type, project_id, current_user, db)

        if not registros:
            raise HTTPException(status_code=404, detail="No se encontraron registros.")

        # 2. Separar por categoría
        tablas = defaultdict(list)

        for item in registros:
            tipo_principal = item.type or "default"
            base_info = {
                "Tipo": tipo_principal,  # ✅ Aquí lo agregas como cabecera visible
                "Recinto": item.recinto,
                "Perfil de uso": item.perfil_uso,
                "Superficie (m²)": item.superficie
            }
            categorias = item.categorias or []

            for cat in categorias:
                # Si cat tiene subcategorías anidadas
                if all(isinstance(val, dict) for val in cat.values()):
                    for subcategoria, valores in cat.items():
                        row = base_info.copy()
                        row["Categoría"] = subcategoria.capitalize()
                        for clave, valor in valores.items():
                            row[clave.capitalize()] = valor
                        tablas[tipo_principal].append(row)
                else:
                    # cat plano
                    row = base_info.copy()
                    row["Categoría"] = "General"
                    for clave, valor in cat.items():
                        row[clave.capitalize()] = valor
                    tablas[tipo_principal].append(row)
        # 3. Crear Excel en archivo temporal
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        with pd.ExcelWriter(temp.name, engine='xlsxwriter') as writer:
            for tipo, rows in tablas.items():
                df = pd.DataFrame(rows)
                df.to_excel(writer, sheet_name=tipo.capitalize(), index=False)

        # 4. Responder con archivo
        filename = f"resultados_project_{project_id}.xlsx"
        return FileResponse(
            temp.name,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))