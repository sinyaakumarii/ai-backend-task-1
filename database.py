import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# .env file se variables load karne ke liye
load_dotenv()

# Database URL structure: postgresql://username:password@host:port/database_name
DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

# Connection Engine create karna
engine = create_engine(DATABASE_URL)

# Local Session setup
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class jisse hamare saare database models inherit karenge
Base = declarative_base()

# FastAPI routes ke liye Database Session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()