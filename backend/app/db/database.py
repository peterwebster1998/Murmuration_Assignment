import os
import psycopg2
from pydantic import BaseSettings
from fastapi import UploadFile
from psycopg2.extras import RealDictCursor
from app.db.table import create_table

class Settings(BaseSettings):
    db_host: str = "localhost"
    db_port: int = "5432"
    db_user: str = "postgres"
    db_password: str = "postgres"
    db_name: str = "survey_db"

    class Config:
        env_file = ".env"

settings = Settings()

def get_db_conn():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'db'),
        database=os.getenv('DB_NAME', 'survey_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres'),
        port=os.getenv('DB_PORT', '5432'),
        cursor_factory=RealDictCursor
    )    

def init_db(filepath: str):
    conn = get_db_conn()
    abs_filepath = os.path.abspath(filepath)
    try:
        with open(abs_filepath, 'rb') as f:
            upload_file = UploadFile(
                filename=abs_filepath,
                file=f,
                content_type='csv'
            )
            create_table(conn, upload_file)
    except Exception as e:
        print(f"Error creating table: {e}")
    finally:
        conn.close()