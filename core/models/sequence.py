import logging

from django.conf import settings as djangosettings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

from core import settings
from core.fields import ShortUUIDField
from core.models import History, Tracker
from core.models.base import (
    Base,
    TimeStamped,
)

logger = logging.getLogger(__name__)

try:
    from django.contrib.auth import get_user_model

    User = get_user_model()
except:
    User = djangosettings.AUTH_USER_MODEL


class Sequence(Base, ):
    sequence_id = ShortUUIDField(
        length=25,
        primary_key=True,
        verbose_name=_('sequence id'),
        help_text=_('Used for identity'),
    )
    content_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE,
        verbose_name=_('content type'),
        help_text=_('Used for linked key model comment'),
    )
    part = models.CharField(
        verbose_name=_('part'),
        help_text=_('Used for identity part'),
    )
    length = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('length'),
        help_text=_('Used for length character number'),
    )
    prefix = models.CharField(
        blank=True,
        null=True,
        verbose_name=_('prefix'),
        help_text=_('Used for prefix number'),
    )
    suffix = models.CharField(
        blank=True,
        null=True,
        verbose_name=_('suffix'),
        help_text=_('Used for suffix number'),
    )
    repeater = models.CharField(
        blank=True,
        null=True,
        verbose_name=_('repeater'),
        help_text='Used for repeater character before after prefix before current number',
    )
    counter = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('counter'),
        help_text='Used for increment',
    )
    tracker = Tracker()
    history = History(
        bases=[Base, ],
        table_name=u'\"history".\"{}_sequence\"'.format(settings.SCHEMA),
        verbose_name=_('Used store history sequence'),
        excluded_fields=['modified', ],
    )

    class Meta:
        managed = True
        db_table = u'\"{}\".\"sequence\"'.format(settings.SCHEMA)
        verbose_name = _('Used store sequence auto numbering')


class SequenceData(TimeStamped, ):
    id = ShortUUIDField(
        length=25,
        primary_key=True,
        verbose_name=_('sequence data id'),
        help_text=_('Used for identity'),
    )
    sequence = models.ForeignKey(
        to=Sequence,
        on_delete=models.DO_NOTHING,
        related_name='%(app_label)s_%(class)s',
        verbose_name=_('sequence'),
        help_text=_('Used for linked key'),
    )
    part = models.CharField(
        verbose_name=_('part'),
        help_text=_('Used for identity part'),
    )
    current = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('current'),
    )
    tracker = Tracker()
    history = History(
        table_name=u'\"history".\"{}_sequence_data\"'.format(settings.SCHEMA),
        verbose_name=_('Used store history sequence data'),
        excluded_fields=['modified', ],
    )

    class Meta:
        managed = True
        db_table = u'\"{}\".\"sequence_data\"'.format(settings.SCHEMA)
        unique_together = (('sequence', 'part',),)
        verbose_name = 'Used store sequence auto numbering data after formated'


class SequenceNumber(TimeStamped, ):
    id = ShortUUIDField(
        length=25,
        primary_key=True,
        verbose_name=_('sequence data id'),
        help_text=_('Used for identity'),
    )
    sequence = models.ForeignKey(
        to=Sequence,
        on_delete=models.DO_NOTHING,
        related_name='%(app_label)s_%(class)s',
        verbose_name=_('sequence'),
        help_text=_('Used for linked key'),
    )
    part = models.CharField(
        verbose_name=_('part'),
        help_text=_('Used for identity part'),
    )
    owner = models.ForeignKey(
        to=User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_('owner'),
        help_text=_('Used for linked key owner number'),
    )
    number = models.CharField(
        blank=True,
        null=True,
        verbose_name=_('number'),
    )

    tracker = Tracker()
    history = History(
        table_name=u'\"history".\"{}_sequence_number\"'.format(settings.SCHEMA),
        verbose_name=_('Used store history sequence number'),
        excluded_fields=['modified', ],
    )

    class Meta:
        managed = True
        db_table = u'\"{}\".\"sequence_number\"'.format(settings.SCHEMA)
        unique_together = (('sequence', 'part', 'owner',),)
        verbose_name = 'Used store sequence auto numbering current number'

    @property
    def content_object(self):
        return self.sequence.content_type.model_class().objects.get(pk=self.number)
