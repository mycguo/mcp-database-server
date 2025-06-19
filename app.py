import streamlit as st
from sqlalchemy import create_engine
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import create_sql_agent, SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
import os

# --- Configuration ---
st.set_page_config(page_title="MCP SQL Agent", layout="wide")

# --- UI ---
st.title("�� MCP-like SQL Agent")
st.markdown("Ask natural language questions about your **PostgreSQL**, **MSSQL**, or **SQLite** database.")

# --- Secrets or Environment ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", st.secrets.get("OPENAI_API_KEY", ""))
assert OPENAI_API_KEY, "Please set OPENAI_API_KEY in environment or Streamlit secrets."

# --- Database Connection ---
st.sidebar.header("🔌 Database Connection")

# Database type selector
db_type = st.sidebar.selectbox(
    "Database Type",
    ["SQLite", "PostgreSQL", "MSSQL"],
    help="Choose your database type"
)

# Database-specific connection parameters
if db_type == "SQLite":
    db_file = st.sidebar.text_input("Database File Path", value="data/todo_app.db")
    st.sidebar.info("💡 SQLite file will be created if it doesn't exist")
    
elif db_type == "PostgreSQL":
    server = st.sidebar.text_input("Server", value="localhost")
    port = st.sidebar.number_input("Port", value=5432, min_value=1, max_value=65535)
    database = st.sidebar.text_input("Database", value="your_db")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    st.sidebar.info("💡 Make sure PostgreSQL is running and accessible")
    
else:  # MSSQL
    server = st.sidebar.text_input("Server", value="localhost")
    database = st.sidebar.text_input("Database", value="your_db")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    st.sidebar.info("💡 Make sure MSSQL Server is running and ODBC Driver 17 is installed")

connect_button = st.sidebar.button("Connect to DB")

if "agent" not in st.session_state and connect_button:
    try:
        # Build connection string based on database type
        if db_type == "SQLite":
            connection_uri = f"sqlite:///{db_file}"
        elif db_type == "PostgreSQL":
            connection_uri = f"postgresql+psycopg2://{username}:{password}@{server}:{port}/{database}"
        else:  # MSSQL
            connection_uri = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"
        
        # Create database connection and agent
        db = SQLDatabase.from_uri(connection_uri)
        llm = ChatOpenAI(temperature=0, openai_api_key=OPENAI_API_KEY, model="gpt-4")
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)
        agent_executor = create_sql_agent(llm=llm, toolkit=toolkit, verbose=True)
        
        st.session_state.agent = agent_executor
        st.session_state.db_type = db_type
        st.success(f"✅ Connected to {db_type} database and agent ready!")
        
    except Exception as e:
        st.error(f"❌ Connection failed: {e}")
        if db_type == "SQLite":
            st.error("🔧 Troubleshooting: Check if the file path is correct and writable")
        elif db_type == "PostgreSQL":
            st.error("🔧 Troubleshooting: Check if PostgreSQL is running, credentials are correct, and psycopg2 is installed")
        else:
            st.error("🔧 Troubleshooting: Check if MSSQL Server is running, credentials are correct, and ODBC Driver 17 is installed")

# --- Ask a Question ---
if "agent" in st.session_state:
    current_db = st.session_state.get("db_type", "Unknown")
    st.info(f"🔗 Connected to: {current_db} database")
    
    query = st.text_area("Ask a question about your database", height=100)

    if st.button("Run Query"):
        with st.spinner("Thinking..."):
            try:
                result = st.session_state.agent.run(query)
                st.markdown(f"### 📄 Response\n{result}")
            except Exception as e:
                st.error(f"❌ Failed to process query: {e}")
                
    # Add disconnect button
    if st.sidebar.button("Disconnect"):
        if "agent" in st.session_state:
            del st.session_state.agent
        if "db_type" in st.session_state:
            del st.session_state.db_type
        st.rerun()
        
else:
    st.info("Please connect to a database first using the sidebar.")
    
    # Show example queries based on database type
    with st.expander("💡 Example Questions"):
        if db_type == "SQLite":
            st.markdown("""
            - What tables are in this database?
            - Show me the schema for the users table
            - How many todos does each user have?
            - What are the top 5 high priority tasks?
            - Show me all completed todos
            - Which user has the most pending tasks?
            """)
        elif db_type == "PostgreSQL":
            st.markdown("""
            - What tables are in this database?
            - Show me the schema for the users table
            - How many records are in the todos table?
            - What are the top 5 users by todo count?
            - Show me all columns in the categories table
            """)
        else:  # MSSQL
            st.markdown("""
            - What tables are in this database?
            - Show me the schema for the Users table
            - How many records are in the Todos table?
            - What are the top 5 users by todo count?
            - Show me all columns in the Categories table
            """)