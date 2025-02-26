
import logging
import sys
from pathlib import Path

from django.conf import settings as djangosettings
from inventory.apps import ApplicationConfig

DEFAULTS = dict(
    SCHEMA=ApplicationConfig.name,
)

SCHEMA = DEFAULTS["SCHEMA"]
