from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'courses', views.CourseViewSet)

urlpatterns = [
    path('lessons/', views.LessonListCreateView.as_view(), name='lesson-list-create'),
    path('lessons/<int:pk>/', views.LessonRetrieveUpdateDestroyView.as_view(), name='lesson-detail'),
    path('api/', include(router.urls)),
]
