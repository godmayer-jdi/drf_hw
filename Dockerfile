FROM python:3.13-slim

WORKDIR /app

# Системные зависимости
RUN apt-get update && apt-get install -y \
    gcc postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Установка Python зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir gunicorn -r requirements.txt

# Копируем код
COPY . .

# Создаем директории
RUN mkdir -p /app/media /app/staticfiles && \
    chown -R 1000:1000 /app/media /app/staticfiles

# Документируем порт 8000 для взаимодействия с приложением
EXPOSE 8000

# Определяем команду для запуска приложения
CMD ["sh", "-c", "python manage.py migrate --noinput && \
     python manage.py collectstatic --noinput && \
     gunicorn config.wsgi:application --bind 0.0.0.0:8000 \
     --workers 3 --threads 2 --timeout 120"]
