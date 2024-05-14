from datetime import datetime
from typing import Union
from typing import List
import sqlite3

from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

app = FastAPI() 
origins = [
    "*",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class TaskCreate(BaseModel):
    title: str
    description: str
    completed:str

class Task(TaskCreate):
    id: int

def create_connection():
    connection = sqlite3.connect("task.db")
    return connection
def create_table():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS task (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        completed TEXT NULL,
        created TEXT NULL,
        description TEXT NOT NULL,
        title TEXT NOT NULL
    )
    """)
    connection.commit()
    connection.close()

def create_task(task: TaskCreate):
    connection = create_connection()
    cursor = connection.cursor()
    dcreated=datetime.strftime(datetime.now(), "%d-%b-%Y-%H:%M:%S")
    cursor.execute("INSERT INTO task (title,description,completed,created ) VALUES (?, ?,?,?)", (task.title, task.description,task.completed,dcreated))
    connection.commit()
    connection.close()

create_table() # Call this function to create the table


@app.get( "/" ) 
async def  read_root (): 
    return { "message" : "Selamat datang di CRUD API" }

@app.post("/task/")
async def create_task_endpoint(task: TaskCreate):
    task_id = create_task(task)
    return {"id": task_id, **task.dict()}


@app.get("/task/", response_model=List[Task])
def get_task():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM task')
    task_data = cursor.fetchall()
    cursor.close()
    connection.close()
    return [Task(id=task[0], completed=task[1], description=task[3] , title=task[4]) for task in task_data]

@app.get("/task/{task_id}", response_model=Task)
def get_task(task_id: int):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM task WHERE id = ?', (task_id,))
    task_data = cursor.fetchone()
    cursor.close()
    connection.close()
    if task_data:
        return Task(id=task_data[0], completed=task_data[1], description=task_data[3] , title=task_data[4])
    else:
        raise HTTPException(status_code=404, detail="Task not found")

# Update operation
@app.put("/task/{task_id}", response_model=Task)
def update_task(task_id: int, task: TaskCreate):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute('UPDATE task SET title=?, description=?,completed=? WHERE id=?', (task.title, task.description,task.completed, task_id))
    connection.commit()
    connection.close()
    if cursor.rowcount > 0:
        return {"id": task_id, **task.dict()}
    else:
        raise HTTPException(status_code=404, detail="Task not found")
    
@app.delete("/task/{task_id}")
def delete_task(task_id: int):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute('DELETE FROM task WHERE id=?', (task_id,))
    connection.commit()
    connection.close()
    if cursor.rowcount > 0:
        return {"id": task_id}
    else:
        raise HTTPException(status_code=404, detail="Task not found")
