"""
Модуль, содержащий функции для валидации данных.

Этот модуль содержит функции для валидации данных,
используемые в приложении отзывов.
"""
from datetime import date
import re

from django.core.exceptions import ValidationError

from .constants import ME


def validate_year(value):
    """
    Проверка правильности введенного года.

    Функция проверяет, является ли значение года четырехзначным числом
    и не превышает ли оно текущий год.
    """
    if len(str(value)) != 4 or not isinstance(value, int):
        raise ValidationError("Дата введена неправильно, введите 4 цифры.")
    elif value > date.today().year:
        raise ValidationError("Год не может быть больше текущего.")


def validate_username(username):
    """
    Проверка правильности введенного года.

    Функция проверяет имя пользователя.
    """
    if username == ME:
        raise ValidationError(
            f'Использовать имя {ME} в качестве username запрещено!'
        )
    non_matching_chars = [char for char in username if not re.match(
        r'^[\w.@+-]+$', char
    )]
    if non_matching_chars:
        raise ValidationError(
            f'Содержимое поля \'username\' не '
            'соответствует паттерну ^[\\w.@+-]+\\Z$, '
            f'а именно содержит {non_matching_chars}'
        )
    return username
