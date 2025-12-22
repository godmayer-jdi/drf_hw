import re
from rest_framework import serializers
from urllib.parse import urlparse


def validate_youtube_link(value):
    """
    Проверяет, что ссылка ведет только на youtube.com
    """
    if not value:
        return value

    youtube_domains = ['youtube.com', 'youtu.be', 'www.youtube.com']
    parsed_url = urlparse(value)

    if parsed_url.netloc not in youtube_domains:
        raise serializers.ValidationError(
            'Разрешены только ссылки на YouTube (youtube.com, youtu.be)'
        )

    # Дополнительная проверка на валидность YouTube URL
    youtube_regex = r'(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]+'
    if not re.match(youtube_regex, value):
        raise serializers.ValidationError('Некорректный формат ссылки YouTube')

    return value
