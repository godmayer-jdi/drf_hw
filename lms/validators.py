import re
from urllib.parse import urlparse

from rest_framework import serializers


def validate_rutube_link(value):
    """
    Проверяет, что ссылка ведет только на rutube.com
    """
    if not value:
        return value

    rutube_domains = ["rutube.ru", "www.rutube.ru"]
    parsed_url = urlparse(value)

    if parsed_url.netloc not in rutube_domains:
        raise serializers.ValidationError("Разрешены только ссылки на RuTube (rutube.ru)")

    # Дополнительная проверка на валидность YouTube URL
    rutube_regex = r"(https?://)?(www\.)?rutube\.ru/(video|figure)/[\w-]+"
    if not re.match(rutube_regex, value):
        raise serializers.ValidationError("Некорректный формат ссылки Rutube")

    return value
