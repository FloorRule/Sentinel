import os
import redis.asyncio as redis
import json

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

pool = redis.ConnectionPool.from_url(REDIS_URL, decode_responses=True)
client = redis.Redis(connection_pool=pool)

async def get_redis():
    return client

# Publishes a JSON message to a Redis channel
async def publish_event(channel: str, data: dict):
    await client.publish(channel, json.dumps(data))

# Caches a dict as a JSON string for some seconds 
async def cache_set(key: str, value: dict, expire: int = 5):
    await client.set(key, json.dumps(value), ex=expire)

# JSON string to dict
async def cache_get(key: str):    
    val = await client.get(key)
    if val:
        return json.loads(val)
    return None