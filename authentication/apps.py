from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class ApplicationConfig(AppConfig):
    name = 'authentication'
    verbose_name = _('Authentication')
    def ready(self):
        import authentication.signals