from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from lms.models import Course, Lesson


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)
    phone = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []


    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email


class Payment(models.Model):
    PAYMENT_METHODS = [
        ("cash", "Наличные"),
        ("transfer", "Перевод на счет"),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='payments')
    paid_course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    paid_lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    payment_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS)

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-payment_date']

    def __str__(self):
        if self.paid_course:
            course_lesson = f"Курс: {self.paid_course}"
        elif self.paid_lesson:
            course_lesson = f"Урок: {self.paid_lesson}"
        else:
            course_lesson = "Неизвестный объект"

        return f"{str(self.user)} - {course_lesson} - {self.amount:.2f} руб. ({self.payment_method})"
