# URL Shortener

Сервис сокращения ссылок с авторизацией, аналитикой переходов и автоматическим истечением.

**Stack:** Python 3.11+ · FastAPI · SQLAlchemy · PostgreSQL · Docker

---

## Features

- **JWT-авторизация** — регистрация, логин, защищённые эндпоинты. Stateless: токен содержит `user_id`, сервер проверяет только подпись.
- **Кастомные коды** — валидация по regex (`a-zA-Z0-9`, 5–10 символов), blacklist зарезервированных слов (`admin`, `root` и т.д.).
- **TTL ссылок** — время жизни от 1 до 48 часов. Просроченные ссылки удаляются при попытке перехода (lazy expiration).
- **Аналитика** — подсчёт кликов по каждой ссылке, профиль пользователя с суммарной статистикой.
- **Ownership** — каждая ссылка привязана к владельцу. Удалить можно только свою.

---

## Architecture

```
main.py          — роуты (FastAPI)
models.py        — Pydantic-схемы с валидацией
database.py      — ORM-модели + подключение к PostgreSQL
utils.py         — JWT, хэширование паролей, генерация кодов
docker-compose   — PostgreSQL 16
```

Однослойная архитектура: роуты работают напрямую с ORM. Осознанный выбор для небольшого сервиса — не оверинжиниринг ради паттернов.

---

## API

### Auth

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/register` | Регистрация (username, email, password) |
| POST | `/api/login` | Логин → JWT-токен (7 дней) |
| GET | `/api/me` | Профиль: username, кол-во ссылок, суммарные клики |

### URLs (требуется токен)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/create_url` | Создать короткую ссылку |
| GET | `/api/my-url` | Список своих ссылок |
| GET | `/api/stats/{code}` | Статистика по ссылке |
| DELETE | `/api/{code}` | Удалить свою ссылку |
| GET | `/{code}` | Редирект (307) + счётчик кликов |

---

## Getting Started

```bash
git clone https://github.com/Flaty/url_shorter
cd url_shorter

# Поднять PostgreSQL
docker-compose up -d

# Установить зависимости
pip install -r requirements.txt

# Запустить сервер
uvicorn main:app --reload
```

Swagger UI: `http://localhost:8000/docs`

### Пример использования

```bash
# Регистрация
curl -X POST http://localhost:8000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "email": "demo@test.com", "password": "1234"}'

# Логин → получить токен
curl -X POST http://localhost:8000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "demo@test.com", "password": "1234"}'

# Создать короткую ссылку (с токеном)
curl -X POST http://localhost:8000/api/create_url \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/Flaty", "custom_code": "mylink", "expires_time": 24}'
```

---

## Design Notes

- **Lazy expiration** — просроченные ссылки удаляются только при попытке перехода. Простое решение без фонового планировщика; trade-off — «мёртвые» записи остаются в БД до обращения.
- **Генерация кодов** — случайная строка 5–10 символов из `[a-zA-Z0-9]` с проверкой коллизий в БД. Для текущего масштаба достаточно, при росте стоит перейти на base62-encoding от auto-increment ID.
- **Однослойная архитектура** — для сервиса с 7 эндпоинтами трёхслойное разделение (routes → services → repositories) избыточно. В AniSync, где 15+ эндпоинтов и фоновые задачи, слои оправданы.

---

## Roadmap

- [ ] Alembic-миграции вместо `Base.metadata.create_all()`
- [ ] Redis-кэш для популярных ссылок
- [ ] Background task для очистки просроченных ссылок
- [ ] Rate limiting (по пользователю)
- [ ] Переменные окружения вместо хардкода конфигурации
