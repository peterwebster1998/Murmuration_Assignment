#!/bin/bash
# Wait for database to be ready
sh wait-for-it.sh db

# Initialize the database with the CSV file
python -c "
from app.main import init_db
print('Loading data...')
init_db('./app/data/us_ai_survey_unique_50.csv')
print('Data loaded')
"

# Start the FastAPI server
uvicorn app.main:app --host backend --port 8000