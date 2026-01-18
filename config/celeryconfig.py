from celery.schedules import crontab

beat_schedule = {
    "block-inactive-users-daily": {
        "task": "users.tasks.block_inactive_users",
        "schedule": crontab(hour=2, minute=0),  # Проверка каждые сутки в 2:00
        "args": (),
    },
}
