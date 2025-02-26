# Generated by Django 4.0.6 on 2022-08-05 21:25

import core.patch.fields
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('hueymonitor', '0000_schema'),
    ]

    operations = [
        migrations.CreateModel(
            name='SignalInfoModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('hostname', models.CharField(help_text='Hostname of the machine that creates this Signal', max_length=128, verbose_name='Hostname')),
                ('pid', models.PositiveIntegerField(help_text='Process ID that creates this Signal', verbose_name='PID')),
                ('thread', models.CharField(help_text='Name of the thread that creates this Signal', max_length=128, verbose_name='Thread Name')),
                ('signal_name', models.CharField(help_text='Name of the signal', max_length=128, verbose_name='Signal Name')),
                ('exception_line', models.TextField(blank=True, max_length=128, verbose_name='Exception Line')),
                ('exception', models.TextField(blank=True, help_text='Full information of a exception', null=True, verbose_name='Exception')),
                ('progress_count', models.PositiveIntegerField(blank=True, help_text='Progress (if any) at the time of creation.', null=True, verbose_name='Progress Count')),
                ('create_dt', core.patch.fields.DateTimeWithautTZField(auto_now_add=True, help_text='(will be set automatically)', verbose_name='Create date')),
            ],
            options={
                'verbose_name': 'Task Signal',
                'verbose_name_plural': 'Task Signals',
                'db_table': '"taskqueue"."task_signal"',
            },
        ),
        migrations.CreateModel(
            name='TaskModel',
            fields=[
                ('create_dt', core.patch.fields.DateTimeWithautTZField(blank=True, editable=False, help_text='ModelTimetrackingMixin.create_dt.help_text', null=True, verbose_name='ModelTimetrackingMixin.create_dt.verbose_name')),
                ('update_dt', core.patch.fields.DateTimeWithautTZField(blank=True, editable=False, help_text='ModelTimetrackingMixin.update_dt.help_text', null=True, verbose_name='ModelTimetrackingMixin.update_dt.verbose_name')),
                ('task_id', models.UUIDField(help_text='The UUID of the Huey-Task', primary_key=True, serialize=False, verbose_name='Task UUID')),
                ('name', models.CharField(max_length=128, verbose_name='Task name')),
                ('finished', models.BooleanField(default=False, help_text='Indicates that this Task no longer waits or run. (It does not mean that execution was successfully completed.)', verbose_name='Finished')),
                ('desc', models.CharField(blank=True, default='', help_text='Prefix for progress information', max_length=128, verbose_name='Description')),
                ('total', models.PositiveIntegerField(blank=True, help_text='The number of expected iterations', null=True)),
                ('progress_count', models.PositiveIntegerField(blank=True, help_text='Number of units processed (If provided)', null=True, verbose_name='Progress Count')),
                ('cumulate_progress', models.BooleanField(default=True, help_text='Should the progress of the sub tasks be added up and saved in the parent task? (Will be done after the task has ended)', verbose_name='Cumulate Progress?')),
                ('unit', models.CharField(default='it', help_text='String that will be used to define the unit of each iteration', max_length=64)),
                ('unit_divisor', models.PositiveIntegerField(default=1000, help_text='Used to convert the units.')),
                ('parent_task', models.ForeignKey(blank=True, editable=False, help_text='Only set if this task is a sub task started from his parent.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='hueymonitor.taskmodel', verbose_name='Parent Task')),
                ('state', models.ForeignKey(blank=True, help_text='Last Signal information', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='hueymonitor.signalinfomodel', verbose_name='State')),
            ],
            options={
                'verbose_name': 'Task',
                'verbose_name_plural': 'Tasks',
                'db_table': '"taskqueue"."task"',
            },
        ),
        migrations.AddField(
            model_name='signalinfomodel',
            name='task',
            field=models.ForeignKey(help_text='The Task instance for this Signal Info entry.', on_delete=django.db.models.deletion.CASCADE, related_name='signals', to='hueymonitor.taskmodel', verbose_name='Task'),
        ),
    ]
