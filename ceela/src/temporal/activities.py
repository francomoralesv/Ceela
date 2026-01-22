import logging
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional, List
from temporalio import activity
from fastapi import HTTPException

from src.calc_engine.input_data_calculator import InputDataCalculator
from src.services.calculation_result.calculation_result_service import upsert_calculation_result
from src.services.calculator.heating_config_service import HeatingConfigService
from src.services.database.db_connection import SessionLocal
from src.services.calculator.results.result_calculator import ResultCalculator

logger = logging.getLogger(__name__)

@activity.defn
async def initialize_input_data(project_id: int) -> Dict[str, Any]:
    """Initialize input data for calculation"""
    db = SessionLocal()
    try:
        input_data = InputDataCalculator(project_id=project_id, db=db)
        
        return {
            "enclosures": [
                {
                    "id": enclosure.id,
                    "name": getattr(enclosure, 'name_enclosure', getattr(enclosure, 'name', f'Enclosure {enclosure.id}')),
                    "area": getattr(enclosure, 'area', None),
                    "height": getattr(enclosure, 'height', None)
                } for enclosure in input_data.enclosures
            ],
            "monthly_processed_data": input_data.monthly_processed_data_df.to_dict('records') if hasattr(input_data, 'monthly_processed_data_df') else []
        }
    except Exception as e:
        logger.error(f"Error initializing input data: {str(e)}")
        raise e
    finally:
        db.close()

@activity.defn
async def process_enclosures(project_id: int, input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Process all enclosures for calculation.
    
    If demand data is not found in cache, it will be calculated on demand.
    """
    db = SessionLocal()
    try:
        from src.calc_engine.enclosure_processor import EnclosureProcessor
        from src.calc_engine.input_data_calculator import InputDataCalculator
        
        input_calculator = InputDataCalculator(project_id=project_id, db=db)
        calculator = ResultCalculator(project_id=project_id)
        
        # Check if we need to process enclosures first by testing the first one
        needs_processing = False
        if input_data["enclosures"]:
            first_enclosure_id = input_data["enclosures"][0]["id"]
            try:
                calculator.get_demand_cache(project_id, first_enclosure_id)
                logger.info(f"Cache exists for project {project_id}, using cached data")
            except HTTPException as e:
                if e.status_code == 404:
                    needs_processing = True
                    logger.info(f"No cache found for project {project_id}, need to process enclosures")
                else:
                    raise
        if needs_processing:
            logger.info(f"Processing all enclosures for project {project_id}...")
            enclosure_processor = EnclosureProcessor(data=input_calculator, db=db)
            await enclosure_processor.process_enclosures(force_data=False)
            enclosure_processor.post_process_enclosures()
            logger.info(f"Finished processing all enclosures for project {project_id}")
        
        results = []
        for enclosure in input_data["enclosures"]:
            enclosure_id = enclosure["id"]
            # Get area from the enclosure, with fallback to database lookup
            area = enclosure.get("area", None)
            if not area or area <= 0:
                # Try to get area from database
                try:
                    from src.services.datos.recintos import get_enclosure_by_id
                    db_enclosure = get_enclosure_by_id(enclosure_id, db=db)
                    area = db_enclosure.get("area", 100.0)
                    logger.info(f"Retrieved area {area} from database for enclosure {enclosure_id}")
                except Exception as e:
                    logger.warning(f"Could not get area from database for enclosure {enclosure_id}: {e}")
                    area = 100.0  # Default fallback
                    
            if area <= 0:
                area = 100.0  # Ensure we never have zero area
                logger.warning(f"Using default area {area} for enclosure {enclosure_id}")
                
            try:
                df_resultado = calculator.get_demand_cache(project_id, enclosure_id)
                logger.info(f"Retrieved demand data for enclosure {enclosure_id}")

            except HTTPException as e:
                logger.error(f"Failed to get demand data for enclosure {enclosure_id}: {str(e)}")
                enclosure_result = {
                    "enclosure_id": enclosure_id,
                    "name": enclosure.get("name", f"Enclosure {enclosure_id}"),
                    "area": area,
                    "demand_summary": {"total_rows": 0, "columns": [], "total_demand": 0},
                    "has_data": False,
                    "error": f"Cache miss: {str(e)}"
                }
                results.append(enclosure_result)
                continue
            
            # Process the results
            try:
                # Only sum numeric columns to avoid type errors
                numeric_df = df_resultado.select_dtypes(include=[np.number]) if isinstance(df_resultado, pd.DataFrame) else pd.DataFrame()
                total_demand = numeric_df.sum().sum() if not numeric_df.empty else 0
                
                demand_summary = {
                    "total_rows": len(df_resultado),
                    "columns": list(df_resultado.columns) if isinstance(df_resultado, pd.DataFrame) else [],
                    "total_demand": float(total_demand) if pd.notna(total_demand) else 0.0
                }
                
                enclosure_result = {
                    "enclosure_id": enclosure_id,
                    "name": enclosure.get("name", f"Enclosure {enclosure_id}"),
                    "area": area,
                    "demand_summary": demand_summary,
                    "has_data": True
                }
                
            except Exception as e:
                logger.error(f"Error processing results for enclosure {enclosure_id}: {str(e)}")
                enclosure_result = {
                    "enclosure_id": enclosure_id,
                    "name": enclosure.get("name", f"Enclosure {enclosure_id}"),
                    "area": area,
                    "demand_summary": {"total_rows": 0, "columns": [], "total_demand": 0},
                    "has_data": False,
                    "error": str(e)
                }
            
            results.append(enclosure_result)
        
        return results
        
    except Exception as e:
        logger.error(f"Error processing enclosures: {str(e)}")
        logger.exception("Detailed error:")
        raise e
    finally:
        db.close()

@activity.defn
async def get_heating_coefficients(project_id: int) -> Dict[str, float]:
    """Get heating coefficients for calculation"""
    db = SessionLocal()
    try:
        coef_consumo = HeatingConfigService.get_consumo_heating_config_constant(project_id, db)
        coef_combustible = HeatingConfigService.get_combustible_heating_config_constant(project_id, db)
        
        return {
            "coef_consumo": coef_consumo if coef_consumo is not None else 0.31,
            "coef_combustible": coef_combustible if coef_combustible is not None else 1.9,
            "SER": 2.95,
            "SCOP": 1.0
        }
    except Exception as e:
        logger.error(f"Error getting heating coefficients: {str(e)}")
        return {
            "coef_consumo": 0.31,
            "coef_combustible": 1.9,
            "SER": 2.95,
            "SCOP": 1.0
        }
    finally:
        db.close()

@activity.defn
async def calculate_final_result(
    project_id: int,
    enclosure_results: List[Dict[str, Any]],
    coefficients: Dict[str, float],
    input_data: Dict[str, Any],
    version: str = "v3"
) -> Dict[str, Any]:
    """Calculate final energy efficiency result"""
    db = SessionLocal()
    try:
        calculator = ResultCalculator(project_id=project_id)
        
        superficie_dict = {}
        all_demand_data = []
        
        for enclosure in enclosure_results:
            enclosure_id = enclosure["enclosure_id"]
            area = enclosure.get("area", 100.0)
            if not area or area <= 0:
                area = 100.0  # Ensure we never have zero area
                logger.warning(f"Using default area {area} for enclosure {enclosure_id}")
            superficie_dict[enclosure_id] = area
            
            # Get demand data from cache instead of from the enclosure results
            demand_df = pd.DataFrame()
            if enclosure["has_data"]:
                demand_df = calculator.get_demand_cache(project_id, enclosure_id)
                if demand_df is None:
                    demand_df = pd.DataFrame()
            
            if not demand_df.empty:
                all_demand_data.append(demand_df)
        
        if not all_demand_data:
            raise ValueError("No demand data found for any enclosure")
        
        df_resultado = pd.concat(all_demand_data, ignore_index=True)
        
        monthly_processed = pd.DataFrame(input_data["monthly_processed_data"]) if input_data["monthly_processed_data"] else pd.DataFrame()
        
        result_by_enclosure_v2 = calculator.calculate_result_by_enclosure_v2(
            df_resultado, 
            monthly_processed, 
            superficie_dict,
            SCOP=coefficients["SCOP"],
            coef_consumo=coefficients["coef_consumo"],
            coef_combustible=coefficients["coef_combustible"],
            SER=coefficients["SER"], 
            db=db
        )
        
        df_base = calculator.simulation_base_case(
            df_resultado, n_recintos=len(enclosure_results)
        )
        
        base_by_enclosure = calculator.calculate_surface_by_enclosure(
            df_base, superficie_dict, 'demanda_total', 
            is_base=False, project_id=project_id, db=db
        )
        
        co2_eq_energia_primaria = calculator.get_co2_eq_energia_primaria(
            project_id, db=db
        )
        
        final_indicators = calculator.calculate_final_indicators(
            result_by_enclosure_v2, base_by_enclosure, co2_eq_energia_primaria
        )
        
        if isinstance(result_by_enclosure_v2, str):
            import json
            result_by_enclosure_v2 = json.loads(result_by_enclosure_v2)
        
        result = {
            "final_indicators": final_indicators,
            "result_by_enclosure": result_by_enclosure_v2,
            "co2_eq_energia_primaria": co2_eq_energia_primaria,
            "calculation_metadata": {
                "version": version,
                "project_id": project_id,
                "enclosures_processed": len(enclosure_results),
                "coefficients_used": coefficients,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Error calculating final result: {str(e)}")
        raise e
    finally:
        db.close()

@activity.defn
async def save_calculation_to_db(project_id: int, result: Dict[str, Any], user_id: int) -> Dict[str, Any]:
    """Save calculation result to database"""
    db = SessionLocal()
    try:
        from src.models.entity.user_table import UserTable
        
        user = db.query(UserTable).filter(UserTable.id == user_id).first()
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        co2_eq = {"total": result["co2_eq_energia_primaria"]}
        
        calculation_result = upsert_calculation_result(
            project_id=project_id,
            final_indicators=result["final_indicators"],
            result_by_enclosure=result["result_by_enclosure"],
            co2_eq=co2_eq,
            current_user=user,
            db=db
        )
        
        return {
            "saved": True,
            "calculation_id": calculation_result.get("id"),
            "project_id": project_id
        }
        
    except Exception as e:
        logger.error(f"Error saving calculation to database: {str(e)}")
        raise e
    finally:
        db.close()

@activity.defn
async def update_calculation_progress(calculation_id: str, status: str, progress: int, message: str, result_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Update calculation progress in database"""
    db = SessionLocal()
    try:
        from src.models.temporal_calculation_status import TemporalCalculationStatus
        from datetime import datetime
        import json
        
        db_status = db.query(TemporalCalculationStatus).filter(
            TemporalCalculationStatus.calculation_id == calculation_id
        ).first()
        
        if db_status:
            db_status.status = status
            db_status.progress = progress
            db_status.message = message
            db_status.updated_at = datetime.utcnow()
            
            # Save results if provided and status is completed
            if result_data and status == "completed":
                db_status.result_data = json.dumps(result_data)
            
            db.commit()
            
            return {
                "updated": True,
                "calculation_id": calculation_id,
                "status": status,
                "progress": progress,
                "has_results": result_data is not None
            }
        else:
            return {
                "updated": False,
                "error": "Calculation not found"
            }
        
    except Exception as e:
        logger.error(f"Error updating calculation progress: {str(e)}")
        db.rollback()
        raise e
    finally:
        db.close()