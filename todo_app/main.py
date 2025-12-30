from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
from pathlib import Path

app = FastAPI(title="ToDo Service", description="CRUD operations for todo items")

# Путь к базе данных в томе
DB_PATH = Path("/app/data/todo.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


# Модели данных
class TodoItem(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False


class TodoItemResponse(TodoItem):
    id: int

    class Config:
        from_attributes = True


class TodoItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


# Инициализация базы данных
def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS todo_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            completed BOOLEAN DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


@app.on_event("startup")
async def startup_event():
    init_db()


@app.post("/items", response_model=TodoItemResponse, status_code=201)
async def create_item(item: TodoItem):
    """Создание новой задачи"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO todo_items (title, description, completed) VALUES (?, ?, ?)",
        (item.title, item.description, item.completed)
    )
    item_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return TodoItemResponse(
        id=item_id,
        title=item.title,
        description=item.description,
        completed=item.completed
    )


@app.get("/items", response_model=List[TodoItemResponse])
async def get_all_items():
    """Получение списка всех задач"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, completed FROM todo_items")
    rows = cursor.fetchall()
    conn.close()
    
    return [
        TodoItemResponse(
            id=row[0],
            title=row[1],
            description=row[2],
            completed=bool(row[3])
        )
        for row in rows
    ]


@app.get("/items/{item_id}", response_model=TodoItemResponse)
async def get_item(item_id: int):
    """Получение задачи по ID"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, description, completed FROM todo_items WHERE id = ?",
        (item_id,)
    )
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return TodoItemResponse(
        id=row[0],
        title=row[1],
        description=row[2],
        completed=bool(row[3])
    )


@app.put("/items/{item_id}", response_model=TodoItemResponse)
async def update_item(item_id: int, item_update: TodoItemUpdate):
    """Обновление задачи по ID"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Получаем текущие данные
    cursor.execute(
        "SELECT id, title, description, completed FROM todo_items WHERE id = ?",
        (item_id,)
    )
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Обновляем только переданные поля
    title = item_update.title if item_update.title is not None else row[1]
    description = item_update.description if item_update.description is not None else row[2]
    completed = item_update.completed if item_update.completed is not None else bool(row[3])
    
    cursor.execute(
        "UPDATE todo_items SET title = ?, description = ?, completed = ? WHERE id = ?",
        (title, description, completed, item_id)
    )
    conn.commit()
    conn.close()
    
    return TodoItemResponse(
        id=item_id,
        title=title,
        description=description,
        completed=completed
    )


@app.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: int):
    """Удаление задачи по ID"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("DELETE FROM todo_items WHERE id = ?", (item_id,))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Item not found")
    
    conn.commit()
    conn.close()
    
    return None

