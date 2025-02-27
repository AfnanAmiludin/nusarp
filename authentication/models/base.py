import copy
import logging
from datetime import timedelta

from django.db import (
    models,
    transaction,
)
from django.db.models.functions import Now
from django.utils import timezone
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

from authentication.utils import stringcase
from library.modelutils import (
    FieldTracker as Tracker,
    Choices,
)
from library.modelutils.fields import MonitorField
from library.modelutils.models import (
    TimeStampedModel as TimeStamped,
    SoftDeletableModel as SoftDeletable,
)
from library.simplehistory.models import HistoricalRecords
from library.treebeard.al_tree import AL_Node
from library.treebeard.mp_tree import MP_Node
from library.treebeard.ns_tree import NS_Node
from library.organizations.abstract import (
    AbstractOrganization as BaseOrganization,
    AbstractOrganizationInvitation as BaseOrganizationInvitation,
    AbstractOrganizationOwner as BaseOrganizationOwner,
    AbstractOrganizationUser as BaseOrganizationUser,
)

logger = logging.getLogger(__name__)


class AdjacencyListTree(AL_Node, ):
    class Meta(AL_Node.Meta, ):
        abstract = True


class MaterializedPathTree(MP_Node, ):
    class Meta(MP_Node.Meta, ):
        abstract = True


class NestedSetTree(NS_Node, ):
    class Meta(NS_Node.Meta, ):
        abstract = True


__all__: [
    Tracker,
    MonitorField,
    AdjacencyListTree,
    MaterializedPathTree,
    NestedSetTree,
    BaseOrganization,
    BaseOrganizationInvitation,
    BaseOrganizationOwner,
    BaseOrganizationUser,
]


class History(HistoricalRecords):
    pass


class Base64:
    @staticmethod
    def encode(string):
        import base64
        encoded = base64.urlsafe_b64encode(string.encode())
        return encoded.rstrip(b'=').decode()

    @staticmethod
    def decode(string):
        import base64
        padding = 4 - (len(string) % 4)
        string = string + ('=' * padding)
        return base64.urlsafe_b64decode(string).decode()


class Base64PkDecodeError(Exception):
    def __init__(self, msg='Failed to decrypt hex, invalid input.'):
        super(Base64PkDecodeError, self).__init__(msg)


class Base64PkManager(models.Manager):
    def get(self, base64pk, **kwargs):
        return self.get(pk=Base64.decode(base64pk), **kwargs)


class Base64PkQuerySet(models.QuerySet):
    def filter(self, *args, **kwargs):
        if 'base64pk' in kwargs:
            base64pk = kwargs.pop('base64pk')
            try:
                assert base64pk is not None
                kwargs['pk'] = Base64.decode(base64pk)
            except (AssertionError, Base64PkDecodeError) as e:
                logger.debug(e)
                return self.none()
        return super(Base64PkQuerySet, self).filter(*args, **kwargs)


class Base64PkModel(models.Model):
    class Meta:
        abstract = True

    hexobjects = Base64PkManager.from_queryset(Base64PkQuerySet)()

    @property
    def base64pk(self):
        if isinstance(self._meta.pk, (models.IntegerField, models.AutoField, models.SmallAutoField, models.BigIntegerField, models.BigAutoField,)):
            return Base64.encode(str(self.pk))
        return Base64.encode(self.pk)


class Base64PkConverter:
    name = 'base64pk'
    regex = '[^/]+'

    def to_python(self, value):
        return Base64.decode(value)

    def to_url(self, value):
        return Base64.encode(value)


class BaseStatus(object):
    Status = Choices(
        ('draft', _('Draft')),
        ('published', _('Published')),
        ('approved', _('Approved')),
        ('canceled', _('Canceled')),
    )


class Base(BaseStatus, TimeStamped, SoftDeletable, Base64PkModel, ):
    read_only = models.BooleanField(
        default=False,
        verbose_name=_('read only'),
        help_text=_('Used for disable modification'),
    )
    enable = models.BooleanField(
        default=False,
        verbose_name=_('enable'),
        help_text=_('Used for usable'),
    )
    properties = models.JSONField(
        default=dict,
        verbose_name=_('properties'),
        help_text=_('Used for other field value'),
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('description'),
        help_text=_('Used for remark'),
    )

    class Meta:
        abstract = True


class TemporaryObjectDescriptor:
    def __init__(self, temporary_model, manager_factory, ):
        self.temporary_model = temporary_model
        self.manager_factory = manager_factory

    def __get__(self, instance, owner, ):
        if instance is not None:
            from core.fields import (IdentifierField, ShortUUIDField, CreatedField, LastModifiedField, )
            values = {
                field.attname: getattr(instance, field.attname)
                for field in self.temporary_model.wrapped_model._meta.local_concrete_fields
                if not isinstance(field, (models.AutoField, IdentifierField, ShortUUIDField, CreatedField, LastModifiedField,))
            }
            return self.temporary_model(**values, )

        return self.manager_factory(self.temporary_model, )


class TemporaryObjectManager(models.Manager):
    def __init__(self, temporary_model, ):
        super().__init__()
        self.model = temporary_model
        self.wrapped_model = temporary_model.wrapped_model

    def get_queryset(self, ):
        queryset = super().get_queryset()
        if not self.model._temporary_expired:
            return queryset
        return queryset.filter(temporary_expired__gte=Now(), )

    def purge_expired(self, ):
        if not self.model._temporary_expired:
            raise TypeError(_('State model does not use expiry timestamps.'))
        queryset = super().get_queryset().filter(temporary_expired__lt=Now(), )
        return queryset.delete()

    def by_temporary_id(self, temporary_id, ):
        return self.get_queryset().get(temporary_id=temporary_id, )

    def by_true_pk(self, pk, ):
        return self.get_queryset().filter(**{self.wrapped_model._meta.pk.attname: pk, }, ).latest()


class TemporaryMixin:
    def post_commit_cleanup(self, ):
        self.delete()

    def wrap(self, populate_relations=False, ):
        model = self.wrapped_model

        def value():
            from django.contrib.contenttypes.fields import GenericForeignKey
            from core.fields import (IdentifierField, ShortUUIDField, CreatedField, LastModifiedField, )
            values = []
            childrens = {}
            for field in model._meta.get_fields(include_parents=False, ):
                if isinstance(field, (GenericForeignKey, models.AutoField, IdentifierField, ShortUUIDField, CreatedField, LastModifiedField,)):
                    continue
                if isinstance(field, (models.ManyToOneRel,)):
                    childrens.update({field.name: (field.name,)})
                    continue
                attribute = getattr(self, getattr(field, 'attname', field.name))
                if populate_relations and field.is_relation:
                    values.append((field.attname, field.remote_field.model._base_manager.get(pk=attribute, ),))
                else:
                    values.append((field.attname, attribute,))
            for index, field in enumerate([
                field
                for field in self._meta.get_fields(include_parents=False, )
                if isinstance(field, (models.ManyToOneRel,))
            ]):
                childrens.update({field.name.replace('_temporary', '_'): (field.name.replace('_temporary', '_'), getattr(self, field.name).all(),)})
            return values, list(childrens.values())

        value, childrens = value()
        object = model(**dict(value))
        return object, childrens

    def commit(self, ):
        def recursive(wrapped, childrens, ):
            for children in childrens:
                try:
                    field, children = children
                except ValueError as e:
                    logger.debug(e)
                    field, children = children, []
                for child in children:
                    wrapped_detail, childrens_detail = child.wrap(populate_relations=False, )
                    wrapped_detail.clean()
                    getattr(wrapped, field).add(wrapped_detail, bulk=False, )
                    if len(childrens_detail) > 0:
                        recursive(wrapped_detail, childrens_detail, )
                    child.post_commit_cleanup()

        wrapped, childrens = self.wrap(populate_relations=False, )
        wrapped.clean()
        connection = transaction.get_connection()

        def callback():
            if len(self.wrapped_model._meta.parents) > 0:
                wrapped.save_base(force_insert=True, raw=True, )
            else:
                wrapped.save(force_insert=True, )
            recursive(wrapped, childrens, )
            self.post_commit_cleanup()

        if connection.in_atomic_block:
            callback()
        else:
            with transaction.atomic():
                callback()
        return wrapped


@deconstructible
class ExpiryDefault:
    def __init__(self, lifetime, ):
        self.lifetime = lifetime

    def __call__(self, ):
        return timezone.now() + self.lifetime


class TemporaryRecords:
    def __init__(
        self,
        temporary_lifetime=None,
        db_table=None,
        verbose_name=None,
        extra_fields=None,
        mapping_parents=None,
        mixin_base=TemporaryMixin,
        manager_factory=TemporaryObjectManager,
    ):
        if extra_fields is None:
            extra_fields = []
        if mapping_parents is None:
            mapping_parents = []
        self.temporary_lifetime: timedelta = temporary_lifetime
        self.db_table = db_table
        self.verbose_name = verbose_name
        self.extra_fields = extra_fields
        self.mapping_parents = mapping_parents
        self.mixin_base = mixin_base
        self.temporary_descriptor_name = None
        self.manager_factory = manager_factory

    def contribute_to_class(self, clazz, name, ):
        self.temporary_descriptor_name = name
        models.signals.class_prepared.connect(self.finalize, sender=clazz, )

    def finalize(self, sender, **kwargs, ):
        setattr(sender, self.temporary_descriptor_name, TemporaryObjectDescriptor(self.create_temporary_model(sender, ), self.manager_factory, ))

    def create_temporary_model(self, model, ):
        attrs = {
            field.name: field
            for field in self.copy_fields(model, )
        }
        attrs['__module__'] = model.__module__
        attrs['wrapped_model'] = model
        attrs['_temporary_expired'] = self.temporary_lifetime is not None
        attrs.update(self.temporary_model_extra_fields())
        attrs.update(Meta=type('Meta', (), self.temporary_model_meta_options(model, )))
        return type(f'Temporary{model._meta.object_name}', (models.Model, self.mixin_base), attrs)

    def copy_fields(self, model, ):
        from core.fields import (IdentifierField, ShortUUIDField, StatusField, CreatedField, LastModifiedField, )
        fields = []
        mapping = dict(self.mapping_parents)
        for field in model._meta.local_concrete_fields:
            if isinstance(field, (models.ManyToManyField, models.AutoField, CreatedField, LastModifiedField,)):
                continue
            field = copy.copy(field)
            if isinstance(field, (IdentifierField, ShortUUIDField, StatusField,)):
                field = models.CharField(
                    name=field.name,
                    null=True,
                )
            if field.primary_key:
                field.primary_key = False
            else:
                field.null = True
            if isinstance(field, models.ForeignKey, ):
                swappable = field.swappable
                field.swappable = False
                try:
                    name, path, args, kwargs = field.deconstruct()
                finally:
                    field.swappable = swappable
                field_type = type(field)
                if isinstance(field, models.OneToOneField, ):
                    field_type = models.ForeignKey
                kwargs.update(
                    serialize=True,
                    auto_created=False,
                    parent_link=False,
                )
                try:
                    if name in mapping.keys():
                        kwargs['to'] = mapping.pop(name, )
                    if kwargs['to'] in ['self', ]:
                        kwargs['to'] = field.model
                except KeyError as e:
                    logger.debug(e)
                field = field_type(*args, **kwargs, )
                field.name = name
            elif field.unique:
                field.unique = False
                field.db_index = True
            fields.append(field, )
        if bool(mapping):
            raise TypeError(_('Mapping parent %(mapping)s in %(app_label)s.%(object_name)s not mapped, please correct') % dict(mapping=', '.join(mapping.keys()), app_label=model._meta.app_label, object_name=model._meta.object_name, ))
        return fields

    def temporary_model_extra_fields(self, ):
        try:
            from django.contrib.auth import get_user_model

            User = get_user_model()
        except Exception as e:
            logger.debug(e)
            from django.conf import settings
            User = settings.AUTH_USER_MODEL
        extra = dict(self.extra_fields)
        fields = {
            **extra,
            **{
                'temporary_id': models.AutoField(primary_key=True, ),
                'session': models.ForeignKey(
                    to=User,
                    on_delete=models.DO_NOTHING,
                    verbose_name=_('session'),
                    help_text=_('Used for linked key session by user'),
                ),
            },
        }
        if self.temporary_lifetime is not None:
            fields['temporary_expired'] = models.DateTimeField(
                default=ExpiryDefault(self.temporary_lifetime, ),
            )
        return fields

    def temporary_model_meta_options(self, model, ):
        return {
            'db_table': self.db_table or f'temporary_{model._meta.db_table}',
            'verbose_name': self.verbose_name or _('Used store temporary %(object_name)s') % dict(object_name=stringcase.titlecase(model._meta.object_name), ),
            'ordering': ('-temporary_id',),
            'get_latest_by': 'temporary_id',
        }


class Temporary(TemporaryRecords, ):
    pass
