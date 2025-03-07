import logging
import os

from django.apps import apps
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db import router
from django.db.utils import DEFAULT_DB_ALIAS as DatabaseAlias

from authentication.models import Permission as Permissions
from authentication import settings

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Management command to collect permission'

    def handle(self, *args, **kwargs):
        self.stdout.write(f'''{os.linesep}{self.help}{os.linesep}{os.linesep}''')
        permissions = Permission.objects.all()
        logger.info('Collecting %s permissions', permissions.count())
        for permission in permissions:
            Permissions.objects.get_or_create(
                inheritance_permission=permission,
                defaults=dict(
                    inheritance_permission=permission,
                    name=permission.name,
                    content_type=permission.content_type,
                    codename=permission.codename,
                )
            )
        for model in apps.get_models():
            if not router.allow_migrate_model(DatabaseAlias, model):
                return
            content_type = ContentType.objects.get_for_model(model)
            for default_permission in getattr(settings, 'PERMISSIONS', []):
                if default_permission not in ['undelete', ]:
                    Permissions.objects.get_or_create(
                        content_type=content_type,
                        codename='%s_%s' % (default_permission, model.__name__.lower()),
                        defaults=dict(
                            name='Can %s %s' % (default_permission, model._meta.verbose_name_raw),
                        )
                    )
                from library.simplehistory.models import HistoricalChanges
                if default_permission in ['undelete', ] and hasattr(model, 'all_objects') and HistoricalChanges.__name__.lower() not in (
                    base.__name__.lower() for base in model.__bases__
                ):
                    Permissions.objects.get_or_create(
                        content_type=content_type,
                        codename='%s_%s' % (default_permission, model.__name__.lower()),
                        defaults=dict(
                            name='Can %s %s' % (default_permission, model._meta.verbose_name_raw),
                        )
                    )
        self.stdout.write(f'''Total {len(permissions)} permissions collected''')
