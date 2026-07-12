from sqlalchemy.orm import Session
import models

class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return self.db.query(models.Task).all()

    def create(self, title: str, description: str = None):
        new_task = models.Task(title=title, description=description)
        self.db.add(new_task)
        self.db.commit()
        self.db.refresh(new_task)
        return new_task

    def update(self, task_id: int, title: str = None, is_completed: bool = None):
        task = self.db.query(models.Task).filter(models.Task.id == task_id).first()
        if not task:
            return None
        if title is not None:
            task.title = title
        if is_completed is not None:
            task.is_completed = is_completed
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task_id: int):
        task = self.db.query(models.Task).filter(models.Task.id == task_id).first()
        if not task:
            return False
        self.db.delete(task)
        self.db.commit()
        return True