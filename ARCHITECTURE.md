# Архитектура проекта

## Общая концепция

Архитектура с разделением на frontend (React SPA), backend (FastAPI REST API) и фоновый воркер (Celery). Все взаимодействие через HTTP и Redis pub/sub.

## Backend (FastAPI)

### Структура слоёв

```
app/
├── api/          # Роутеры (HTTP handlers)
├── core/         # Инфраструктура (config, db, auth)
├── models/       # SQLAlchemy модели
├── schemas/      # Pydantic схемы (DTO)
├── services/     # Бизнес-логика (CRUD, Lichess API, Celery)
└── tasks.py      # Celery задачи
```

**Паттерны:**
- **Dependency Injection** — через FastAPI `Depends()` для DB сессий и авторизации
- **Repository Pattern** — `crud.py` изолирует логику работы с БД
- **Service Layer** — `lichess.py` инкапсулирует взаимодействие с внешним API
- **Singleton Settings** — `@lru_cache` для конфигурации (читается один раз)

### Аутентификация

**OAuth 2.0 с PKCE:**
1. Генерируем `code_verifier` + `code_challenge` (SHA-256)
2. Редиректим на Lichess OAuth с challenge
3. Получаем `code` в колбэке, обмениваем на `access_token` с verifier
4. Сохраняем токен в БД, возвращаем через cookie `auth_token`

**Текущая реализация:**
- Bearer token в заголовке `Authorization` (из cookie)
- Dependency `get_current_user()` декодирует JWT и достаёт User из БД
- **TODO:** добавить refresh token ротацию, короткий TTL для access token

### База данных

**PostgreSQL + SQLAlchemy (async):**
- Двусторонняя связь `User ↔ Game` через `relationship()`
- Индексы на `game_id`, `played_at`, `user_id` для быстрых запросов
- Cascade delete: удаление User удаляет все Game

**Alembic миграции:**
- Автогенерация через `alembic revision --autogenerate`
- Версионирование схемы в `alembic/versions/`

### Celery + Redis

**Архитектура задач:**
- **sync_all_user_games** — при первом логине синхронизирует всю историю батчами (30 игр/запрос)
- **sync_recent_games** — периодическая задача (каждые 5 мин), обновляет последние игры для всех пользователей

**Celery использует sync engine:**
- Celery worker не поддерживает asyncio event loop
- Создаём отдельный синхронный `create_engine()` для задач
- URL конвертируем: `postgresql+asyncpg://` → `postgresql://`

**Beat scheduler:**
- `celery-beat` — крон-подобная система для периодических задач
- Конфигурация в `celery_app.py` через `beat_schedule`

## Frontend (React + TypeScript)

### Структура

```
src/
├── api/         # Axios клиент (базовая настройка)
├── components/  # Переиспользуемые компоненты
├── hooks/       # Custom hooks (useAuth, useProfile, useGames)
├── pages/       # Страницы (DashboardPage)
├── services/    # API методы (api.ts)
├── types/       # TypeScript типы
└── utils/       # Утилиты (formatDate)
```

**Паттерны:**
- **Custom Hooks** — инкапсуляция логики состояния (auth, API calls)
- **Separation of Concerns** — hooks для логики, components для UI
- **Controlled Components** — состояние пагинации и фильтров в родительском компоненте

### Управление состоянием

**Без Redux/Zustand:**
- Локальное состояние через `useState` в custom hooks
- Авторизация — cookie-based, токен в httpOnly cookie
- API calls — через Axios с автоматической отправкой credentials

**useAuth:**
- Проверяет `/api/auth/check` на маунте
- Редирект на `/api/auth/login` для OAuth flow
- Logout очищает cookie через `/api/auth/logout`

**useGames:**
- Пагинация + фильтрация через query params
- Дебаунсинг не используется (опционально для фильтров)

## Docker Compose

### Сервисы

1. **db** (postgres:15) — основная БД, persistent volume `pgdata`
2. **redis** (redis:7) — брокер для Celery + кэш
3. **backend** — FastAPI с hot-reload через volume mount
4. **celery-worker** — обработка задач
5. **celery-beat** — планировщик периодических задач
6. **frontend** — Vite dev server с HMR

**Зависимости:**
- frontend → backend → db, redis
- celery-worker, celery-beat → backend, redis

**Volumes:**
- `./backend:/app` — hot-reload для dev
- `./frontend:/app` + `/app/node_modules` — сохраняем node_modules в контейнере
- `pgdata:/var/lib/postgresql/data` — персистентность БД

## API дизайн

### REST принципы
- `GET /api/profile` — получить данные (из Lichess API в реальном времени)
- `GET /api/games?page=1&per_page=20&opening=Sicilian` — список с фильтрацией
- Pydantic схемы для валидации входа/выхода

### CORS
- `allow_origins=["*"]` для dev (в проде — whitelist фронтенда)
- `allow_credentials=True` для cookie-based auth

## Безопасность

**Текущие меры:**
- OAuth 2.0 с PKCE (защита от code interception)
- HttpOnly cookies (защита от XSS)
- SQLAlchemy ORM (защита от SQL injection)
- CORS ограничения (в проде)

**Риски и TODO:**
- Access token без TTL — хранится вечно
- Refresh token не используется
- Rate limiting отсутствует
- HTTPS обязателен в проде (для OAuth redirect)

## Масштабирование

**Текущие ограничения:**
- Один инстанс backend — bottleneck для CPU-intensive задач
- Redis без persistence — потеря задач при рестарте
- PostgreSQL без репликации

**План на продакшн:**
- Horizontal scaling: несколько backend workers за load balancer (Nginx/Traefik)
- Celery: увеличить количество workers, добавить мониторинг через Flower
- БД: read replicas, connection pooling (PgBouncer)
- Redis: Sentinel для HA или Elasticache

## Тестирование

**Стратегия:**
- Unit тесты — для `services/crud.py`, `services/lichess.py` (моки httpx)
- Integration тесты — для API endpoints (TestClient + test БД)
- E2E — опционально через Playwright

**Текущий статус:** pytest настроен, тесты отсутствуют.

## Мониторинг и логирование

**Dev:**
- Логи в stdout через `logging.getLogger()`
- Docker logs: `docker compose logs -f backend`

**Продакшн TODO:**
- Structured logging (JSON format)
- Centralized logs (ELK, CloudWatch)
- Metrics (Prometheus + Grafana)
- Error tracking (Sentry)
- Celery monitoring (Flower)
