# FastAPI Микросервисы: ToDo и Short URL

Проект содержит два микросервиса на базе FastAPI:
- **ToDo-сервис** - CRUD операции для списка задач
- **Сервис сокращения URL** - создание коротких ссылок и редиректы

## Структура проекта

```
.
├── todo_app/
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── shorturl_app/
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
└── README.md
```

## Локальный запуск

### Предварительные требования

- Python 3.11+
- pip

### ToDo-сервис

1. Перейдите в директорию сервиса:
```bash
cd todo_app
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Запустите сервис:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Сервис будет доступен по адресу: http://localhost:8000
Документация API: http://localhost:8000/docs

### Сервис сокращения URL

1. Перейдите в директорию сервиса:
```bash
cd shorturl_app
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Запустите сервис:
```bash
uvicorn main:app --host 0.0.0.0 --port 8001
```

Сервис будет доступен по адресу: http://localhost:8001
Документация API: http://localhost:8001/docs

## Запуск через Docker

### Сборка образов

```bash
# Сборка образа ToDo-сервиса
docker build -t todo-service:latest todo_app/

# Сборка образа сервиса сокращения URL
docker build -t shorturl-service:latest shorturl_app/
```

### Создание именованных томов

```bash
docker volume create todo_data
docker volume create shorturl_data
```

### Запуск контейнеров

```bash
# Запуск ToDo-сервиса
docker run -d -p 8000:80 -v todo_data:/app/data --name todo-service todo-service:latest

# Запуск сервиса сокращения URL
docker run -d -p 8001:80 -v shorturl_data:/app/data --name shorturl-service shorturl-service:latest
```

### Проверка работы

```bash
# Проверка статуса контейнеров
docker ps

# Просмотр логов
docker logs todo-service
docker logs shorturl-service
```

## API Endpoints

### ToDo-сервис (http://localhost:8000)

- `POST /items` - создание задачи
  ```json
  {
    "title": "Новая задача",
    "description": "Описание задачи",
    "completed": false
  }
  ```

- `GET /items` - получение списка всех задач
- `GET /items/{item_id}` - получение задачи по ID
- `PUT /items/{item_id}` - обновление задачи
- `DELETE /items/{item_id}` - удаление задачи

### Сервис сокращения URL (http://localhost:8001)

- `POST /shorten` - создание короткой ссылки
  ```json
  {
    "url": "https://example.com/very/long/url"
  }
  ```

- `GET /{short_id}` - перенаправление на полный URL
- `GET /stats/{short_id}` - получение информации о ссылке

## Тестирование

### Тестирование ToDo-сервиса

```bash
# Создание задачи
curl -X POST "http://localhost:8000/items" \
  -H "Content-Type: application/json" \
  -d '{"title": "Купить молоко", "description": "В магазине", "completed": false}'

# Получение всех задач
curl http://localhost:8000/items

# Получение задачи по ID
curl http://localhost:8000/items/1

# Обновление задачи
curl -X PUT "http://localhost:8000/items/1" \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'

# Удаление задачи
curl -X DELETE http://localhost:8000/items/1
```

### Тестирование сервиса сокращения URL

```bash
# Создание короткой ссылки
curl -X POST "http://localhost:8001/shorten" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.google.com"}'

# Перенаправление (в браузере или с флагом -L)
curl -L http://localhost:8001/{short_id}

# Получение статистики
curl http://localhost:8001/stats/{short_id}
```

## Публикация на Docker Hub

### 1. Сборка образов с тегами для Docker Hub

```bash
docker build -t karim90403/todo-service:latest todo_app/
docker build -t karim90403/shorturl-service:latest shorturl_app/
```

### 2. Вход в Docker Hub

```bash
docker login
```

### 3. Публикация образов

```bash
docker push karim90403/todo-service:latest
docker push karim90403/shorturl-service:latest
```

### 4. Запуск опубликованных образов

```bash
docker run -d -p 8000:80 -v todo_data:/app/data karim90403/todo-service:latest
docker run -d -p 8001:80 -v shorturl_data:/app/data karim90403/shorturl-service:latest
```

## Хранение данных

Оба сервиса используют SQLite для хранения данных. Файлы базы данных находятся в директории `/app/data` внутри контейнера, которая подключена как именованный том. Это обеспечивает сохранность данных при перезапуске или удалении контейнера.

- ToDo-сервис: `/app/data/todo.db`
- Сервис сокращения URL: `/app/data/shorturl.db`

## Остановка и удаление контейнеров

```bash
# Остановка контейнеров
docker stop todo-service shorturl-service

# Удаление контейнеров
docker rm todo-service shorturl-service

# Удаление томов (опционально, данные будут потеряны)
docker volume rm todo_data shorturl_data
```

