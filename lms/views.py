import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status, viewsets
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import Payment
from users.permissions import IsModer, IsOwner

from .models import Course, Lesson, Subscription
from .paginators import \
    LMSPagination  # Отменены после применения общего пагинатора - CoursePagination, LessonPagination
from .serializers import CourseSerializer, LessonSerializer
from .services import create_payment_session

stripe.api_key = settings.STRIPE_SECRET_KEY


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

    @swagger_auto_schema(
        operation_description="Получить список уроков или создать новый",
        responses={200: LessonSerializer(many=True), 201: LessonSerializer, 400: "Ошибки валидации"},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Создать урок (только не-модераторы)",
        request_body=LessonSerializer,
        responses={201: LessonSerializer, 400: "Ошибки валидации", 403: "Нет прав"},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated & (IsModer | IsOwner)]  # Редактирование, удаление — модераторы или владельцы

    @swagger_auto_schema(
        operation_description="Уроки: просмотр, редактирование, удаление",
        responses={200: LessonSerializer, 204: "Удален", 403: "Нет прав", 404: "Не найден"},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CourseSubscribeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Подписка/отписка от курса (toggle)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"course_id": openapi.Schema(type=openapi.TYPE_INTEGER)},
            required=["course_id"],
        ),
        responses={
            200: openapi.Response(
                "Успех",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT, properties={"message": openapi.Schema(type=openapi.TYPE_STRING)}
                ),
            )
        },
    )
    def post(self, request):
        course_id = request.data.get("course_id")
        course = get_object_or_404(Course, id=course_id)

        # Toggle логика
        subscription = Subscription.objects.filter(user=request.user, course=course)

        if subscription.exists():
            subscription.delete()
            message = "Подписка удалена"
        else:
            Subscription.objects.create(user=request.user, course=course)
            message = "Подписка добавлена"

        return Response({"message": message}, status=status.HTTP_200_OK)


class CoursePaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Оплата курса через Stripe",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"course_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="ID курса")},
            required=["course_id"],
        ),
        responses={
            200: openapi.Response(
                "Ссылка на оплату",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "session_id": openapi.Schema(type=openapi.TYPE_STRING),
                        "url": openapi.Schema(type=openapi.TYPE_STRING),
                        "payment_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                    },
                ),
            ),
            400: "Курс не найден или бесплатный",
        },
    )
    def post(self, request):
        course_id = request.data.get("course_id")
        course = get_object_or_404(Course, id=course_id)

        if course.price <= 0:
            return Response({"error": "Курс бесплатный"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            """Создание записи платежа перед Stripe"""
            payment = Payment.objects.create(
                user=request.user,
                paid_course=course,
                amount=course.price,
                payment_method="stripe",
                stripe_status="pending",
            )

            """ Stripe сессия с payment """
            stripe_data = create_payment_session(course, payment)

            """ Сохраняем данные Stripe в БД """
            payment.stripe_session_id = stripe_data["session_id"]
            payment.stripe_payment_url = stripe_data["payment_url"]
            payment.stripe_status = stripe_data["status"]
            payment.save()

            return Response(
                {"session_id": stripe_data["session_id"], "url": stripe_data["payment_url"], "payment_id": payment.id},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


""" Проверка статуса """


class PaymentStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Проверка статуса платежа Stripe",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"payment_id": openapi.Schema(type=openapi.TYPE_INTEGER)},
            required=["payment_id"],
        ),
        responses={
            200: openapi.Response(
                "Статус платежа",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "payment_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "status": openapi.Schema(type=openapi.TYPE_STRING),
                        "amount": openapi.Schema(type=openapi.TYPE_NUMBER),
                    },
                ),
            ),
            400: "Платеж не найден или нет Stripe данных",
            403: "Нет доступа к чужому платежу",
        },
    )
    def post(self, request):
        payment_id = request.data.get("payment_id")
        payment = get_object_or_404(Payment, id=payment_id, user=request.user)

        if payment.payment_method != "stripe" or not payment.stripe_session_id:
            return Response({"error": "Нет данных Stripe"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            """Запрос в Stripe"""
            stripe_session = stripe.checkout.Session.retrieve(payment.stripe_session_id)

            """ Обновление статуса """
            payment.stripe_status = stripe_session.payment_status
            payment.save()

            return Response(
                {
                    "payment_id": payment.id,
                    "status": stripe_session.payment_status,
                    "amount": float(payment.amount),
                    "url": payment.stripe_payment_url,
                }
            )
        except stripe.error.StripeError as e:
            return Response({"error": f"Stripe: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
