from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.shortcuts import reverse
from .models import Course, Lesson

User = get_user_model()


class LessonAndSubscriptionTests(APITestCase):
    def setUp(self):
        """Создаем тестовые данные"""
        self.client = APIClient()

        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.moderator = User.objects.create_user(
            email='moder@example.com',
            password='testpass123'
        )

        group, created = Group.objects.get_or_create(name='moderators')
        self.moderator.groups.add(group)

        self.course = Course.objects.create(
            title='Test Course',
            description='Test desc',
            owner=self.user
        )

        # Полные данные для урока
        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            description='Test desc',
            preview='lessons/test.jpg',
            video_link='https://youtu.be/dQw4w9WgXcQ',
            course=self.course,
            owner=self.user
        )

    def test_lesson_crud_user(self):
        """Тест CRUD уроков обычным пользователем"""
        self.client.force_authenticate(user=self.user)

        # GET список — работает
        response = self.client.get('/api/lessons/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # POST создание — ПОЛНЫЕ ДАННЫЕ
        data = {
            'title': 'New Lesson',
            'description': 'New lesson description',
            'preview': 'lessons/new_lesson.jpg',
            'video_link': 'https://youtu.be/valid123',
            'course': self.course.id
        }
        response = self.client.post('/api/lessons/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        bad_data = {
            'title': 'Bad Lesson',
            'description': 'Bad desc',
            'preview': 'lessons/bad.jpg',
            'video_link': 'https://vk.com/video',
            'course': self.course.id
        }
        response = self.client.post('/api/lessons/', bad_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_course_subscribe_toggle(self):
        """Тест toggle подписки"""
        self.client.force_authenticate(user=self.user)

        response = self.client.post('/api/courses/subscribe/',
                                    {'course_id': self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка добавлена')

        response = self.client.post('/api/courses/subscribe/',
                                    {'course_id': self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка удалена')

    def test_moderator_permissions(self):
        """Тест прав модератора"""
        self.client.force_authenticate(user=self.moderator)

        data = {
            'title': 'Mod Lesson',
            'description': 'Mod desc',
            'preview': 'lessons/mod.jpg',
            'video_link': 'https://youtu.be/test',
            'course': self.course.id
        }
        response = self.client.post('/api/lessons/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.get('/api/lessons/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
