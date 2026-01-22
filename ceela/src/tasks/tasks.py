import os
from typing import Dict, Any


from src.models.user import User
from src.services.calculator.results.result_calculator import ResultCalculator
from src.services.calculator.results.mock_result_helpers import ResultCalculator as MockResultCalculator
from src.services.database.db_connection import SessionLocal


async def calculation_task(
    ctx,  # ARQ job context
    project_id: int,
    user: Dict[str, Any],
    force_calculation: bool = False
):
    """
    Task that performs calculation for a project.
    Creates its own database session instead of receiving one through parameters.
    """
    print(f"[INFO] Iniciando procesamiento en segundo plano")    # Create a new database session for this task
    print(
        f"[DEBUG] calculation_task - project_id: {project_id} - user: {user}")

    # Ensure we have a proper database session
    db = SessionLocal()
    try:
        mock_helper = MockResultCalculator()
        response = 0
        return response
    except Exception as e:
        print(f"[ERROR] Error in calculation_task: {e}")
        import traceback
        print(traceback.format_exc())
        raise e
