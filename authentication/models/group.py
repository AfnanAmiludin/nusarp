import logging

from django.contrib.auth.models import Group
from django.db import models
from django.utils.translation import gettext_lazy as _

from authentication import settings
from core.models import Base, History, Tracker, AdjacencyListTree

logger = logging.getLogger(__name__)


class Groups(AdjacencyListTree, Base, Group, ):
    node_order_by = ['id', ]
    inheritance_group = models.OneToOneField(
        to=Group,
        on_delete=models.CASCADE,
        parent_link=True,
        primary_key=True,
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

    class Meta:
        managed = True
        db_table = u'\"{}\".\"group\"'.format(settings.SCHEMA)
        verbose_name = _('Used store group')
        permissions = [
            ('add_group_permission', _('Can add group permission')),
            ('delete_group_permission', _('Can delete group permission')),
        ]

    def get_children(self):
        return super(Groups, self).get_children().filter(
            parent=self,
            is_removed=False,
        )

    @property
    def has_children(self):
        return len(self.get_children()) > 0


class GroupsPermission(models.Model, ):
    group = models.ForeignKey(
        to=Groups,
        on_delete=models.DO_NOTHING,
    )
    permission = models.ForeignKey(
        to='authentication.Permissions',
        on_delete=models.DO_NOTHING,
    )

    class Meta:
        managed = False
        db_table = u'\"auth_group_permissions\"'.format(settings.SCHEMA)
