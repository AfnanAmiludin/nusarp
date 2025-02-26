import logging
import sys
from pathlib import Path

from django.conf import settings as djangosettings

from authentication.apps import ApplicationConfig

DEFAULTS = dict(
    SCHEMA=ApplicationConfig.name,
)
__all__ = list(DEFAULTS)
