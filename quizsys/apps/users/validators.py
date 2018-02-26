import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_no_space(value):
    if re.search("\s", value):
        raise ValidationError(
            _('%(value)s should not contain spaces'),
            params={'value': value},
        )