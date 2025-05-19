import time
import json
import random
from config.redis_config import get_redis_connection

redis_conn = get_redis_connection()

while True:
    data = {
        "sensor_id": "sensor_01",
        "temperature": round(random.uniform(25, 35), 2),
        "humidity": round(random.uniform(50, 70), 2),
        "timestamp": time.time()
    }
    redis_conn.xadd("iot_stream", data)
    print("Sent:", data)
    time.sleep(2)
