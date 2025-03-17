
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class ApplicationConfig(AppConfig):
    name = 'warehouse'
    verbose_name = _('Application')

    def ready(self):
        import warehouse.signals
