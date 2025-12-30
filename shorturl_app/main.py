from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import sqlite3
import secrets
import string
from pathlib import Path

app = FastAPI(title="Short URL Service", description="URL shortening service")

# Путь к базе данных в томе
DB_PATH = Path("/app/data/shorturl.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Длина короткого идентификатора
SHORT_ID_LENGTH = 8


# Модели данных
class URLRequest(BaseModel):
    url: str


class ShortURLResponse(BaseModel):
    short_id: str
    short_url: str


class URLStats(BaseModel):
    short_id: str
    full_url: str


def generate_short_id() -> str:
    """Генерация случайного короткого идентификатора"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(SHORT_ID_LENGTH))


# Инициализация базы данных
def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS short_urls (
            short_id TEXT PRIMARY KEY,
            full_url TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


@app.on_event("startup")
async def startup_event():
    init_db()


@app.post("/shorten", response_model=ShortURLResponse, status_code=201)
async def shorten_url(request: URLRequest):
    """Создание короткой ссылки для полного URL"""
    # Проверяем, что URL валидный
    if not request.url.startswith(('http://', 'https://')):
        raise HTTPException(status_code=400, detail="URL must start with http:// or https://")
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Генерируем уникальный short_id
    while True:
        short_id = generate_short_id()
        cursor.execute("SELECT short_id FROM short_urls WHERE short_id = ?", (short_id,))
        if not cursor.fetchone():
            break
    
    # Сохраняем в базу данных
    cursor.execute(
        "INSERT INTO short_urls (short_id, full_url) VALUES (?, ?)",
        (short_id, request.url)
    )
    conn.commit()
    conn.close()
    
    # Формируем короткий URL (в реальном приложении здесь был бы домен)
    short_url = f"/{short_id}"
    
    return ShortURLResponse(short_id=short_id, short_url=short_url)


@app.get("/{short_id}")
async def redirect_to_url(short_id: str):
    """Перенаправление на полный URL по короткому идентификатору"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT full_url FROM short_urls WHERE short_id = ?", (short_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Short URL not found")
    
    return RedirectResponse(url=row[0], status_code=302)


@app.get("/stats/{short_id}", response_model=URLStats)
async def get_url_stats(short_id: str):
    """Получение информации о сокращённой ссылке"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT short_id, full_url FROM short_urls WHERE short_id = ?", (short_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Short URL not found")
    
    return URLStats(short_id=row[0], full_url=row[1])

