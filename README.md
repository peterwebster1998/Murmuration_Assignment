# Survey Data Discovery Platform

## Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Features](#features)
   - [Survey Management](#survey-management)
   - [Question Analysis](#question-analysis)
4. [Setup & Installation](#setup--installation)
5. [API Reference](#api-reference)
6. [Data Format](#data-format)
7. [Development Notes](#development-notes)

## Overview
This project was completed as a take-home assessment by Peter Webster while interviewing for the Research Engineer role at Murmuration.

This assessment required the development of a simple front-end UI that could communicate with a backend API to access information in a PostgreSQL database.

## System Architecture
The architecture for the project is as follows:
- Frontend:
    - React Native Web Application (JavaScript)
- Backend:
    - FastAPI & Pydantic Python Application
- Database:
    - PostgreSQL Server

## Features
### Survey Management
The FastAPI backend is capable of accepting new CSV files, interpreting the schema, and creating & populating corresponding tables in the database. (This functionality is only accessible through the FastAPI UI - http://localhost:8000/docs)

Tables can also have their data overwritten using the same method. A local copy of the source CSV file is saved locally on the container whenever one is uploaded.

### Question Analysis
Through the React Native Web UI, data discovery can be conducted. The schema of the provided CSV was (rudimentally) split into two different types of fields: Categories & Questions. Once a survey has been selected, selections for a category and a question may then be specified, producing a table of sorted response values per category. (Due to the nature of some of the longer-form answers, sorting isn't always useful)

A good example to explore in the provided data is to view the 'sentiment_label' by 'education_level' or 'income'. These explorations start to touch on what could be useful insights from a survey of this fashion.

There is space for many further enhancements within this UI, with aggregation methodologies, graphical display of bar charts and plots just scratching the surface.

## Setup & Installation
(*Fingers Crossed*) 
Setup and Installation should be very simple:
1. Ensure you have Docker installed
2. Run `docker-compose up --build`

If you are using Docker Desktop, you can access the UI by selecting the localhost port on the frontend-1 container (Port 3000). If not, http://localhost:3000 should also work in any web browser.

The UI only ties into one of the four backend API methods. For testing of the remaining methods, please use the auto-generated FastAPI UI (http://localhost:8000/docs).

## API Reference
● GET /surveys: All responses
This call retrieves all tables from within the database.

● GET /surveys/{survey_name}: Filtered by survey
This call retrieves all the results for the given named survey.

● GET /questions/{question_id}: Responses to a specific question
This call retrieves (id, response) pairs for a given field/question.

● POST /upload: Upload CSV files to refresh survey data
This call either creates a new table with the contents and name of the file provided, or updates the content within the table if the name already exists.

## Data Format
This application currently only accepts CSVs, although future extension of these capabilities would not be difficult.

## Development Notes
### Backend

While my initial instinct was to define Pydantic models (base.py) to encompass results of a specific schema and on a per-row basis, the requirement for the Question request API saw this reconfigured into more of a Parquet-style structuring to aid in the retrieval of this information.

The question API call also raised certain ambiguity, due to having to assume the survey from which the question was being requested. One approach would have been to alter the `GET/questions/question_id` into `GET/surveys/survey_id/question_id`, but this still would have required the input of the additional survey value within the call.

The other approach (that I outlined but didn't implement (context.py)) was to create a concept of context or storage of state. As APIs in best practice are stateless, this is less of a 'best-practices' solution, but one that for a proof of concept would have been useful in maintaining the context of the previously hit surveys to automatically request question/category data from.

To preserve this state within a scaled version of the application, users could have their context stored in a Redis Cache that could be quickly retrieved without disrupting the statelessness of the API.

I also boilerplated some simple API tests that could be further implemented with assertions based on response data structure and intentional failures to ensure the stability of the product if it were to be scaled.

For large datasets, using the fetchAll() on the PostgreSQL cursor would not be performant. Adding pagination and limiting returned results to those non-null or within a certain index range would help this application as it scaled.

### Frontend

The frontend implementation, as requested, is an MVPOC, to demostrate the capablity for the returned data to be explored through a UI, rather than being a full implementation of.

There are many areas for improvement here, including the incorporation of additional pages allowing for servicing of the rest of the API requests, more options for display and visualization. There may also be some value in a certain amount of precomputation to determine the type of data being retrieved, e.g., key point analysis in long-form answers, groupings based on zipcode, or other demographics. This type of natural language reasoning would be well implementable with an LLM prompt-engineered microservice. Other map-based visualizations could be incorporated to display geographic preferences within the data.

The ability to perform joins on content across tables would also be profoundly useful in a tool like this, but at a certain extent, it would be better to use industry tooling like PowerBI or Looker. Joining capabilities would also allow for some simple time-series analysis across a sequence of normalized surveys.

### Provisioning/Infrastructure
The application is split into three different containers: frontend, backend, & database. The implementation and provisioning of each of these containers is basic. The backend container does have a couple of startup scripts to ensure that the database is online before it tries to talk to it, and an additional set of actions to preload the provided CSV into the PostgreSQL database for immediate access from the API.

There is a defined Terraform script for the provisioning of this Docker environment on an EC2 instance. Being that it is a POC project, the instance type is of the 'micro' class as no more is required.

As this application scaled, I would choose to provision both the frontend and the database into a K8s cluster (EKS) and would preferentially abstract the backend API into a serverless microservice.

In terms of security, once the UI was of suitable utility, most users would not need even 'read' access to either the database or API layers as each of these responsibilities can be abstracted to a service account. Some users of the UI will need full 'write' access to be able to upload new surveys. The majority of users, however, would require just 'read' access.

As this project begins to scale, Git workflows for source control and CI/CD will need to be implemented to ensure the stability of the service for end users. Some core developers will also need to be identified as the primary maintainers of the project as PR approval is tightened to require reviews of those already familiar with the technology.

One final note on security: Currently, the SQL queries used are sensitive to SQL injections. To protect from this, parameterized values and queries should be incorporated.