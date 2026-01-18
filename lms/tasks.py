import logging
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from users.models import CustomUser

from .models import Course, Subscription

logger = logging.getLogger(__name__)


@shared_task
def send_course_update_notification(course_id: int):
    """
    Асинхронная рассылка уведомлений подписчикам об обновлении курса
    """
    try:
        course = Course.objects.get(id=course_id)
        # ✅ Проверка: курс не обновлялся >4 часа
        if course.updated_at and (timezone.now() - course.updated_at) < timedelta(hours=4):
            logger.info(f"Курс {course.id} обновлялся недавно, пропускаем рассылку")
            return False

        # Получаем подписчиков
        subscriptions = Subscription.objects.filter(course=course).select_related("user")
        users = [sub.user for sub in subscriptions if sub.user.email]

        if not users:
            logger.info(f"Подписчиков на курс {course.id} нет")
            return True

        # Формируем письмо
        subject = f"Обновление курса: {course.title}"
        message = (
            f"Дорогой подписчик!\n\n"
            f"Курс '{course.title}' был обновлен.\n\n"
            f"Доступно новое содержимое для изучения.\n"
            f"Ссылка: {settings.FRONTEND_URL}/courses/{course.id}\n\n"
            f"С уважением,\nКоманда LMS"
        )

        # Отправляем
        sent_count = 0
        for user in users:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True,
            )
            sent_count += 1

        logger.info(f"Рассылка курса {course.id}: отправлено {sent_count} писем")
        return True

    except Course.DoesNotExist:
        logger.error(f"Курс {course_id} не найден")
        return False
    except Exception as e:
        logger.error(f"Ошибка рассылки курса {course_id}: {str(e)}")
        return False
