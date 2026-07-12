from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import models
from database import engine, get_db

# Ye line database me saare tables automatic create kar degi agar wo nahi bane hain
models.Base.metadata.create_all(bind=engine)
app = FastAPI()

@app.get("/status")
def read_status():
    return {"status": "success", "database": "Connected & Tables Created! 🚀"}

# Ek test route jo database me naya task add karega
@app.post("/tasks/create")
def create_task(title: str, description: str = None, db: Session = Depends(get_db)):
    new_task = models.Task(title=title, description=description)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return {"message": "Task created successfully!", "task": new_task}

# Saare tasks ko database se lekar aane ke liye GET route
@app.get("/tasks")
def get_all_tasks(db: Session = Depends(get_db)):
    tasks = db.query(models.Task).all()
    return tasks