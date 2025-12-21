from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny, SAFE_METHODS, IsAuthenticated
from users.permissions import IsModer, IsOwner
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer


# ViewSet для курсов
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.action in SAFE_METHODS:
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update']:  # Редактирование
            return [IsAuthenticated & (IsModer | IsOwner)]  # Только модераторы или владельцы
        elif self.action == 'destroy':
            return [IsOwner()]  # Удалить разрешено только владельцу
        elif self.action == 'create':
            return [IsAuthenticated & ~IsModer]
        return [IsAuthenticated()]

# Generics для уроков
class LessonListCreateView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated & ~IsModer]  # Создание, кроме модераторов

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated & (IsModer | IsOwner)]  #Редактирование, удаление — модераторы или владельцы
