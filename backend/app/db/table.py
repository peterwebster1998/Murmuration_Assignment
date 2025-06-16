from pydantic import BaseModel, create_model
from typing import Any
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType, BooleanType
from fastapi import UploadFile, File
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


spark = SparkSession.builder.appName("Infer CSV Schema").getOrCreate()

# This schema inference does not accurately preserve the leading zeros in the zip code column
# But I figured it was good enough for this exercise
def convert_file_to_df(file: UploadFile) -> DataFrame:
    logger.debug(f"Converting file to dataframe")
    try:
        return spark.read \
            .option("header", "true") \
            .option("inferSchema", "true") \
            .csv(f"{file.filename}")
    except Exception as e:
        logger.debug(f"Error: {e}")
        raise e

def create_schema(df: DataFrame) -> type[BaseModel]:
    logger.debug(f"Creating schema")
    field_types = {}
    
    # Map Spark types to Python types
    type_mapping = {
        'StringType()': str,
        'IntegerType()': int,
        'FloatType()': float,
        'BooleanType()': bool,
        'TimestampType()': str,
        'DateType()': str
    }
    
    for field in df.schema.fields:
        # Get the Spark type and map it to Python type
        spark_type = str(field.dataType)
        python_type = type_mapping.get(spark_type, str)
        field_types[field.name] = (python_type, None)  # None is the default value
    # logger.debug(f"Field types: {field_types}")
    # Create a dynamic model with the fields
    return create_model('Schema', **field_types)

def convert_schema_to_query(schema_model: Any, table_name: str) -> str:
    logger.debug(f"Converting schema to query")
    try:
        # Create table with dynamic columns
        columns = []
        # Change from model_fields to __fields__ for Pydantic v1
        for field_name, field in schema_model.__fields__.items():
            # logger.debug(f"Field name: {field_name}, Field type: {field.type_}")
            sql_type = {
                "<class 'str'>": 'TEXT',
                "<class 'int'>": 'INTEGER',
                "<class 'float'>": 'FLOAT',
                "<class 'bool'>": 'BOOLEAN',
                "<class 'datetime'>": 'TIMESTAMP',
                "<class 'date'>": 'DATE'
            }.get(str(field.type_), 'TEXT')
            if field_name != 'id':
                columns.append(f"{field_name} {sql_type}")
        
        query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id SERIAL PRIMARY KEY,
                {', '.join(columns)}
            )
        """
        return query
    except Exception as e:
        raise e
    
def insert_data_into_table(conn, table_name: str, df: DataFrame):
    logger.debug(f"Inserting data into table")
    try:
        # Convert Spark DataFrame to list of rows and insert data
        with conn.cursor() as cur:
            rows = df.collect()
            for row in rows:
                # logger.debug(f"Row: {row}")
                columns = ', '.join(row.asDict().keys())
                values = ', '.join(['%s'] * len(row))
                insert_query = f"""
                    INSERT INTO {table_name} ({columns})
                    VALUES ({values})
                    ON CONFLICT (id) DO UPDATE SET
                    {', '.join([f"{k} = EXCLUDED.{k}" for k in columns.split(', ')])}
                """
                cur.execute(insert_query, tuple(row))
    except Exception as e:
        logger.debug(f"Error: {e}")
        raise e

def create_table(conn, file: UploadFile):
    try:
        df = convert_file_to_df(file)
        table_name = file.filename.split('/')[-1].split('.')[0].replace(' ', '_')
        schema_model = create_schema(df)
        query = convert_schema_to_query(schema_model, table_name)
        with conn.cursor() as cur:
            cur.execute(query)
        insert_data_into_table(conn, table_name, df)
        conn.commit()
        # logger.debug("Committed transaction")
    except Exception as e:
        logger.debug(f"Error: {e}")
        raise e
