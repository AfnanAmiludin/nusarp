import logging

from django.db import models

from core.constants import timezones
from django.conf import settings as djangosettings

logger = logging.getLogger(__name__)


class TimeZoneField(models.CharField):

    def __init__(self, *args, **kwargs):
        defaults = {
            'max_length': 100,
            'default': '' if not djangosettings.TIME_ZONE else djangosettings.TIME_ZONE,
            'choices': timezones.TIMEZONES,
            'blank': True,
        }
        defaults.update(kwargs)
        super(TimeZoneField, self).__init__(*args, **defaults)
