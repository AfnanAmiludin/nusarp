import logging
from collections import namedtuple

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.utils import ShortUUID
from django.conf import settings as djangosettings

logger = logging.getLogger(__name__)

class ShortUUIDField(models.CharField):
    description = _('A short UUID field')

    def __init__(
        self,
        *args,
        **kwargs
    ):
        self.length = kwargs.pop('length', 22)
        self.prefix = kwargs.pop('prefix', '')
        if 'max_length' not in kwargs:
            kwargs['max_length'] = self.length + len(self.prefix)
        self.alphabet = kwargs.pop('alphabet', None)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs['alphabet'] = self.alphabet
        kwargs['length'] = self.length
        kwargs['prefix'] = self.prefix
        return name, path, args, kwargs

    def get_default(self):
        if not hasattr(self, '_default'):
            self._default = self._get_default()
        return self._default

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname, '')
        if add and not len(value) > 0:
            value = self.prefix + ShortUUID(alphabet=self.alphabet).random(
                length=self.length
            )
            logger.debug(f'''Set default value {value} to model {model_instance._meta.db_table.replace('"', '')} field {self.attname}''')
            setattr(model_instance, self.attname, value)
        else:
            logger.debug(f'''Model {model_instance._meta.db_table.replace('"', '')} field {self.attname} with value {value}''')
        return value
