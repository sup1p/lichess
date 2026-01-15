# Lichess Stats (FastAPI + React)

Полноценный пример приложения для просмотра профиля и истории игр Lichess на стеке FastAPI, PostgreSQL, Redis, Celery и React (Vite, TypeScript). Управление зависимостями: backend — uv, frontend — pnpm.

## Стек
- Backend: FastAPI, SQLAlchemy, Alembic, Celery, Redis
- Frontend: React + Vite + TypeScript
- БД: PostgreSQL
- Инфра: Docker Compose

## Быстрый старт
1. Скопируйте окружение: `cp .env.example .env` и заполните `LICHESS_CLIENT_ID`, `LICHESS_CLIENT_SECRET`.
2. Установите менеджеры: `pip install uv` (или используйте уже установленный в репо `.venv`), `npm install -g pnpm`.
3. Backend локально: `cd backend && uv sync`, запуск `uv run uvicorn app.main:app --reload`.
4. Frontend локально: `cd frontend && pnpm install && pnpm dev --host`.
5. Docker: `docker compose up --build` (использует uv внутри контейнера и pnpm-готовый фронт).

## Миграции
- Создать новую: `uv run alembic revision -m "msg"` (из папки backend).
- Применить: `uv run alembic upgrade head`.

## Celery
- В составе docker-compose поднимаются `celery-worker` и `celery-beat`.
- Периодическая задача `sync_recent_games` обновляет новые партии каждые 5 минут.

## Архитектура
- `backend/app` — FastAPI, маршруты `/api/auth`, `/api/profile`, `/api/games`.
- `backend/app/tasks.py` — фоновая синхронизация игр.
- `frontend/src` — Vite/React, компоненты `ProfileCard`, `GamesTable`.

## Что доделать под прод
- Безопасные сессии (JWT или серверные куки) вместо заголовка `X-User`.
- Обновление токена по `refresh_token`.
- Более полная схематика Celery/Redis (наблюдение, ретраи).
- Тесты (pytest) и линт (ruff, mypy, eslint) — базовые конфиги уже есть.
