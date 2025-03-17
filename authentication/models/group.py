import logging

from django.contrib.auth.models import Group
from django.db import models
from django.utils.translation import gettext_lazy as _

from authentication import settings
from core.models import Base, History, Tracker, SchemaView, Trigrams, FullOptimizer, IndexOptimizer

logger = logging.getLogger(__name__)

class Group(Base):
    group_id = models.CharField(
        primary_key=True,
        verbose_name=_('group id'),
        help_text=_('Used for identity for group'),
    )
    group_name = models.CharField(
        verbose_name=_('group name'),
        help_text=_('Used for view'),
    )
    parent = models.ForeignKey(
        to='self',
        on_delete=models.DO_NOTHING,
        related_name='children_set',
        blank=True,
        null=True,
        verbose_name=_('parent'),
        help_text=_('Used for hierarchy parent id'),
    )
    group_hierarchy = models.CharField(
        verbose_name=_('group hierarchy'),
        help_text=_('Used for hierarchy group'),
        blank=True,
        null=True,
    )
    status = models.CharField(
        default='draft',
        verbose_name=_('status'),
        help_text=_('Used for status'),
    )
    tracker = Tracker()
    history = History(
        bases=[Base, ],
        table_name=u'\"history".\"{}_group\"'.format(settings.SCHEMA),
        verbose_name=_('Used store history group'),
        excluded_fields=['modified', ],
    )
    schema_view = SchemaView(schema='authentication')
    trigrams = Trigrams()
    indexes = IndexOptimizer()

    class Meta:
        managed = True
        db_table = u'\"{}\".\"group\"'.format(settings.SCHEMA)
        verbose_name = _('Used store group')
        permissions = [
            ('add_group_permission', _('Can add group permission')),
            ('delete_group_permission', _('Can delete group permission')),
        ]

    def get_children(self):
        return super(Group, self).get_children().filter(
            parent=self,
            is_removed=False,
        )

    @property
    def has_children(self):
        return len(self.get_children()) > 0


class GroupPermission(models.Model, ):
    group = models.ForeignKey(
        to=Group,
        on_delete=models.DO_NOTHING,
    )
    permission = models.ForeignKey(
        to='authentication.Permissions',
        on_delete=models.DO_NOTHING,
    )

    class Meta:
        managed = False
        db_table = u'\"auth_group_permissions\"'.format(settings.SCHEMA)
