import time
import datetime
import jwt
import bcrypt
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError

import models
from database import engine, get_db
from repository import TaskRepository  # Built for Storage Layering Architecture

# === DOCKER CONNECTION RETRY BLOCK ===
# Jab docker-compose start hota hai, toh database fully up hone me thoda waqt leta hai.
# Yeh loop crash se bachane ke liye 5 baar database connect karne ka try karega.
for _ in range(5):
    try:
        models.Base.metadata.create_all(bind=engine)
        print("Database connected successfully and tables validated! 🚀")
        break
    except OperationalError:
        print("Database ready nahi hai, 2 seconds me retry kar rahe hain...")
        time.sleep(2)

app = FastAPI(title="Flyrank Task Management API with Auth Integration")

# === CORS MIDDLEWARE CONFIGURATION ===
# Frontend applications (React/Vue/JS) ko backend se bina cross-origin error ke jodne ke liye
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "apna_super_secret_key_yahan_rakhein"
ALGORITHM = "HS256"

# === SECURE BCRYPT PASSWORD UTILITIES ===
def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


@app.get("/status")
def read_status():
    return {"status": "success", "database": "Connected via Docker Stack Control Layer! 🔐"}


# ==================== AUTH ROUTES ====================

@app.post("/auth/signup")
def signup(username: str, password: str, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username pehle se liya ja chuka hai!")
    
    new_user = models.User(username=username, hashed_password=get_password_hash(password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User successfully register ho gaya!", "user_id": new_user.id}


@app.post("/auth/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username ya password!")
    
    # Generate Token with 30 Minutes Lifespan
    expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    token_data = {"sub": user.username, "exp": expiration}
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    
    return {"access_token": token, "token_type": "bearer"}


# ==================== TASK CRUD ROUTES ====================
# Yeh saare endpoints internal calculations ke liye TaskRepository layer ko use karte hain.

@app.get("/tasks")
def get_all_tasks(db: Session = Depends(get_db)):
    repo = TaskRepository(db)
    return repo.get_all()


@app.post("/tasks/create")
def create_task(title: str, description: str = None, db: Session = Depends(get_db)):
    repo = TaskRepository(db)
    new_task = repo.create(title=title, description=description)
    return {"message": "Task created successfully!", "task": new_task}


@app.put("/tasks/{task_id}")
def update_task(task_id: int, title: str = None, is_completed: bool = None, db: Session = Depends(get_db)):
    repo = TaskRepository(db)
    task = repo.update(task_id, title, is_completed)
    if not task:
        raise HTTPException(status_code=404, detail="Task nahi mila!")
    return {"message": "Task update ho gaya!", "task": task}


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    repo = TaskRepository(db)
    if not repo.delete(task_id):
        raise HTTPException(status_code=404, detail="Task nahi mila!")
    return {"message": f"Task ID {task_id} successfully delete ho gaya!"}