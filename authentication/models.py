from django.db import models
from authentication import settings
from django.utils.translation import gettext_lazy as _
from datetime import datetime

# Create your models here.
class User(models.Model):
    user_id = models.AutoField(
        primary_key=True,
        verbose_name=_('user id'),
        help_text=_('Used for identity for signin'),
    )
    user_name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name=_('user name'),
        help_text=_(
            'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only. '
            'This column is an alternative identity.'
        ),
        error_messages={
            'unique': _('A user with that username already exists.'),
        },
    )
    real_name = models.CharField(
        max_length=255,
        verbose_name=_('real name'),
        help_text=_('Used for display purposes'),
    )
    email = models.EmailField(
        unique=True,
        blank=True,
        verbose_name=_('email address'),
        help_text=_('Used for email and alternative identity'),
    )
    phone = models.CharField(
        max_length=15,
        unique=True,
        blank=True,
        null=True,
        verbose_name=_('phone'),
        help_text=_('Used for phone and alternative identity'),
    )
    password = models.CharField(
        max_length=255,
        verbose_name=_('password'),
        help_text=_('Used to store password'),
    )
    avatar = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('avatar'),
        help_text=_('Used for profile picture'),
    )
    actived_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('activated date'),
        help_text=_('Used for tracking activation date'),
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name=_('staff status'),
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('active'),
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(
        default=datetime.now,
        verbose_name=_('date joined'),
        help_text=_('Used for tracking join date'),
    )

    class Meta:
        managed = True
        db_table = u'\"{}\".\"user\"'.format(settings.SCHEMA)
        verbose_name = _('Used store user')
