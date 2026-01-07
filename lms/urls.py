from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .views import CourseSubscribeAPIView

router = DefaultRouter()
router.register(r"courses", views.CourseViewSet)

urlpatterns = [
    path("lessons/", views.LessonListCreateView.as_view(), name="lesson-list-create"),
    path(
        "lessons/<int:pk>/",
        views.LessonRetrieveUpdateDestroyView.as_view(),
        name="lesson-detail",
    ),
    path("api/", include(router.urls)),
    path('courses/subscribe/', CourseSubscribeAPIView.as_view(), name='course_subscribe'),
]
