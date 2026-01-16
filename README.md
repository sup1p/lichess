# Lichess Stats

Веб-приложение для просмотра профиля и истории игр Lichess с фильтрацией, пагинацией и фоновой синхронизацией партий.

## Стек

**Backend:**
- FastAPI — REST API с async/await
- SQLAlchemy + Alembic — ORM и миграции БД
- PostgreSQL — основная БД (asyncpg драйвер)
- Redis — брокер сообщений и кэш
- Celery — фоновые задачи синхронизации игр
- uv — быстрый менеджер пакетов и виртуальных окружений

**Frontend:**
- React 19 + TypeScript
- Vite — сборка и dev-сервер
- React Router — навигация
- Axios — HTTP-клиент
- pnpm — менеджер пакетов

**Инфраструктура:**
- Docker Compose — оркестрация контейнеров
- 6 сервисов: backend, frontend, db, redis, celery-worker, celery-beat

## Быстрый старт

### 1. Настройка окружения
```bash
cp .env.example .env
```

Заполните в `.env`:
- `LICHESS_CLIENT_ID` — любая комбинация символов(для уникальности)
- `SECRET_KEY` — секретный ключ для подписи токенов - тоже рандом

### 2. Запуск через Docker
```bash
docker compose up --build
```

Сервисы:
- Frontend: [http://localhost:5173](http://localhost:5173)
- Backend API: [http://localhost:8000](http://localhost:8000)
- API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. Локальная разработка (опционально)

**Backend:**
```bash
cd backend
pip install uv
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install -g pnpm
pnpm install
pnpm dev
```

## Основные возможности

### API Endpoints
- `GET /api/auth/login` — инициация OAuth-авторизации через Lichess
- `GET /api/auth/callback` — колбэк OAuth, создание пользователя и синхронизация всех игр
- `GET /api/profile` — профиль пользователя с рейтингами (из Lichess API)
- `GET /api/games` — список партий с фильтрацией (opening, result, time_class) и пагинацией

### Фоновые задачи (Celery)
- `sync_all_user_games(user_id)` — первичная синхронизация всех игр при регистрации (батчами по 30)
- `sync_recent_games()` — периодическое обновление новых партий каждые 5 минут (через celery-beat)

### UI Компоненты
- `ProfileCard` — карточка с аватаром, рейтингами и статистикой
- `GamesTable` — таблица игр с сортировкой
- `Pagination` — постраничная навигация

## База данных

### Миграции
```bash
cd backend
uv run alembic revision --autogenerate -m "описание"
uv run alembic upgrade head
```

### Модели
- **User** — пользователи (lichess_id, username, access_token, refresh_token)
- **Game** — партии (game_id, white, black, result, opening, time_class, played_at, pgn)


## Известные проблемы

### Permission denied на entrypoint.sh (Mac/Linux)(пофикшено но может быть)
```bash
chmod +x backend/entrypoint.sh
git update-index --chmod=+x backend/entrypoint.sh
```

