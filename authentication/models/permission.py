import logging

from django.contrib.auth.models import Permission
from django.db import models
from django.utils.translation import gettext_lazy as _

from authentication import settings
from core.models import Base, History, Tracker

logger = logging.getLogger(__name__)


class Permissions(Base, Permission, ):
    inheritance_permission = models.OneToOneField(
        to=Permission,
        on_delete=models.CASCADE,
        parent_link=True,
        primary_key=True,
    )
    tracker = Tracker()
    history = History(
        table_name=u'\"history".\"{}_permission\"'.format(settings.SCHEMA),
        verbose_name=_('Used store history permission'),
        excluded_fields=['modified', ],
    )

    class Meta:
        managed = True
        db_table = u'\"{}\".\"permission\"'.format(settings.SCHEMA)
        verbose_name = _('Used store permission')
        permissions = []

    @property
    def name_translated(self):
        return ' '.join(' '.join([
            _(name)
            .replace('Used', '')
            .replace('Store', '')
            .replace('History', str(_('History')))
            .replace('Can', str(_('Can')))
            .replace('Add', str(_('Add')))
            .replace('Change', str(_('Change')))
            .replace('Delete', str(_('Delete')))
            .replace('View', str(_('View'))) for name in (self.name.title()).split()
        ]).split())
