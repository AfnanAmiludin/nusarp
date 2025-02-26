
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class ApplicationConfig(AppConfig):
    name = 'inventory'
    verbose_name = _('Application')

    def ready(self):
        import inventory.signals
