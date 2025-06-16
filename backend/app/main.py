# ● GET /surveys: All responses
# ● GET /surveys/{survey_name}: Filtered by survey
# ● GET /questions/{question_id}: Responses to a specific question
# ● POST /upload: Upload CSV files to refresh survey data

import uvicorn
from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.models.base import Survey, QuestionOrField, Response, ResponseModel, DBContents
from app.db.database import init_db, get_db_conn
from app.db.table import create_table
from app.db.context import get_db_context, set_db_context

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


app = FastAPI()

# Add CORS middleware with more specific settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your React app's URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
    expose_headers=["*"]  # Exposes all headers
)

# Make sure to update to fetch all tables and results
@app.get("/surveys", response_model=ResponseModel[DBContents])
async def get_surveys():
    conn = get_db_conn()
    try:
        with conn.cursor() as cur:
            # Get list of all tables
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """)
            tables = [row['table_name'] for row in cur.fetchall()]
            logger.debug(f"tables fetched: {tables}")
            # Query each table
            surveys = []
            for table in tables:
                cur.execute(f"SELECT * FROM {table}")
                surveys.append(Survey.from_real_dict(table, cur.fetchall()))
            logger.debug(f"surveys processed: {[s.name for s in surveys]}")
            # if len(surveys) == 1:
            #     set_db_context(surveys[0].name)
    except Exception as e:
        logger.debug(f"error: {e}")
        return ResponseModel(status="error", data=str(e))   
    return ResponseModel(status="success", data=DBContents(surveys=surveys))

@app.get("/surveys/{survey_name}", response_model=ResponseModel[Survey])
async def get_survey(survey_name: str):
    # logger.debug(f"Setting context for survey: {survey_name}")
    # set_db_context(survey_name)
    # # Verify context was set
    # current_context = get_db_context()
    # logger.debug(f"Context after setting: {current_context}")
    
    conn = get_db_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM {survey_name}")
            survey = Survey.from_real_dict(survey_name, cur.fetchall())
    except Exception as e:
        logger.debug(f"error: {e}")
        return ResponseModel(status="error", data=str(e))   
    return ResponseModel(status="success", data=survey)

@app.get("/questions/{question_id}", response_model=ResponseModel[QuestionOrField])
async def get_question(
    question_id: str,
    # current_context: str = Depends(get_db_context)
    # Couldnt get the context to maintain state across requests, so hardcoded for now
    current_context: str = "us_ai_survey_unique_50"
):
    # logger.debug(f"Current context in get_question: {current_context}")
    
    if not current_context:
        return ResponseModel(
            status="error", 
            data="No survey context set. Please select a survey first."
        )
    
    conn = get_db_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT id, {question_id} FROM {current_context}")
            question = QuestionOrField.from_real_dict(question_id, cur.fetchall())
    except Exception as e:
        logger.debug(f"error: {e}")
        return ResponseModel(status="error", data=str(e))   
    return ResponseModel(status="success", data=question)

@app.post("/upload", response_model=ResponseModel[Survey])
async def upload_csv(file: UploadFile = File(...)):
    logger.debug(f"upload_csv called with file: {file.filename}")
    conn = get_db_conn()
    try:
        print("Writing to local dir")
        with open(f"./app/data/{file.filename}", "wb") as f:
            f.write(file.file.read())
        print("File written to local dir")
        local_file = UploadFile(
            filename=f"./app/data/{file.filename}",
            file=file.file,
            content_type=file.content_type
        )
        create_table(conn, local_file)
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM {file.filename.split('.')[0]}")
            survey = Survey.from_real_dict(file.filename.split('.')[0], cur.fetchall())
            # logger.debug(f"Table created and data inserted: {survey}")
    except Exception as e:
        logger.debug(f"Error: {e}")
        return ResponseModel(status="error", data=str(e))   
    return ResponseModel(status="success", data=survey)


if __name__ == "__main__":
    init_db("./app/data/us_ai_survey_unique_50.csv")
    db_context = get_surveys().surveys[0].survey_name
    uvicorn.run(app, host="0.0.0.0", port=8000)