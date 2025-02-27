from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class ApplicationConfig(AppConfig):
    name = 'core'
    verbose_name = _('Core')
    def ready(self):
        import core.signals