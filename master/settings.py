
import logging
import sys
from pathlib import Path

from django.conf import settings as djangosettings
from master.apps import ApplicationConfig

DEFAULTS = dict(
    SCHEMA=ApplicationConfig.name,
)

SCHEMA = DEFAULTS["SCHEMA"]
