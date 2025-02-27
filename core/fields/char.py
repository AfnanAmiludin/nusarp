import logging

from django.core import validators
from django.db import models
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class UnlimitedCharField(models.CharField):
    description = _('String with unlimited max_length=None available')

    def __init__(self, *args, db_collation=None, **kwargs):
        models.Field.__init__(self, *args, **kwargs)
        self.db_collation = db_collation
        if self.max_length is not None:
            self.validators.append(validators.MaxLengthValidator(self.max_length))

    def check(self, **kwargs):
        databases = kwargs.get('databases') or []
        return [
            *models.Field.check(self, **kwargs),
            *super()._check_db_collation(databases),
        ]

    def cast_db_type(self, connection):
        return connection.ops.cast_char_field_without_max_length

    def db_type(self, connection):
        return connection.ops.cast_char_field_without_max_length

    def get_internal_type(self):
        return 'UnlimitedCharField'

    def to_python(self, value):
        if isinstance(value, str) or value is None:
            return value
        return str(value)
