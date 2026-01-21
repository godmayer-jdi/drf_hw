# LMS API (Django + DRF + PostgreSQL + Redis + Celery)

REST API для системы управления обучением с оплатой через Stripe, JWT авторизацией и периодическими задачами Celery.

##  Быстрый запуск (Docker Compose)

### Предварительные требования
```bash
Docker >= 20.10
Docker Compose >= 2.0
```


### 1. Клонировать проект

```bash
git clone
cd DRF_hw
```


### 2. Настроить переменные окружения

```bash
cp .env.example .env
# Отредактировать .env (DB_PASSWORD, STRIPE ключи)
```


### 3. Запустить проект (единая команда)

```bash
docker compose up --build -d
```


### 4. Выполнить миграции и создать суперпользователя

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
```


##  Проверка работоспособности сервисов

| Сервис | Команда проверки | Ожидаемый результат | URL/API |
| :-- | :-- | :-- | :-- |
| **Backend (Django)** | `docker compose logs backend` | `Starting development server at http://0.0.0.0:8000/` | http://localhost:8000/swagger/ |
| **PostgreSQL** | `docker compose logs db` | `database system is ready to accept connections` | localhost:5433 |
| **Redis** | `docker compose exec redis redis-cli ping` | `PONG` | localhost:6379 |
| **Celery Worker** | `docker compose logs celery` | `celery@... ready` | Логи задач |
| **Celery Beat** | `docker compose logs celery-beat` | `beat: Starting...` | `/admin/django_celery_beat/` |


### Суперпользователь

```bash
docker compose exec backend python manage.py createsuperuser
# Username: admin
# Email: test@test.com
# Password: admin
```


### База данных

```bash
# Подключение к PostgreSQL
docker compose exec db psql -U postgres -d lms_db

# Сброс БД (осторожно!)
docker compose down -v
docker compose up --build -d
```


##  Структура сервисов

```
docker-compose.yaml (5 сервисов):
├── db (PostgreSQL:16)    → localhost:5433
├── redis (Redis:7)       → localhost:6379  
├── backend (Django:5.2)  → localhost:8000
├── celery (Worker)       → Фоновые задачи
└── celery-beat (Beat)    → Периодические задачи
```


##  Настройки (.env)

```env
# Django
SECRET_KEY=django-insecure-superkey-change-in-production
DEBUG=True
ALLOWED_HOSTS=*

# База данных
DB_NAME=lms_db
DB_USER=postgres
DB_PASSWORD=postgres123
DB_HOST=db
DB_PORT=5432

# Redis/Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Stripe (тестовые ключи)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=test@example.com
```


##  Функционал API

| Эндпоинт | Метод | Описание |
| :-- | :-- | :-- |
| `/swagger/` | GET | Swagger UI документация |
| `/admin/` | GET | Django Admin |
| `/api/token/` | POST | Получить JWT токен |
| `/api/courses/` | GET/POST | Список/создание курсов |
| `/api/courses/1/pay/` | POST | Оплата курса (Stripe) |

##  Остановка проекта

```bash
# Остановить контейнеры (сохранить БД)
docker compose down

# Полная очистка (БД + volumes)
docker compose down -v

# Удалить образы
docker compose down --rmi all -v
```


##  Локальная разработка (альтернатива)

```bash
# 1. Запустить БД и Redis
docker compose up db redis -d

# 2. Локальный Django (.venv)
python manage.py runserver 8000
```


##  Частые проблемы и решения

| Проблема | Решение |
| :-- | :-- |
| `backend` не запускается | `docker compose logs backend` |
| `Connection refused` к БД | Проверить `DB_HOST=db` в `.env` |
| Swagger 404 | `http://localhost:8000/swagger/` |
| Celery не работает | `docker compose logs celery` |
| Миграции не прошли | `docker compose exec backend python manage.py migrate` |

##  Мониторинг

```bash
# Статус всех сервисов
docker compose ps

# Ресурсы
docker stats

# Сеть
docker network ls
docker network inspect <project>_default
```
