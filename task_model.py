import json
import os
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional


class Priority(Enum):
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()


class TaskStatus(Enum):
    TODO = auto()
    DONE = auto()


class Task:
    def __init__(self, title: str, priority: Priority, status: TaskStatus = TaskStatus.TODO):
        self.title = title
        self.creation_date = datetime.now().isoformat()
        self.priority = priority
        self.status = status

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "creation_date": self.creation_date,
            "priority": self.priority.name,
            "status": self.status.name
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Task":
        task = cls(
            title=data["title"],
            priority=Priority[data["priority"]]
        )
        task.creation_date = data["creation_date"]
        task.status = TaskStatus[data["status"]]
        return task


class TaskManager:
    def __init__(self, file_path: str = "tasks.json"):
        self.file_path = file_path
        self.tasks: List[Task] = []
        self.load_tasks()

    def load_tasks(self) -> None:
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    data = json.load(f)
                    self.tasks = [Task.from_dict(task_data) for task_data in data]
            except (json.JSONDecodeError, KeyError):
                self.tasks = []
        else:
            self.tasks = []

    def save_tasks(self) -> None:
        with open(self.file_path, "w") as f:
            json.dump([task.to_dict() for task in self.tasks], f, indent=2)

    def add_task(self, title: str, priority: Priority) -> Task:
        task = Task(title=title, priority=priority)
        self.tasks.append(task)
        self.save_tasks()
        return task

    def toggle_task_status(self, index: int) -> None:
        if 0 <= index < len(self.tasks):
            task = self.tasks[index]
            if task.status == TaskStatus.TODO:
                task.status = TaskStatus.DONE
            else:
                task.status = TaskStatus.TODO
            self.save_tasks()

    def update_task_title(self, index: int, new_title: str) -> None:
        if 0 <= index < len(self.tasks) and new_title.strip():
            self.tasks[index].title = new_title
            self.save_tasks()

    def update_task_priority(self, index: int, new_priority: Priority) -> None:
        if 0 <= index < len(self.tasks):
            self.tasks[index].priority = new_priority
            self.save_tasks()

    def delete_task(self, index: int) -> None:
        if 0 <= index < len(self.tasks):
            del self.tasks[index]
            self.save_tasks()

    def get_tasks(self, status: Optional[TaskStatus] = None) -> List[Task]:
        if status is None:
            return self.tasks
        return [task for task in self.tasks if task.status == status] 