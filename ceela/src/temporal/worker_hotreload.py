#!/usr/bin/env python3
"""
Temporal Worker with Hot Reload for Development
Monitors file changes and restarts the worker automatically
"""

import asyncio
import logging
import os
import sys
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.temporal.config import get_temporal_client, TASK_QUEUE
from src.temporal.workflows import EnergyCalculationWorkflow
from src.temporal.activities import (
    initialize_input_data,
    process_enclosures,
    get_heating_coefficients,
    calculate_final_result,
    save_calculation_to_db,
    update_calculation_progress
)
from temporalio.worker import Worker, UnsandboxedWorkflowRunner

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CodeChangeHandler(FileSystemEventHandler):
    """Handle file changes and restart worker"""
    
    def __init__(self, worker_task):
        self.worker_task = worker_task
        self.last_reload = 0
        self.reload_delay = 2  # seconds to wait before reload
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        # Only reload for Python files
        if not event.src_path.endswith('.py'):
            return
            
        # Skip cache and venv directories
        if '__pycache__' in event.src_path or '.venv' in event.src_path:
            return
            
        current_time = time.time()
        if current_time - self.last_reload < self.reload_delay:
            return
            
        self.last_reload = current_time
        logger.info(f"Detected change in {event.src_path}, restarting worker...")
        
        # Cancel current worker task
        if self.worker_task and not self.worker_task.done():
            self.worker_task.cancel()

async def run_worker():
    """Run a single Temporal worker instance"""
    try:
        # Connect to Temporal
        client = await get_temporal_client()
        logger.info("Connected to Temporal successfully")
        
        # Create and start worker
        worker = Worker(
            client,
            task_queue=TASK_QUEUE,
            workflows=[EnergyCalculationWorkflow],
            activities=[
                initialize_input_data,
                process_enclosures,
                get_heating_coefficients,
                calculate_final_result,
                save_calculation_to_db,
                update_calculation_progress
            ],
            workflow_runner=UnsandboxedWorkflowRunner(),
        )
        
        logger.info(f"Starting Temporal worker on task queue: {TASK_QUEUE}")
        logger.info("Worker is ready to process workflows and activities...")
        
        # Run worker
        await worker.run()
        
    except asyncio.CancelledError:
        logger.info("Worker cancelled, shutting down...")
    except Exception as e:
        logger.error(f"Error running worker: {e}")
        raise

async def main():
    """Main function with hot reload"""
    # Watch for file changes
    watch_path = Path(__file__).parent.parent.parent
    
    # Create event handler
    event_handler = CodeChangeHandler(None)
    
    # Create observer
    observer = Observer()
    observer.schedule(event_handler, str(watch_path), recursive=True)
    observer.start()
    
    logger.info(f"Starting Temporal worker with hot reload...")
    logger.info(f"Watching directory: {watch_path}")
    
    try:
        while True:
            try:
                # Create new worker task
                worker_task = asyncio.create_task(run_worker())
                event_handler.worker_task = worker_task
                
                # Wait for worker to complete or be cancelled
                await worker_task
                
            except asyncio.CancelledError:
                logger.info("Worker cancelled, restarting...")
                await asyncio.sleep(1)  # Brief pause before restart
                continue
                
    except KeyboardInterrupt:
        logger.info("Received interrupt, shutting down...")
    finally:
        observer.stop()
        observer.join()

if __name__ == "__main__":
    asyncio.run(main())
