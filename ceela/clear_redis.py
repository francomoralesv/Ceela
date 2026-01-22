import os
import redis
from dotenv import load_dotenv
load_dotenv()
print(os.getenv("REDIS_HOST"))
r = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    db=int(os.getenv("REDIS_DB")),
    password=os.getenv("REDIS_PASSWORD")
)

r.flushall()