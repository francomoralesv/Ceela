import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from temporalio import workflow
from temporalio.common import RetryPolicy

from src.temporal.activities import (
    initialize_input_data,
    process_enclosures,
    get_heating_coefficients,
    calculate_final_result,
    save_calculation_to_db,
    update_calculation_progress
)

logger = logging.getLogger(__name__)

@workflow.defn
class EnergyCalculationWorkflow:
    """Temporal workflow for energy efficiency calculations"""
    
    def __init__(self) -> None:
        self._calculation_status: Dict[str, Any] = {}
    
    @workflow.run
    async def run(
        self,
        calculation_id: str,
        project_id: int,
        user_id: Optional[int] = None,
        version: str = "v3",
        force_data: bool = False
    ) -> Dict[str, Any]:
        """Run the complete energy calculation workflow"""
        
        try:
            # Update status: Starting
            self._calculation_status = {
                "calculation_id": calculation_id,
                "status": "running",
                "progress": 10,
                "message": "Initializing project data...",
                "project_id": project_id,
                "user_id": user_id
            }
            
            # Update progress in database
            await workflow.execute_activity(
                update_calculation_progress,
                args=[calculation_id, "running", 10, "Initializing project data...", None],
                start_to_close_timeout=timedelta(seconds=30)
            )
            
            # Step 1: Initialize input data
            input_data = await workflow.execute_activity(
                initialize_input_data,
                args=[project_id],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    backoff_coefficient=2,
                    maximum_interval=timedelta(minutes=1),
                    maximum_attempts=3
                )
            )
            
            # Update status: Processing enclosures
            self._calculation_status.update({
                "progress": 25,
                "message": "Processing enclosures..."
            })
            
            await workflow.execute_activity(
                update_calculation_progress,
                args=[calculation_id, "running", 25, "Processing enclosures...", None],
                start_to_close_timeout=timedelta(seconds=30)
            )
            
            # Step 2: Process enclosures
            enclosure_results = await workflow.execute_activity(
                process_enclosures,
                args=[project_id, input_data],
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    backoff_coefficient=2,
                    maximum_interval=timedelta(minutes=1),
                    maximum_attempts=3
                )
            )
            
            # Update status: Calculating coefficients
            self._calculation_status.update({
                "progress": 50,
                "message": "Calculating demands and coefficients..."
            })
            
            await workflow.execute_activity(
                update_calculation_progress,
                args=[calculation_id, "running", 50, "Calculating demands and coefficients...", None],
                start_to_close_timeout=timedelta(seconds=30)
            )
            
            # Step 3: Get heating coefficients
            coefficients = await workflow.execute_activity(
                get_heating_coefficients,
                args=[project_id],
                start_to_close_timeout=timedelta(minutes=2),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    backoff_coefficient=2,
                    maximum_interval=timedelta(minutes=1),
                    maximum_attempts=3
                )
            )
            
            # Update status: Computing final indicators
            self._calculation_status.update({
                "progress": 75,
                "message": "Computing final indicators..."
            })
            
            await workflow.execute_activity(
                update_calculation_progress,
                args=[calculation_id, "running", 75, "Computing final indicators...", None],
                start_to_close_timeout=timedelta(seconds=30)
            )
            
            # Step 4: Calculate final result
            final_result = await workflow.execute_activity(
                calculate_final_result,
                args=[project_id, enclosure_results, coefficients, input_data, version],
                start_to_close_timeout=timedelta(minutes=15),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    backoff_coefficient=2,
                    maximum_interval=timedelta(minutes=1),
                    maximum_attempts=3
                )
            )
            
            # Step 5: Save to database if user_id provided
            if user_id:
                await workflow.execute_activity(
                    save_calculation_to_db,
                    args=[project_id, final_result, user_id],
                    start_to_close_timeout=timedelta(minutes=5),
                    retry_policy=RetryPolicy(
                        initial_interval=timedelta(seconds=1),
                        backoff_coefficient=2,
                        maximum_interval=timedelta(minutes=1),
                        maximum_attempts=3
                    )
                )
            
            # Update status: Completed
            self._calculation_status.update({
                "status": "completed",
                "progress": 100,
                "message": "Calculation completed successfully",
                "result": final_result
            })
            
            await workflow.execute_activity(
                update_calculation_progress,
                args=[calculation_id, "completed", 100, "Calculation completed successfully", final_result],
                start_to_close_timeout=timedelta(seconds=30)
            )
            
            return {
                "calculation_id": calculation_id,
                "project_id": project_id,
                "status": "completed",
                "result": final_result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in calculation workflow for calculation {calculation_id}: {str(e)}")
            logger.exception("Detailed error trace:")
            
            # Update status: Error
            self._calculation_status.update({
                "status": "error",
                "progress": 0,
                "message": f"Calculation failed: {str(e)[:200]}...",
                "error_message": str(e)
            })
            
            return {
                "calculation_id": calculation_id,
                "project_id": project_id,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    @workflow.query
    def get_status(self) -> Dict[str, Any]:
        """Query method to get current calculation status"""
        return self._calculation_status