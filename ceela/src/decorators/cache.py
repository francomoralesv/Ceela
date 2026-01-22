import functools
import pickle
import hashlib
from sqlalchemy.orm import Session

from src.utils.redis_utils import get_redis, get_redis_sync


def generate_safe_key(func, args, kwargs):
    """Generate a cache key that can handle non-picklable objects like SQLAlchemy sessions."""
    # Create a list to hold picklable arguments
    picklable_args = []
    
    # Process positional arguments
    for arg in args:
        if isinstance(arg, Session):
            # Skip SQLAlchemy Session objects
            continue
        elif hasattr(arg, '__dict__'):
            # For complex objects, use their __dict__ or string representation
            try:
                picklable_args.append(str(arg.__dict__))
            except:
                picklable_args.append(str(arg))
        else:
            # For simple objects, include them directly
            picklable_args.append(arg)
    
    # Process keyword arguments, excluding non-picklable objects
    picklable_kwargs = {
        k: str(v) if isinstance(v, Session) or not isinstance(v, (str, int, float, bool, list, dict, tuple)) else v
        for k, v in kwargs.items()
    }
    
    # Create a unique key using the function name and picklable arguments
    key_parts = [func.__module__, func.__name__]
    
    # Add a hash of the arguments to make the key unique but short
    args_str = str(picklable_args) + str(picklable_kwargs)
    key_hash = hashlib.md5(args_str.encode('utf-8')).hexdigest()
    
    # Combine everything into a key
    cache_key = f"{'.'.join(key_parts)}:{key_hash}"
    
    # Debug logging
    print(f"[CACHE DEBUG] Function: {func.__name__}")
    print(f"[CACHE DEBUG] Picklable args: {picklable_args}")
    print(f"[CACHE DEBUG] Picklable kwargs: {picklable_kwargs}")
    print(f"[CACHE DEBUG] Args string: {args_str}")
    print(f"[CACHE DEBUG] Generated key: {cache_key}")
    
    return cache_key


def async_cache(ttl=60):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                redis = await get_redis()
                key = generate_safe_key(func, args, kwargs)
                
                try:
                    cached = await redis.get(key)
                    if cached:
                        try:
                            return pickle.loads(cached)
                        except Exception as e:
                            # If unpickling fails, log and ignore cache
                            print(f"Failed to unpickle cached value: {e}")
                except Exception as e:
                    # If Redis get fails, continue without caching
                    print(f"Redis get error: {e}")
            except Exception as e:
                print(f"Redis connection error: {e}")
                    
            # Execute the function if we got here (no cache or error)
            result = await func(*args, **kwargs)
            
            # Try to cache the result if Redis is available
            try:
                redis = await get_redis()
                if redis:
                    pickled_result = pickle.dumps(result)
                    await redis.setex(key, ttl, pickled_result)
            except Exception as e:
                # Log error but continue without caching
                print(f"Cache set error: {e}")
                
            return result
        return wrapper
    return decorator


def sync_cache(ttl=60):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                key = generate_safe_key(func, args, kwargs)
                try:
                    redis = get_redis_sync()
                    cached = redis.get(key)
                    if cached:
                        try:
                            return pickle.loads(cached)
                        except Exception as e:
                            # If unpickling fails, log and ignore cache
                            print(f"Failed to unpickle cached value: {e}")
                except Exception as e:
                    print(f"Redis error: {e}")
                    
                print(f"Cache miss for key: {key}, executing function.")
                result = func(*args, **kwargs)
                
                try:
                    redis = get_redis_sync()
                    pickled_result = pickle.dumps(result)
                    redis.setex(key, ttl, pickled_result)
                except Exception as e:
                    # Log error but continue without caching
                    print(f"Cache set error: {e}")
                
                return result
            except Exception as e:
                print(f"Cache wrapper error: {e}")
                return func(*args, **kwargs)
        return wrapper
    return decorator