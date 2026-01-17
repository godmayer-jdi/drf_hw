import os
import platform

from celery import Celery
#  from .celeryconfig import beat_schedule # Для прямого подключения расписания проверки "beat_schedule" из celeryconfig.py

#  Проверка платформы и, если Windows: отключаем GSSAPI
if platform.system() == "Windows":
    os.environ["KRB5_CONFIG"] = ""
    os.environ["NO_GSSAPI"] = "1"

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("config.celeryconfig")  # Загружаем расписание из config/celeryconfig.py. Отключить/закомментировать при применении прямого подключения.
#  app.conf.beat_schedule = beat_schedule  # Для прямого подключения расписания проверки "beat_schedule" из celeryconfig.py
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
