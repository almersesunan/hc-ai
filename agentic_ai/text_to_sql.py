from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool
from langchain import hub
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(override=True)
gemini_key = os.getenv("GEMINI_API_KEY")
SQL_HOST=os.getenv("SQL_HOST")
SQL_USER=os.getenv("SQL_USER")
SQL_PORT=os.getenv("SQL_PORT")
SQL_PASSWORD=os.getenv("SQL_PASSWORD")
SQL_DB_NAME=os.getenv("SQL_DB_NAME")
SQL_DIALECT=os.getenv("SQL_DIALECT")

# Initialize the Gemini model
try:
  llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",api_key=gemini_key,transport="rest")
except Exception as e:
  raise ValueError(f"❌ Failed to initialize Gemini LLM: {e}")

# Connect to the Postgresql database
connection_Uri = f"{SQL_DIALECT}://{SQL_USER}:{SQL_PASSWORD}@{SQL_HOST}:{SQL_PORT}/{SQL_DB_NAME}"
db = SQLDatabase.from_uri(connection_Uri)
    
# Pull the SQL query prompt from LangChain Hub
query_prompt_template = hub.pull("langchain-ai/sql-query-system-prompt")

def write_query(question: str):
    """Generate SQL query from the user's question."""
    prompt = query_prompt_template.invoke(
        {
            "dialect": db.dialect,
            "top_k": 10,
            "table_info": db.get_table_info(),
            "input": question,
        }
    )
    response = llm.invoke(prompt.to_string())

    extraction_prompt = """
    NEVER execute any DML statement. Return error when user is trying any DML statement. 
    Please extract the SQL query from the following text and return only the SQL query without any additional characters, wrapper or markdown/sql formatting.
    Remove any leading or trailing text, and ensure the query is syntactically correct.

    {response}

    SQL Query:
    """
    # Format the prompt with the actual response
    prompt = extraction_prompt.format(response=response)
    # Invoke the language model with the prompt
    parsed_query = llm.invoke(prompt)
    return parsed_query.content

def execute_query(query: str):
    """Execute the SQL query."""
    execute_query_tool = QuerySQLDatabaseTool(db=db)
    return execute_query_tool.invoke(query)

def generate_answer(question: str, query: str, result: str):
    """Generate an answer using the query results."""
    prompt = (
        "Given the following user question, corresponding SQL query, "
        "and SQL result, answer the user question.\n\n"
        f'Question: {question}\n'
        f'SQL Query: {query}\n'
        f'SQL Result: {result}'
    )
    response = llm.invoke(prompt)
    return response.content

