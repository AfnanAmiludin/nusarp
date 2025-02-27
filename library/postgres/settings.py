import logging
import sys

from django.conf import settings as djangosettings

logger = logging.getLogger(__name__)

DEFAULTS = dict(
    SCHEMA='postgres',
)
__all__ = list(DEFAULTS)


def load():
    module = sys.modules[__name__]
    for name, default in DEFAULTS.items():
        setattr(module, name, getattr(djangosettings, 'postgres'.upper(), {}).get(name, default))


load()
