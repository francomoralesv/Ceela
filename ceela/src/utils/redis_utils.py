import os

from dotenv import load_dotenv
from redis.asyncio import Redis as Redis
from redis import Redis as RedisSync

load_dotenv()
redis: Redis | None = None
redis_host = os.getenv("REDIS_HOST")
redis_port = os.getenv("REDIS_PORT")
redis_password = os.getenv("REDIS_PASSWORD")


async def get_redis() -> Redis:
    global redis
    print(
        f"[DEBUG] get_redis - redis_conn: {redis_host}:{redis_port} - redis_password: {redis_password}")
    if redis is None:
        if not redis_host:
            raise ValueError("REDIS_HOST environment variable is not set.")
        redis = Redis(
            host=redis_host,
            port=int(redis_port),
            password=redis_password if redis_password else None,
            decode_responses=False  
        )
        print(f"[DEBUG] get_redis - Created new redis instance: {redis}")
    
    print(f"[DEBUG] get_redis - Returning redis instance: {redis}")
    return redis


def get_redis_sync() -> RedisSync:
    global redis_sync
    if not hasattr(get_redis_sync, 'redis_sync'):
        if not redis_host:
            raise ValueError("REDIS_HOST environment variable is not set.")
        get_redis_sync.redis_sync = RedisSync(
            host=redis_host,
            password=redis_password if redis_password else None,
            port=int(redis_port),
            decode_responses=False 
        )
    return get_redis_sync.redis_sync


async def invalidate_cache_key(key):
    """Invalidate a specific cache key"""
    try:
        redis = await get_redis()
        await redis.delete(key)
        return True
    except Exception as e:
        print(f"Error invalidating cache key: {e}")
        return False


def invalidate_cache_key_sync(key):
    """Invalidate a specific cache key synchronously"""
    try:
        redis = get_redis_sync()
        redis.delete(key)
        return True
    except Exception as e:
        print(f"Error invalidating cache key: {e}")
        return False


async def clear_cache_pattern(pattern):
    """Clear all cache keys matching a pattern (e.g. 'module.*' to clear all keys in a module)"""
    try:
        redis = await get_redis()
        cursor = 0
        while True:
            cursor, keys = await redis.scan(cursor=cursor, match=pattern, count=100)
            if keys:
                await redis.delete(*keys)
            if cursor == 0:
                break
        return True
    except Exception as e:
        print(f"Error clearing cache pattern: {e}")
        return False


async def check_redis_health():
    """Check if Redis is accessible and working properly"""
    try:
        redis = await get_redis()
        # Set a test value
        test_key = "health_check"
        test_value = "ok"
        await redis.setex(test_key, 10, test_value)

        # Read it back
        value = await redis.get(test_key)

        # Verify value was stored correctly
        if value == b"ok":
            return True, "Redis is working correctly"
        else:
            return False, f"Redis test failed: value mismatch. Expected 'ok', got {value}"
    except Exception as e:
        return False, f"Redis health check failed: {str(e)}"

