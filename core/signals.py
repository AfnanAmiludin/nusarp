from django.db import connection
from django.db.models.signals import pre_migrate
from django.dispatch import receiver
from django.conf import settings

@receiver(pre_migrate)
def create_schema(sender, **kwargs):
    schemas = getattr(settings, "SCHEMA", ["core", "history"])
    with connection.cursor() as cursor:
        for schema in schemas:
            cursor.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema}";')