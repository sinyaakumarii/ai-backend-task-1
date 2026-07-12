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

# 1. Update Route: Task ko complete mark karne ya title badalne ke liye
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

# 2. Delete Route: Task ko database se hatane ke liye
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        return {"error": "Task nahi mila!"}
        
    db.delete(task)
    db.commit()
    return {"message": f"Task ID {task_id} successfully delete ho gaya!"}