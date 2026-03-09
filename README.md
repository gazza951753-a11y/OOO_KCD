# ООО КЦД — Кадровая система

HR-система с поддержкой 4 ролей: суперадмин, кадровик, руководитель, сотрудник.

## Модули

| Модуль | Описание |
|--------|----------|
| Табельный учёт | Учёт рабочего времени, статусы, утверждение |
| Документооборот | Заявки, маршрут согласования, статусы |
| Отчётность | Выгрузка в Excel (.xlsx) и PDF |
| Аудит | Журнал всех действий в системе |

## Стек

**Бэкенд:** Python 3.12 · FastAPI · SQLAlchemy · Alembic · PostgreSQL 16 · JWT
**Фронтенд:** React 18 · Vite · TypeScript · shadcn/ui · Tailwind CSS · Axios
**Отчёты:** openpyxl (Excel) · reportlab (PDF)
**Деплой:** Docker · Docker Compose

## Быстрый старт

```bash
# 1. Клонировать репозиторий
git clone <repo-url>
cd OOO_KCD

# 2. Скопировать конфигурацию
cp .env.example .env
# При необходимости отредактировать .env

# 3. Запустить
docker compose up --build

# 4. Открыть в браузере
# Приложение:  http://localhost
# Swagger API: http://localhost/api/docs
```

## Тестовые аккаунты

| Роль | Email | Пароль |
|------|-------|--------|
| Суперадмин | admin@kcd.ru | Admin123! |
| Кадровик | hr@kcd.ru | Hr123456! |
| Руководитель | manager@kcd.ru | Manager123! |
| Сотрудник | employee@kcd.ru | Employee123! |

## Структура проекта

```
OOO_KCD/
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic/          # Миграции БД
│   └── app/
│       ├── main.py       # FastAPI приложение
│       ├── models/       # SQLAlchemy модели
│       ├── schemas/      # Pydantic схемы
│       ├── routers/      # API роутеры
│       ├── services/     # Бизнес-логика
│       ├── core/         # JWT, RBAC, аудит
│       └── seed.py       # Начальные данные
└── frontend/
    ├── Dockerfile
    ├── nginx.conf
    └── src/
        ├── App.tsx
        ├── api/          # Axios + интерцепторы
        ├── store/        # Zustand auth store
        ├── components/   # UI + Layout
        └── pages/        # Страницы по модулям
```

## API

Документация (Swagger UI): `http://localhost/api/docs`

Основные группы:
- `POST /api/auth/login` — вход
- `GET /api/auth/me` — текущий пользователь
- `GET/POST /api/users` — управление пользователями
- `GET/POST /api/timesheet` — табельный учёт
- `GET/POST /api/documents` — документооборот
- `GET /api/reports/timesheet/excel` — отчёт Excel
- `GET /api/reports/timesheet/pdf` — отчёт PDF
- `GET /api/audit` — журнал аудита
