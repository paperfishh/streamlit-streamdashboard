from sqlalchemy import text
from config.redis_config import get_redis_connection
from config.pg_config import get_pg_engine
import time

redis_conn = get_redis_connection()
engine = get_pg_engine()

last_id = '0-0'

insert_sql = text("""
INSERT INTO sensor_data (sensor_id, temperature, humidity, timestamp)
VALUES (:sensor_id, :temperature, :humidity, to_timestamp(:timestamp))
""")

while True:
    messages = redis_conn.xread({"iot_stream": last_id}, block=5000, count=10)
    for stream, entries in messages:
        for entry_id, data in entries:
            last_id = entry_id
            with engine.begin() as conn:
                conn.execute(
                    insert_sql,
                    {
                        'sensor_id': data['sensor_id'],
                        'temperature': float(data['temperature']),
                        'humidity': float(data['humidity']),
                        'timestamp': float(data['timestamp'])
                    }
                )
            print("Inserted:", data)
