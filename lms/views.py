from rest_framework import generics, viewsets, status
from rest_framework.permissions import AllowAny, SAFE_METHODS, IsAuthenticated
from users.permissions import IsModer, IsOwner
from .models import Course, Lesson, Subscription
from .serializers import CourseSerializer, LessonSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .paginators import LMSPagination # Отменены после применения общего пагинатора - CoursePagination, LessonPagination


# ViewSet для курсов
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = LMSPagination  # Пагинация
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.action in SAFE_METHODS:
            return [IsAuthenticated()]
        elif self.action in ["update", "partial_update"]:  # Редактирование
            return [IsAuthenticated & (IsModer | IsOwner)]  # Только модераторы или владельцы
        elif self.action == "destroy":
            return [IsOwner()]  # Удалить разрешено только владельцу
        elif self.action == "create":
            return [IsAuthenticated & ~IsModer]
        return [IsAuthenticated()]


# Generics для уроков
class LessonListCreateView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = LMSPagination  # Пагинация
    permission_classes = [IsAuthenticated & ~IsModer]  # Создание, кроме модераторов

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated & (IsModer | IsOwner)]  # Редактирование, удаление — модераторы или владельцы


class CourseSubscribeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        course_id = request.data.get('course_id')
        course = get_object_or_404(Course, id=course_id)

        # Toggle логика
        subscription = Subscription.objects.filter(
            user=request.user,
            course=course
        )

        if subscription.exists():
            subscription.delete()
            message = 'Подписка удалена'
        else:
            Subscription.objects.create(user=request.user, course=course)
            message = 'Подписка добавлена'

        return Response({"message": message}, status=status.HTTP_200_OK)
