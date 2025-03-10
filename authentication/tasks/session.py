import logging

from django.contrib.sessions.models import Session
from django.utils import timezone
from huey import crontab

import library.djangohuey as huey
from authentication.models import TokenOutstanding, Token, TokenBlackListed
from library.cacheops import invalidate_model

logger = logging.getLogger(__name__)


@huey.db_periodic_task(crontab(minute='*/30'), retry_delay=60 * 5, name='Process Flush Session Task', queue='core', )
def process_flush():
    for session in Session.objects.filter(
        expire_date__lte=timezone.now(),
    ):
        session.delete()
    for token in Token.objects.filter(
        expires_at__lte=timezone.now(),
    ):
        token.delete()
    TokenOutstanding.objects.filter(
        expires_at__lte=timezone.now(),
    ).delete()
    invalidate_model(Token)
    invalidate_model(TokenOutstanding)
    invalidate_model(TokenBlackListed)
