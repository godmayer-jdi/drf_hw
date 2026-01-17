from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import CustomUser, Payment

User = get_user_model()


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ["payment_date"]


class PaymentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    payments = PaymentListSerializer(source="payment_set", many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "phone", "city", "avatar", "payments"]


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "phone", "city"]

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            phone=validated_data.get("phone", ""),
            city=validated_data.get("city", ""),
        )
        return user
