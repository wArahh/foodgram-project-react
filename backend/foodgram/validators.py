import re

from django.conf import settings
from rest_framework.exceptions import ValidationError

BAD_USERNAME = (
    'Неверный формат имени. '
    'Запрещенные символы: {characters}'
)


def username_validator(username):
    bad_characters = re.sub(
        settings.USERNAME_PATTERN, '', username
    )
    if bad_characters:
        raise ValidationError(
            BAD_USERNAME.format(
                characters=bad_characters
            )
        )
    return username
