from sqlalchemy import create_engine

def get_pg_engine():
    return create_engine("postgresql://postgres:admin@localhost:5433/iot_db")
