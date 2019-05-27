import re

from django.core.exceptions import ValidationError


LANGUAGE_PATTERN = re.compile('[a-z]{2}_[A-Z]{2}')


def validate_language_code(value):
    if not LANGUAGE_PATTERN.match(value):
        raise ValidationError(
            '"{}" is not a valid language code!'.format(value)
        )


def validate_language_code_list(value):
    if value == '':
        return

    codes = value.split(',')
    for code in codes:
        validate_language_code(code)
