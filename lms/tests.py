from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.shortcuts import reverse
from .models import Subscription, Course, Lesson

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
            video_link='https://rutube.ru/video/b2a127bfc206b85978150f390156d052/?r=plwd',
            course=self.course,
            owner=self.user
        )

    def get_lesson_url(self, pk):
        return reverse('lesson-detail', kwargs={'pk': pk})

    def test_lesson_full_crud_user(self):
        """Тест полный CRUD list, create, retrieve, update, delete"""
        self.client.force_authenticate(user=self.user)

        # GET список — работает
        response = self.client.get('/api/lessons/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

        # POST создание — полные данные
        create_data = {
            'title': 'New Lesson',
            'description': 'New lesson description',
            'preview': 'lessons/new_lesson.jpg',
            'video_link': 'https://rutube.ru/video/b2a127bfc206b85978150f390156d052/?r=plwd',
            'course': self.course.id
        }
        response = self.client.post('/api/lessons/', create_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_lesson_id = response.data['id']

        # Retrieve
        response = self.client.get(self.get_lesson_url(self.lesson.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Lesson')

        # Update
        update_data = {
            'title': 'Updated Lesson',
            'description': 'Updated desc',
            'preview': 'lessons/update_lesson.jpg',
            'video_link': 'https://rutube.ru/video/b2a127bfc206b85978150f390156d052/?r=plwd',
            'course': self.course.id
        }
        response = self.client.patch(self.get_lesson_url(new_lesson_id), update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Lesson')

        # Delete
        response = self.client.delete(self.get_lesson_url(new_lesson_id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Validation
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
        """Toggle подписки"""
        self.client.force_authenticate(user=self.user)
        """Подписаться"""
        response = self.client.post('/api/courses/subscribe/',
                                    {'course_id': self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка добавлена')
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())
        """Отписаться"""
        response = self.client.post('/api/courses/subscribe/',
                                    {'course_id': self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка удалена')
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_moderator_permissions(self):
        """Тест прав модератора"""
        self.client.force_authenticate(user=self.moderator)

        data = {
            'title': 'Mod Lesson',
            'description': 'Mod desc',
            'preview': 'lessons/mod.jpg',
            'video_link': 'https://vk.com/video_test',
            'course': self.course.id
        }
        """Не может создавать"""
        response = self.client.post('/api/lessons/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        """Может читать"""
        response = self.client.get('/api/lessons/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
