import uuid
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy.orm import Session
from temporalio.client import WorkflowHandle

from src.services.database.db_connection import get_db, SessionLocal
from src.models.user import User
from src.models.temporal_calculation_status import TemporalCalculationStatus
from src.temporal.config import get_temporal_client, TASK_QUEUE
from src.temporal.workflows import EnergyCalculationWorkflow
from builtins import isinstance
logger = logging.getLogger(__name__)
import json
router = APIRouter()

class CalculationRequest(BaseModel):
    force_data: bool = False
    version: str = "v3"
    user_id: Optional[int] = None

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, calculation_id: str):
        await websocket.accept()
        self.active_connections[calculation_id] = websocket

    def disconnect(self, calculation_id: str):
        if calculation_id in self.active_connections:
            del self.active_connections[calculation_id]

    async def send_personal_message(self, message: dict, calculation_id: str):
        if calculation_id in self.active_connections:
            try:
                await self.active_connections[calculation_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending WebSocket message: {str(e)}")
                self.disconnect(calculation_id)

manager = ConnectionManager()

@router.post("/calculate/temporal/{project_id}")
async def start_temporal_calculation(
    project_id: int,
    request: CalculationRequest,
    db: Session = Depends(get_db)
):
    """Start a new energy calculation using Temporal workflow"""
    calculation_id = str(uuid.uuid4())
    workflow_id = f"energy-calculation-{calculation_id}"
    
    try:
        # Get Temporal client
        client = await get_temporal_client()
        
        # Start the workflow
        handle: WorkflowHandle = await client.start_workflow(
            EnergyCalculationWorkflow.run,
            args=[calculation_id, project_id, request.user_id, request.version, request.force_data],
            id=workflow_id,
            task_queue=TASK_QUEUE
        )
        
        # Save initial status to database
        calculation_status = TemporalCalculationStatus(
            calculation_id=calculation_id,
            workflow_id=workflow_id,
            run_id=handle.run_id or handle.id,  # Fallback to workflow id if run_id is None
            project_id=project_id,
            user_id=request.user_id,
            status="queued",
            progress=0,
            message="Calculation queued for processing"
        )
        
        db.add(calculation_status)
        db.commit()
        db.refresh(calculation_status)
        
        logger.info(f"Temporal workflow started successfully for calculation {calculation_id}")
        
        return {
            "calculation_id": calculation_id,
            "workflow_id": workflow_id,
            "run_id": handle.run_id,
            "status": "queued",
            "project_id": project_id,
            "version": request.version,
            "message": f"Temporal calculation started for project {project_id} using {request.version}",
            "websocket_url": f"/api/v1/ws/calculation/{calculation_id}",
            "status_url": f"/api/v1/calculate/status/{calculation_id}"
        }
        
    except Exception as e:
        logger.error(f"Error starting Temporal calculation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start calculation: {str(e)}")

@router.get("/calculate/status/{calculation_id}")
async def get_calculation_status(calculation_id: str, db: Session = Depends(get_db)):
    """Get the current status of a calculation"""
    try:
        # Get status from database first
        db_status = db.query(TemporalCalculationStatus).filter(
            TemporalCalculationStatus.calculation_id == calculation_id
        ).first()
        
        if not db_status:
            return {
                "calculation_id": calculation_id,
                "status": "not_found",
                "progress": 0,
                "message": "Calculation not found"
            }
        
        # Try to get live status from Temporal workflow
        try:
            import asyncio
            client = await get_temporal_client()
            handle = client.get_workflow_handle(db_status.workflow_id)
            
            # Query the workflow for current status with timeout
            live_status = await asyncio.wait_for(
                handle.query(EnergyCalculationWorkflow.get_status),
                timeout=5.0  # 5 second timeout
            )
            
            # Update database with live status if available
            if live_status and live_status.get("status"):
                db_status.status = live_status["status"]
                db_status.progress = live_status.get("progress", db_status.progress)
                db_status.message = live_status.get("message", db_status.message)
                if live_status.get("result_data"):
                    db_status.result_data = live_status["result_data"]
                if live_status.get("error_message"):
                    db_status.error_message = live_status["error_message"]
                db_status.updated_at = datetime.utcnow()
                db.commit()
                
        except asyncio.TimeoutError:
            logger.warning(f"Workflow status query timed out for workflow {db_status.workflow_id}")
        except Exception as e:
            logger.warning(f"Could not get live status from workflow: {e}")
        
        return {
            "calculation_id": db_status.calculation_id,
            "project_id": db_status.project_id,
            "status": db_status.status,
            "progress": db_status.progress,
            "message": db_status.message,
            "result_data": db_status.result_data,
            "error_message": db_status.error_message,
            "created_at": db_status.created_at.isoformat() if db_status.created_at else None,
            "updated_at": db_status.updated_at.isoformat() if db_status.updated_at else None,
            "workflow_id": db_status.workflow_id,
            "run_id": db_status.run_id
        }
        
    except Exception as e:
        logger.error(f"Error getting calculation status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

@router.websocket("/ws/calculation/{calculation_id}")
async def websocket_calculation(websocket: WebSocket, calculation_id: str):
    """WebSocket endpoint for real-time calculation updates"""
    await manager.connect(websocket, calculation_id)
    try:
        # Send initial status
        if calculation_id != "test":
            try:
                # Create a temporary database session for WebSocket
                db = SessionLocal()
                try:
                    status_response = await get_calculation_status(calculation_id, db)
                    await manager.send_personal_message(status_response, calculation_id)
                finally:
                    db.close()
            except Exception as e:
                logger.error(f"Error getting initial status: {e}")
        else:
            await websocket.send_text(json.dumps({
                "status": "connected",
                "message": "WebSocket test connection established"
            }))
        
        # Keep connection alive and handle pings with periodic status updates
        import asyncio
        last_status = None
        
        while True:
            try:
                # Use wait_for to timeout and check status periodically
                try:
                    data = await asyncio.wait_for(websocket.receive_text(), timeout=2.0)
                    if data == "ping":
                        await websocket.send_text("pong")
                    elif data == "status":
                        # Send current status immediately
                        db = SessionLocal()
                        try:
                            status_response = await get_calculation_status(calculation_id, db)
                            await manager.send_personal_message(status_response, calculation_id)
                            last_status = status_response.get("status")
                        finally:
                            db.close()
                except asyncio.TimeoutError:
                    # Timeout occurred, check for status updates
                    if calculation_id != "test":
                        db = SessionLocal()
                        try:
                            status_response = await get_calculation_status(calculation_id, db)
                            current_status = status_response.get("status")
                            
                            # Send update if status changed, progress changed, or if it's an active status
                            current_progress = status_response.get("progress", 0)
                            last_progress = getattr(websocket, '_last_progress', 0)
                            
                            if (current_status != last_status or 
                                current_progress != last_progress or
                                current_status in ["running", "processing", "queued"]):
                                await manager.send_personal_message(status_response, calculation_id)
                                last_status = current_status
                                websocket._last_progress = current_progress
                                
                            # Stop polling if calculation is finished
                            if current_status in ["completed", "failed", "error", "cancelled"]:
                                await manager.send_personal_message(status_response, calculation_id)
                                break
                                
                        except Exception as e:
                            logger.error(f"Error polling status: {e}")
                        finally:
                            db.close()
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error: {str(e)}")
                break
    finally:
        manager.disconnect(calculation_id)

@router.get("/calculate/projects/{project_id}/history")
async def get_project_calculation_history(
    project_id: int,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get calculation history for a project"""
    try:
        calculations = db.query(TemporalCalculationStatus).filter(
            TemporalCalculationStatus.project_id == project_id
        ).order_by(
            TemporalCalculationStatus.created_at.desc()
        ).limit(limit).all()
        
        result = []
        for calc in calculations:
            result.append({
                "calculation_id": calc.calculation_id,
                "workflow_id": calc.workflow_id,
                "project_id": calc.project_id,
                "status": calc.status,
                "progress": calc.progress,
                "message": calc.message,
                "created_at": calc.created_at.isoformat() if calc.created_at else None,
                "updated_at": calc.updated_at.isoformat() if calc.updated_at else None,
                "has_results": calc.result_data is not None
            })
        
        return {
            "project_id": project_id,
            "calculations": result,
            "total": len(result)
        }
        
    except Exception as e:
        logger.error(f"Error getting calculation history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")

@router.get("/calculate/results/{calculation_id}")
async def get_calculation_results(calculation_id: str, db: Session = Depends(get_db)):
    """Get the results of a completed calculation"""
    try:
        status_data = await get_calculation_status(calculation_id, db)
        
        if status_data["status"] != "completed":
            return {
                "calculation_id": calculation_id,
                "status": status_data["status"],
                "message": "Calculation not yet completed",
                "progress": status_data.get("progress", 0)
            }
        
        result_data = status_data.get("result_data")

        # If result_data is a string, parse it to JSON
        if isinstance(result_data, str):
            try:
                result_data = json.loads(result_data)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse result_data for {calculation_id}")
                raise HTTPException(status_code=500, detail="Error processing calculation results")

        # If result_data is null, try to get it from the workflow result (for legacy calculations)
        if not result_data:
            try:
                import asyncio
                client = await get_temporal_client()
                handle = client.get_workflow_handle(status_data["workflow_id"])
                
                # Get workflow result for completed workflows
                workflow_result = await asyncio.wait_for(
                    handle.result(),
                    timeout=10.0
                )
                
                if workflow_result and "result" in workflow_result:
                    result_data = workflow_result["result"]
                    logger.info(f"Retrieved results from workflow for calculation {calculation_id}")
                else:
                    raise HTTPException(status_code=404, detail="Results not found in workflow")
                    
            except asyncio.TimeoutError:
                raise HTTPException(status_code=404, detail="Results retrieval timed out")
            except Exception as e:
                logger.error(f"Error retrieving workflow results: {str(e)}")
                raise HTTPException(status_code=404, detail="Results not found")
        else:
            # Parse JSON if result_data is a string
            if isinstance(result_data, str):
                import json
                result_data = json.loads(result_data)
        
        # Ensure we have valid results before returning
        if not result_data:
            raise HTTPException(status_code=404, detail="No results found for this calculation")
            
        # Return the parsed results directly
        return {
            "calculation_id": calculation_id,
            "status": "completed",
            "results": result_data,
            "completed_at": status_data.get("updated_at") or datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting calculation results: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get results: {str(e)}")

@router.post("/calculate/cancel/{calculation_id}")
async def cancel_calculation(calculation_id: str, db: Session = Depends(get_db)):
    """Cancel a running calculation"""
    try:
        db_status = db.query(TemporalCalculationStatus).filter(
            TemporalCalculationStatus.calculation_id == calculation_id
        ).first()
        
        if not db_status:
            raise HTTPException(status_code=404, detail="Calculation not found")
        
        if db_status.status in ["completed", "error", "cancelled"]:
            return {
                "calculation_id": calculation_id,
                "status": db_status.status,
                "message": "Calculation already finished"
            }
        
        # Cancel the Temporal workflow
        client = await get_temporal_client()
        handle = client.get_workflow_handle(db_status.workflow_id)
        await handle.cancel()
        
        # Update status in database
        db_status.status = "cancelled"
        db_status.message = "Calculation cancelled by user"
        db_status.updated_at = datetime.utcnow()
        db.commit()
        
        return {
            "calculation_id": calculation_id,
            "status": "cancelled",
            "message": "Calculation cancelled successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling calculation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel calculation: {str(e)}")

async def send_websocket_update(calculation_id: str, data: Dict[str, Any]):
    """Send WebSocket update if connection exists"""
    await manager.send_personal_message(data, calculation_id)