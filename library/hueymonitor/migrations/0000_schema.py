from django.db import migrations


class Migration(migrations.Migration):
    initial = True

    dependencies = []
    setup_database_sql = """
            CREATE SCHEMA IF NOT EXISTS taskqueue;
        """

    reverse_setup_database_sql = """
            DROP SCHEMA IF EXISTS taskqueue CASCADE;
        """  # noqa

    operations = [
        migrations.RunSQL(
            sql=setup_database_sql,
            reverse_sql=reverse_setup_database_sql
        )
    ]
