import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta

from .models import CustomUser

logger = logging.getLogger(__name__)


@shared_task
def block_inactive_users():
    """
    Периодическая задача: блокировать пользователей неактивных >30 дней
    """
    try:
        cutoff_date = timezone.now() - timedelta(days=30)
        inactive_users = CustomUser.objects.filter(
            last_login__lt=cutoff_date,
            is_active=True
        ).exclude(is_superuser=True)  # исключаем из задачи пользователей-администраторов

        blocked_count = 0
        for user in inactive_users:
            user.is_active = False
            user.save(update_fields=['is_active'])
            logger.info(f"Заблокирован неактивный пользователь: {user.email}")
            blocked_count += 1

        logger.info(f"Задача block_inactive_users: заблокировано {blocked_count} пользователей")
        return blocked_count

    except Exception as e:
        logger.error(f"Ошибка в block_inactive_users: {str(e)}")
        return 0
