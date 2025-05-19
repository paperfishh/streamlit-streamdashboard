import redis

def get_redis_connection():
    return redis.Redis(host='172.17.125.76', port=6379, decode_responses=True)