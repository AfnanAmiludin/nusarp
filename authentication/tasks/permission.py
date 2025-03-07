import logging

from django.conf import settings as djangosettings
from django.core import management
from django.utils import formats
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import library.djangohuey as huey
from authentication.management.commands import collectpermission
from core.models import Notification, Icon
from library import timeago

logger = logging.getLogger(__name__)


@huey.db_task(name='Process Collect Permission Task', queue='core', )
def process_collect(user, ):
    begin = timezone.now()
    management.call_command(collectpermission.Command(), )
    end = timezone.now()
    duration = end - begin
    Notification.objects.create(
        notification_name=_('Permission Collect'),
        platform=Notification.Platform.erpro,
        content=_(u'Permission data %(count)s have been successfully collected <br/>Started %(ago)s <br/>Finished in %(delta)s') % dict(
            count=formats.localize(Icon.objects.count(), use_l10n=True),
            ago=timeago.format(duration, locale=user.locale or djangosettings.LANGUAGE_CODE, ),
            delta=str(duration),
        ),
        toast=True,
        icon=Notification.Icon.info,
        owner=user,
    )
