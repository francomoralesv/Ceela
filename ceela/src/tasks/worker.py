
import os
import asyncio
from arq import Retry, create_pool
from arq.connections import RedisSettings
from src.models.entity.user_table import UserTable
from src.models.project_base import ProjectBase
from src.models.entity.project_table import Project
from src.models.entity.personal_access_token import PersonalAccessToken

from src.tasks.tasks import calculation_task
# Get Redis connection settings from environment
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", "6379"))
redis_password = os.getenv("REDIS_PASSWORD", None)
# Reduced timeout for faster failure detection
redis_timeout = int(os.getenv("REDIS_TIMEOUT", "5"))

class WorkerSettings:
    """ARQ Worker settings for background tasks"""
    functions = [calculation_task]
    redis_settings = RedisSettings(
        host=redis_host,
        port=redis_port,
        password=redis_password,

    )


async def get_redis_pool():
    import random
    max_retries = int(os.getenv("REDIS_MAX_RETRIES", 10))
    base_delay = int(os.getenv("REDIS_RETRY_DELAY", 5))
    for attempt in range(1, max_retries + 1):
        try:
            pool = await create_pool(WorkerSettings.redis_settings)
            print("[INFO] Redis pool created successfully.")
            return pool
        except Exception as e:
            if attempt < max_retries:
                delay = base_delay * attempt + random.uniform(0, 2)
                print(
                    f"[ERROR] Failed to create Redis pool (attempt {attempt}/{max_retries}): {e}. Retrying in {delay:.1f} seconds...")
                await asyncio.sleep(delay)
            else:
                print(
                    f"[ERROR] Failed to create Redis pool after {max_retries} attempts: {e}")
                raise
