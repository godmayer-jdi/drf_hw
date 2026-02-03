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
git clone https://github.com/godmayer-jdi/drf_hw.git
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


## ️ **ПРОДАКШН ДЕПЛОЙ (YandexCloud)**

### **Критерий 4.4: Инструкции по настройке сервера**

#### **1. Подключение к серверу**

```bash
ssh -i ssh-key_YC godmayer385@158.160.20.204
# passphrase: testadmin
```


#### **2. Настройка сервера (выполнить один раз)**

```bash
# Обновление и установка
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io docker-compose nginx ufw git curl

# Docker права
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
newgrp docker

# Firewall (критерий 1.5 безопасность)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw --force enable
sudo ufw status

# Директория проекта (критерий 1.1)
sudo mkdir -p /var/www/drf_hw
sudo chown $USER:$USER /var/www/drf_hw -R
cd /var/www/drf_hw
```


#### **3. Ручной деплой**

```bash
# Клонировать (первый раз)
git clone https://github.com/godmayer-jdi/drf_hw.git .
git checkout hw-docker

# Настроить .env
cp .env.example .env
# Отредактировать: SECRET_KEY, DB_PASSWORD

# Запуск (критерий 1.4 доступно по IP)
docker compose up -d --build

# Проверка (критерий 1.6 auto-restart)
docker compose ps
docker compose logs -f
```

**Приложение доступно:** **http://158.160.20.204**

##  **CI/CD GitHub Actions (Задание 2)**

### **Критерий 4.5: Шаги запуска workflow**

#### **1. Настройка GitHub Secrets**

**GitHub → Settings → Secrets and variables → Actions:**

```
SERVER_IP=158.160.20.204
SERVER_USER=godmayer385
SSH_PRIVATE_KEY=-----BEGIN... (ssh-key_YC)
SSH_PASSPHRASE=testadmin
PROD_SECRET_KEY=django-super-secret-production-key
PROD_DB_PASSWORD=secure_db_password_123
```


#### **2. Автоматический запуск**

```
1. git push origin hw-docker  → Workflow запускается автоматически (критерий 2.2)
2. Тесты pytest               → (критерий 2.3, 2.4, 2.5)
3. Деплой на сервер           → Только после успешных тестов (критерий 2.6, 2.7)
```


#### **3. Проверка workflow**

```
GitHub → Actions → CI/CD DRF_hw → Просмотр логов
Зеленые галочки = успешный деплой
```


#### **4. Ручной триггер (если нужно)**

```bash
git commit --allow-empty -m "trigger deploy"
git push origin hw-docker
```


##  Проверка работоспособности сервисов

| Сервис | Команда проверки | Ожидаемый результат | URL/API |
| :-- | :-- | :-- | :-- |
| **Nginx** | `curl http://158.160.20.204` | `200 OK` | **http://158.160.20.204** |
| **Backend (Django)** | `docker compose logs web` | `gunicorn... started` | http://158.160.20.204/swagger/ |
| **PostgreSQL** | `docker compose logs db` | `database system is ready` | **localhost:5433** (dev) |
| **Redis** | `docker compose exec redis redis-cli ping` | `PONG` | **localhost:6379** (dev) |
| **Celery Worker** | `docker compose logs celery` | `celery@... ready` | Логи задач |
| **Celery Beat** | `docker compose logs celery-beat` | `beat: Starting...` | /admin/django_celery_beat/ |

### Суперпользователь

```bash
docker compose exec web python manage.py createsuperuser
# Username: admin | Password: admin
```


## ️ Структура сервисов (Production)

```
6x Docker контейнеров:
├── nginx          → 158.160.20.204:80  (критерий 1.3)
├── web (Gunicorn) → web:8000           (proxy через nginx)
├── db (PostgreSQL:16)
├── redis (Redis:7)
├── celery (Worker)
└── celery-beat (Beat)
```


##  Настройки (.env) для продакшена

```env
# Django (критерий 3.1 секреты)
SECRET_KEY=${PROD_SECRET_KEY}           # Из GitHub Secrets
DEBUG=0                                 # Продакшн!
ALLOWED_HOSTS=158.160.20.204,localhost

# База данных
DB_NAME=lms_db
DB_USER=postgres
DB_PASSWORD=${PROD_DB_PASSWORD}         # Из GitHub Secrets
DB_HOST=db
DB_PORT=5432

# Redis/Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```


##  Функционал API

| Эндпоинт | Метод | Описание |
| :-- | :-- | :-- |
| `/swagger/` | GET | **Swagger UI** документация |
| `/admin/` | GET | **Django Admin** |
| `/api/token/` | POST | JWT токен авторизации |
| `/api/courses/` | GET/POST | Список/создание курсов |
| `/api/courses/1/pay/` | POST | Оплата курса (Stripe) |

##  Остановка и обновление

### Сервер

```bash
cd /var/www/drf_hw
docker compose down
git pull origin develop
docker compose up -d --build
```


### CI/CD (автоматически)

```bash
git push origin develop  # Тесты + деплой
```


##  Мониторинг продакшена

```bash
# Статус
docker compose ps

# Логи (все сервисы)
docker compose logs -f

# Ресурсы
docker stats

# Перезапуск
docker compose restart
```

**Live: http://158.160.20.204** | ** Auto-deploy: `git push origin hw-docker`**
