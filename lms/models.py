from django.db import models

class Course(models.Model):
    title = models.CharField(max_length=200)
    preview = models.ImageField(upload_to='courses/previews/')
    description = models.TextField()

    def __str__(self):
        return self.title

class Lesson(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    preview = models.ImageField(upload_to='lessons/previews/')
    video_link = models.URLField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')

    def __str__(self):
        return f"{self.title} ({self.course.title})"
