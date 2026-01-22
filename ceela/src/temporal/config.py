import os
from temporalio.client import Client
from temporalio.worker import Worker

# Temporal configuration
TEMPORAL_HOST = os.getenv("TEMPORAL_HOST", "localhost:7233")
TEMPORAL_NAMESPACE = os.getenv("TEMPORAL_NAMESPACE", "default")
TASK_QUEUE = "energy-calculation-queue"

async def get_temporal_client() -> Client:
    """Get Temporal client connection"""
    return await Client.connect(
        target_host=TEMPORAL_HOST,
        namespace=TEMPORAL_NAMESPACE
    )