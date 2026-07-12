from fastapi import FastAPI
import os
import psycopg2
from dotenv import load_dotenv

# .env file load karne ke liye
load_dotenv()

app = FastAPI()

def check_db_connection():
    try:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT")
        )
        connection.close()
        return "Connected Successfully! 🚀"
    except Exception as e:
        return f"Connection Failed: {str(e)} ❌"

@app.get("/status")
def read_status():
    db_status = check_db_connection()
    return {
        "status": "success", 
        "intern": "doing-great",
        "database_status": db_status
    }