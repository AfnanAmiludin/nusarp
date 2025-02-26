from django.db import models
from authentication import settings

# Create your models here.
class User(Base, AbstractBaseUser, PermissionsMixin, ):
    username_validator = UnicodeUsernameValidator()
    user_id = IdentifierField(
        primary_key=True,
        company=None,
        prefix='USR',
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

    class Meta:
        managed = True
        db_table = u'\"{}\".\"user\"'.format(settings.SCHEMA)
        verbose_name = _('Used store user')
