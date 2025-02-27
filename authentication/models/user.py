from django.db import models
from authentication import settings
from django.utils.translation import gettext_lazy as _
from datetime import datetime
import logging
from datetime import datetime
from django.db.models import signals, Q
from django.dispatch import receiver
from django.conf import settings as djangosettings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.mail import send_mail
from django.db import models
from django.utils.itercompat import is_iterable
from django.utils.translation import gettext_lazy as _

from authentication import settings
from authentication.managers import UserManager
from core.fields import TimeZoneField, EncryptedCharField
from core.models import Base, History, Tracker

# Create your models here.
class User(Base, AbstractBaseUser, PermissionsMixin, ):
    username_validator = UnicodeUsernameValidator()
    user_id = models.CharField(
        primary_key=True,
        verbose_name=_('user id'),
        help_text=_('Used for identity for signin'),
    )
    user_name = models.CharField(
        unique=True,
        verbose_name=_('user name'),
        help_text=_(
            'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only. '
            'this column alternative identity'
        ),
        validators=[username_validator],
        error_messages={
            'unique': _('A user with that username already exists.'),
        },
    )
    real_name = models.CharField(
        verbose_name=_('real name'),
        help_text=_('Used for view'),
    )
    email = models.EmailField(
        unique=True,
        blank=True,
        verbose_name=_('email address'),
        help_text=_('Used for email and alternative identity'),
    )
    phone = models.CharField(
        unique=True,
        blank=True,
        null=True,
        verbose_name=_('phone'),
        help_text=_('Used for phone and alternative identity'),
    )
    password = EncryptedCharField(
        verbose_name=_('password'),
        help_text=_('Used for store password'),
    )
    avatar = models.CharField(
        blank=True,
        null=True,
        verbose_name=_('avatar'),
        help_text=_('Used for picture'),
    )
    locale = models.CharField(
        default='' if not djangosettings.LANGUAGE_CODE else djangosettings.LANGUAGE_CODE,
        choices=djangosettings.LANGUAGES,
        blank=True,
        null=True,
        verbose_name=_('locale'),
        help_text=_('Used for default language'),
    )
    timezone = TimeZoneField(
        verbose_name=_('timezone'),
        help_text=_('Used for default timezone'),
    )
    last_ip_address = models.CharField(
        blank=True,
        null=True,
        verbose_name=_('last ip address'),
        help_text=_('Used for tracking ip address'),
    )
    last_activity_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('last activity date'),
        help_text=_('Used for tracking activisty date'),
    )
    actived_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('actived date'),
        help_text=_('Used for tracking actived date'),
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
    status = models.CharField(
        default='draft',
        verbose_name=_('status'),
        help_text=_('Used for status'),
    )
    tracker = Tracker()
    history = History(
        bases=[Base, ],
        table_name=u'\"history".\"{}_user\"'.format(settings.SCHEMA),
        verbose_name=_('Used store history user'),
        excluded_fields=['modified', 'last_activity_date', ],
    )

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'user_name'
    REQUIRED_FIELDS = ['user_id', 'email']

    objects = UserManager()

    class Meta:
        managed = True
        db_table = u'\"{}\".\"user\"'.format(settings.SCHEMA)
        verbose_name = _('Used store user')
        permissions = [
            ('add_user_permission', _('Can add user permission')),
            ('delete_user_permission', _('Can delete user permission')),
            ('add_user_group', _('Can add user group')),
            ('delete_user_group', _('Can delete user group')),
            ('change_user_password', _('Can change user password')),
        ]

    def clean(self, ):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self, ):
        full_name = '%s %s' % (self.user_name, self.real_name)
        return full_name.strip()

    def get_short_name(self, ):
        return self.user_name

    def email_user(self, subject, message, from_email=None, **kwargs, ):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def has_anyperms(self, permissions, object=None):
        if not is_iterable(permissions) or isinstance(permissions, str):
            raise ValueError('permissions must be an iterable of permissions.')
        return any(self.has_perm(permission, object) for permission in permissions)

    def groups_derivative(self):
        from authentication.models import Group
        collected = {}

        def collector(group: Group):
            if group is not None:
                if not group.pk in collected:
                    collected.update({group.pk: group, })
                    if group.derivative_permission == Group.DerivativePermission.parent:
                        collector(group.parent)
                    if group.derivative_permission == Group.DerivativePermission.child:
                        for child in group.children_set.all():
                            collector(child)
                    if group.derivative_permission == Group.DerivativePermission.both:
                        collector(group.parent)
                        for child in group.children_set.all():
                            collector(child)

        if self.is_superuser:
            return Group.objects.all()
        for group in Group.objects.filter(pk__in=list(self.groups.values_list('pk', flat=True))):
            collector(group)
        return Group.objects.filter(pk__in=collected.keys())

    def permissions_derivative(self):
        from authentication.models import Permission
        if self.is_superuser:
            return Permission.objects.all()
        return Permission.objects.filter(group__in=self.groups_derivative())

    @property
    def magic(self, ):
        from library.sesame.utils import (get_token, )
        return get_token(self, )

    @property
    def magic_name(self, ):
        from library.sesame.utils import (get_parameters, )
        return get_parameters(self, )

    @property
    def magic_query(self, ):
        from library.sesame.utils import (get_query_string, )
        return get_query_string(self, )



    class Meta:
        managed = True
        db_table = u'\"{}\".\"user\"'.format(settings.SCHEMA)
        verbose_name = _('Used store user')