from django.db import models


class Course(models.Model):
    objects = None
    title = models.CharField(max_length=200)
    preview = models.ImageField(upload_to="courses/previews/")
    description = models.TextField()
    owner = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def __str__(self):
        return self.title


class Lesson(models.Model):
    objects = None
    title = models.CharField(max_length=200)
    description = models.TextField()
    preview = models.ImageField(upload_to="lessons/previews/")
    video_link = models.URLField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    owner = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ['id']

    def __str__(self):
        return f"{self.title} ({self.course})"


class Subscription(models.Model):
    objects = None
    user = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE, related_name="subscriptions")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="subscriptions")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        unique_together = ["user", "course"]  # Один курс — одна подписка

    def __str__(self):
        return f"{self.user.email} → {self.course.title}"
