# Generated by Django 4.2.4 on 2023-10-06 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hueymonitor', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='signalinfomodel',
            name='create_dt',
            field=models.DateTimeField(auto_now_add=True, help_text='(will be set automatically)', verbose_name='Create date'),
        ),
        migrations.AlterField(
            model_name='taskmodel',
            name='create_dt',
            field=models.DateTimeField(blank=True, editable=False, help_text='ModelTimetrackingMixin.create_dt.help_text', null=True, verbose_name='ModelTimetrackingMixin.create_dt.verbose_name'),
        ),
        migrations.AlterField(
            model_name='taskmodel',
            name='update_dt',
            field=models.DateTimeField(blank=True, editable=False, help_text='ModelTimetrackingMixin.update_dt.help_text', null=True, verbose_name='ModelTimetrackingMixin.update_dt.verbose_name'),
        ),
    ]
