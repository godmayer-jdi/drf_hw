from rest_framework import serializers

from .models import Course, Lesson
from .validators import validate_rutube_link


class LessonSerializer(serializers.ModelSerializer):
    video_link = serializers.URLField(validators=[validate_rutube_link])
    class Meta:
        model = Lesson
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = "__all__"

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        """Проверяет подписку текущего пользователя"""
        user = self.context["request"].user
        return obj.subscriptions.filter(user=user).exists()
