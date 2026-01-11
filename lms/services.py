import stripe
from django.conf import settings
from .models import Course

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_product(course: Course):
    """Создание продукта в Stripe"""
    return stripe.Product.create(
        name=course.title,
        description=course.description[:100],
    )


def create_stripe_price(course: Course):
    """Создание цены в Stripe"""
    product = create_stripe_product(course)
    price_cents = int(course.price * 100)

    return stripe.Price.create(
        product=product.id,
        unit_amount=price_cents,
        currency='rub',  # тип валюты
    )


def create_payment_session(course: Course):
    """Создание сессии оплаты"""
    price = create_stripe_price(course)

    return stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': price.id,
            'quantity': 1,
        }],
        mode='payment',
        success_url='http://localhost:8000/success?session_id={CHECKOUT_SESSION_ID}',
        cancel_url='http://localhost:8000/cancel',
    )
