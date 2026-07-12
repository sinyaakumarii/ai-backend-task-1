from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models
from database import engine, get_db
import bcrypt
import jwt
import datetime

# Database tables automatically create karne ke liye
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

SECRET_KEY = "apna_super_secret_key_yahan_rakhein"
ALGORITHM = "HS256"

# Pure Python Bcrypt Functions (No passlib error!)
def get_password_hash(password: str) -> str:
    # Password ko bytes me badal kar salt ke saath hash karna
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


@app.get("/status")
def read_status():
    return {"status": "success", "database": "Connected & Authentication Ready! 🔐"}

# === AUTH ROUTES ===
@app.post("/auth/signup")
def signup(username: str, password: str, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username pehle se liya ja chuka hai!")
    
    hashed_pwd = get_password_hash(password)
    new_user = models.User(username=username, hashed_password=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User successfully register ho gaya!", "user_id": new_user.id}

@app.post("/auth/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username ya password!")
    
    expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    token_data = {"sub": user.username, "exp": expiration}
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    
    return {"access_token": token, "token_type": "bearer"}

# === TASK CRUD ROUTES ===
@app.get("/tasks")
def get_all_tasks(db: Session = Depends(get_db)):
    return db.query(models.Task).all()

@app.post("/tasks/create")
def create_task(title: str, description: str = None, db: Session = Depends(get_db)):
    new_task = models.Task(title=title, description=description)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return {"message": "Task created successfully!", "task": new_task}

@app.put("/tasks/{task_id}")
def update_task(task_id: int, title: str = None, is_completed: bool = None, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        return {"error": "Task nahi mila!"}
    if title is not None:
        task.title = title
    if is_completed is not None:
        task.is_completed = is_completed
    db.commit()
    db.refresh(task)
    return {"message": "Task update ho gaya!", "task": task}

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        return {"error": "Task nahi mila!"}
    db.delete(task)
    db.commit()
    return {"message": f"Task ID {task_id} successfully delete ho gaya!"}