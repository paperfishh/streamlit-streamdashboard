import time
import random
from config.redis_config import get_redis_connection

redis_conn = get_redis_connection()

while True:
    data = {
        "sensor_id": "sensor_01",
        "temperature": round(random.uniform(25, 35), 2),
        "humidity": round(random.uniform(50, 70), 2),
        "soil_moisture": round(random.uniform(30, 80), 2),
        "rainfall": round(random.uniform(0, 5), 2),
        "light_intensity": round(random.uniform(1000, 8000), 2),
        "co2": round(random.uniform(350, 800), 2),
        "timestamp": time.time()
    }
    redis_conn.xadd("iot_stream", data)
    print("Sent:", data)
    time.sleep(2)
