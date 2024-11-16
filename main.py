from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.callbacks import BaseCallbackHandler
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import openai
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
openai.api_key = os.getenv("OPENAI_API_KEY")


class QueryRequest(BaseModel):
    question: str


class Step(BaseModel):
    step: str
    detail: str


class QueryResponse(BaseModel):
    steps: List[Step]
    final_answer: str
    llm_responses: List[str]
    sql_queries: List[str]


DATABASE_URL = "sqlite:///mining_machines.db"
engine = create_engine(DATABASE_URL)
llm = ChatOpenAI(temperature=0, model='gpt-4')


class CustomCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.llm_responses = []
        self.sql_queries = []

    def on_llm_end(self, response, **kwargs):
        self.llm_responses.append(response['text'])

    def on_tool_end(self, output: str, **kwargs):
        self.sql_queries.append(output)


@app.post("/query", response_model=QueryResponse)
async def query_database(request: QueryRequest):
    steps = []
    callback_handler = CustomCallbackHandler()

    steps.append(Step(step="Connecting to Database",
                      detail="Establishing connection to the database to retrieve schema."))
    try:
        db = SQLDatabase(engine)
        schema = db.get_table_info()
        steps.append(Step(step="Retrieved Schema",
                          detail="Successfully retrieved the database schema."))
    except Exception as e:
        steps.append(Step(step="Error Retrieving Schema", detail=str(e)))
        raise HTTPException(
            status_code=500, detail="Database connection error.")

    try:
        agent = create_sql_agent(
            llm=llm,
            db=db,
            agent_type="openai-tools",
            callbacks=[callback_handler]
        )
    except Exception as e:
        steps.append(Step(step="Error Initializing Agent", detail=str(e)))
        raise HTTPException(
            status_code=500, detail="Agent initialization error.")

    steps.append(Step(step="Generating SQL Query",
                      detail=f"Generating SQL query for the question: '{request.question}'"))
    try:
        agent_response = agent.invoke({"input": request.question})
        steps.append(Step(step="SQL Query Generated",
                          detail="SQL query generated successfully."))
    except Exception as e:
        steps.append(Step(step="Error Generating SQL Query", detail=str(e)))
        raise HTTPException(
            status_code=500, detail="Error generating SQL query.")

    steps.append(Step(step="Executing SQL Query",
                      detail="Running the SQL query against the database."))
    try:
        final_answer = agent_response['output']
        steps.append(Step(step="SQL Query Executed",
                          detail="SQL query executed successfully."))
    except Exception as e:
        steps.append(Step(step="Error Executing SQL Query", detail=str(e)))
        raise HTTPException(
            status_code=500, detail="Error executing SQL query.")

    steps.append(Step(step="Generating Final Answer",
                      detail="Formatting the response to the user."))
    try:
        steps.append(Step(step="Final Answer Generated",
                          detail="Final answer generated successfully."))
    except Exception as e:
        steps.append(Step(step="Error Generating Final Answer", detail=str(e)))
        raise HTTPException(
            status_code=500, detail="Error generating final answer.")

    llm_responses = callback_handler.llm_responses
    sql_queries = callback_handler.sql_queries

    return QueryResponse(
        steps=steps,
        final_answer=final_answer,
        llm_responses=llm_responses,
        sql_queries=sql_queries
    )
