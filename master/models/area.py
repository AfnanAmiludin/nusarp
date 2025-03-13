from django.db import models
from master import settings
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import Base, History, Tracker


class Area(Base, ):
    area_id = models.TextField(
        primary_key=True,
        verbose_name=_('area id'),
        help_text=_('used for area id'),
    )
    area_name = models.TextField(
        null=False,
        verbose_name=_('area name'),
        help_text=_('used for area name'),
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='areadetail',
        help_text="Parent area jika ini adalah area detail.",
        verbose_name="Area"
    )
    status = models.CharField(
        default='draft',
        verbose_name=_('status'),
        help_text=_('Used for status'),
    )
    tracker = Tracker()
    history = History(
        bases=[Base, ],
        table_name=u'\"history".\"{}_area\"'.format(settings.SCHEMA),
        verbose_name=_('Area store history area'),
        excluded_fields=['modified', 'last_activity_date', ],
    )

    class Meta:
        managed = True
        db_table = u'\"{}\".\"area\"'.format(settings.SCHEMA)
        verbose_name = _('Used store area')