import logging
import inspect
import sys
from pathlib import Path

from django.conf import settings as djangosettings

from core.apps import ApplicationConfig

DEFAULTS = dict(
    SCHEMA=ApplicationConfig.name,
    FIELD_ENCRYPTION_KEYS=[
        'f164ec6bd6fbc4aef5647abc15199da0f9badcc1d2127bde2087ae0d794a9a0b',
    ],
)
FIELD_ENCRYPTION_KEYS = DEFAULTS["FIELD_ENCRYPTION_KEYS"]

SCHEMA = DEFAULTS["SCHEMA"]