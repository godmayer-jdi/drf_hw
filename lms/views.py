from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny, SAFE_METHODS, IsAuthenticated
from users.permissions import IsModer
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer


# ViewSet для курсов
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.action in SAFE_METHODS:
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update']:  # Редактирование
            return [IsAuthenticated & IsModer]  # Только модераторы
        else:
            return [IsAuthenticated & ~IsModer]  # Только обычные пользователи

# Generics для уроков
class LessonListCreateView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated & ~IsModer]  # Создание, кроме модераторов

class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated & IsModer]  #Редактирование, удаление — модераторы
