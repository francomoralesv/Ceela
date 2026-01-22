import pickle
import hashlib
from src.utils.redis_utils import get_redis_sync

def simple_cache_call(func, ttl=60, *args, **kwargs):
    """
    Cachea el resultado de una función usando Redis, sin decorador.
    La clave se genera a partir del nombre de la función y los argumentos simples.
    No incluye objetos Session ni argumentos no serializables.
    """
    # Solo argumentos simples para la clave
    def filter_arg(arg):
        # Ignora SQLAlchemy Session y otros objetos complejos
        try:
            from sqlalchemy.orm import Session
            if isinstance(arg, Session):
                return None
        except ImportError:
            pass
        if hasattr(arg, '__dict__'):
            return str(arg.__dict__)
        return arg

    picklable_args = [filter_arg(a) for a in args if filter_arg(a) is not None]
    picklable_kwargs = {k: v for k, v in kwargs.items() if filter_arg(v) is not None}
    key_str = func.__module__ + "." + func.__name__ + str(picklable_args) + str(picklable_kwargs)
    key_hash = hashlib.md5(key_str.encode('utf-8')).hexdigest()
    cache_key = f"simplecache:{func.__name__}:{key_hash}"

    redis = get_redis_sync()
    cached = redis.get(cache_key)
    if cached:
        try:
            return pickle.loads(cached)
        except Exception as e:
            print(f"[simple_cache_call] Failed to unpickle: {e}")

    result = func(*args, **kwargs)
    try:
        redis.setex(cache_key, ttl, pickle.dumps(result))
    except Exception as e:
        print(f"[simple_cache_call] Failed to set cache: {e}")
    return result
