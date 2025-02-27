import hashlib
import string
from inspect import isclass

from Crypto.Cipher import AES
from django.contrib.admin.widgets import (
    AdminTextInputWidget,
    AdminEmailInputWidget,
    AdminDateWidget,
    AdminIntegerFieldWidget,
    AdminBigIntegerFieldWidget,
    AdminSplitDateTime,
    AdminTextareaWidget,
)
from django.contrib.auth import get_user_model
from django.core import validators
from django.core.exceptions import FieldError, ImproperlyConfigured
from django.db import models
from django.utils.functional import cached_property
from django.utils.text import capfirst

from core import settings

__all__ = [
    'EncryptedFieldMixin',
    'EncryptedTextField',
    'EncryptedCharField',
    'EncryptedEmailField',
    'EncryptedIntegerField',
    'EncryptedDateField',
    'EncryptedDateTimeField',
    'EncryptedBigIntegerField',
    'EncryptedPositiveIntegerField',
    'EncryptedPositiveSmallIntegerField',
    'EncryptedSmallIntegerField',
    'SearchField',
]


class EncryptedFieldMixin(models.Field):
    def __init__(self, *args, **kwargs):
        if kwargs.get('primary_key'):
            raise ImproperlyConfigured(f'{self.__class__.__name__} does not support primary_key=True.')
        if kwargs.get('unique'):
            raise ImproperlyConfigured(f'{self.__class__.__name__} does not support unique=True.')
        if kwargs.get('db_index'):
            raise ImproperlyConfigured(f'{self.__class__.__name__} does not support db_index=True.')
        self._internal_type = 'BinaryField'
        super().__init__(*args, **kwargs)

    @cached_property
    def keys(self):
        key_list = settings.FIELD_ENCRYPTION_KEYS
        if not isinstance(key_list, (list, tuple)):
            raise ImproperlyConfigured('FIELD_ENCRYPTION_KEYS should be a list.')
        return key_list

    def encrypt(self, data_to_encrypt):
        if not isinstance(data_to_encrypt, str):
            data_to_encrypt = str(data_to_encrypt)
        cipher = AES.new(bytes.fromhex(self.keys[0]), AES.MODE_GCM)
        nonce = cipher.nonce
        cypher_text, tag = cipher.encrypt_and_digest(data_to_encrypt.encode())
        return nonce + tag + cypher_text

    def decrypt(self, value):
        nonce = value[:16]
        if not isinstance(nonce, (bytes, bytearray, memoryview)) or len(nonce) != 16:
            raise ValueError('Data is corrupted.')
        tag = value[16:32]
        cypher_text = value[32:]
        counter = 0
        num_keys = len(self.keys)
        while counter < num_keys:
            cipher = AES.new(bytes.fromhex(self.keys[counter]), AES.MODE_GCM, nonce=nonce)
            try:
                plaintext = cipher.decrypt_and_verify(cypher_text, tag)
            except ValueError:
                counter += 1
                continue
            return plaintext.decode()
        raise ValueError('AES Key incorrect or data is corrupted')

    def get_internal_type(self):
        return self._internal_type

    def get_db_prep_save(self, value, connection):
        if self.empty_strings_allowed and value == bytes():
            value = ''
        value = super().get_db_prep_save(value, connection)
        if value is not None:
            encrypted_value = self.encrypt(value)
            return connection.Database.Binary(encrypted_value)

    def from_db_value(self, value, expression, connection):
        if value is not None:
            return self.to_python(self.decrypt(value))

    @cached_property
    def validators(self):
        self._internal_type = super().get_internal_type()
        try:
            return super().validators
        finally:
            self._internal_type = 'BinaryField'


class EncryptedTextField(EncryptedFieldMixin, models.TextField):
    pass


class EncryptedCharField(EncryptedFieldMixin, models.CharField):
    def __init__(self, *args, db_collation=None, **kwargs):
        EncryptedFieldMixin.__init__(self, *args, **kwargs)
        self.db_collation = db_collation
        if self.max_length is not None:
            self.validators.append(validators.MaxLengthValidator(self.max_length))

    def check(self, **kwargs):
        databases = kwargs.get('databases') or []
        return [
            *EncryptedFieldMixin.check(self, **kwargs),
            *super()._check_db_collation(databases),
        ]


class EncryptedEmailField(EncryptedFieldMixin, models.EmailField):
    pass


class EncryptedIntegerField(EncryptedFieldMixin, models.IntegerField):
    pass


class EncryptedPositiveIntegerField(EncryptedFieldMixin, models.PositiveIntegerField):
    pass


class EncryptedPositiveSmallIntegerField(EncryptedFieldMixin, models.PositiveSmallIntegerField):
    pass


class EncryptedSmallIntegerField(EncryptedFieldMixin, models.SmallIntegerField):
    pass


class EncryptedBigIntegerField(EncryptedFieldMixin, models.BigIntegerField):
    pass


class EncryptedDateField(EncryptedFieldMixin, models.DateField):
    pass


class EncryptedDateTimeField(EncryptedFieldMixin, models.DateTimeField, ):
    def db_type(self, connection):
        if connection.vendor == 'postgresql':
            return 'timestamp'
        else:
            return super(EncryptedDateTimeField, self).db_type(connection)


SEARCH_HASH_PREFIX = 'enc:'


def is_hashed_already(data_string):
    if data_string is None:
        return False
    if not isinstance(data_string, str):
        return False
    if not data_string.startswith(SEARCH_HASH_PREFIX):
        return False
    actual_hash = data_string[len(SEARCH_HASH_PREFIX):]
    if len(actual_hash) != 64:
        return False
    return all([char in string.hexdigits for char in actual_hash])


class SearchFieldDescriptor:
    def __init__(self, field):
        self.field = field

    def __get__(self, instance, owner):
        if instance is None:
            return self
        if self.field.encrypted_field_name in instance.__dict__:
            decrypted_data = instance.__dict__[self.field.encrypted_field_name]
        else:
            instance.refresh_from_db(fields=[self.field.encrypted_field_name])
            decrypted_data = getattr(instance, self.field.encrypted_field_name)
        setattr(instance, self.field.name, decrypted_data)
        return instance.__dict__[self.field.name]

    def __set__(self, instance, value):
        instance.__dict__[self.field.name] = value
        if not is_hashed_already(value):
            instance.__dict__[self.field.encrypted_field_name] = value


class SearchField(models.CharField):
    description = 'A secure SearchField to accompany an EncryptedField'
    descriptor_class = SearchFieldDescriptor

    def __init__(self, hash_key=None, encrypted_field_name=None, *args, **kwargs):
        if hash_key is None:
            raise ImproperlyConfigured('you must supply a hash_key')
        self.hash_key = hash_key
        if encrypted_field_name is None:
            raise ImproperlyConfigured('you must supply the name of the accompanying Encrypted Field that will hold the data')
        if not isinstance(encrypted_field_name, str):
            raise ImproperlyConfigured(''''encrypted_field_name' must be a string''')
        self.encrypted_field_name = encrypted_field_name
        if kwargs.get('primary_key'):
            raise ImproperlyConfigured('SearchField does not support primary_key=True.')
        if 'default' in kwargs:
            raise ImproperlyConfigured(f'''SearchField does not support 'default='. Set 'default=' on '{self.encrypted_field_name}' instead''')
        if 'db_index' not in kwargs:
            kwargs['db_index'] = True
        kwargs['max_length'] = 64 + len(SEARCH_HASH_PREFIX)
        kwargs['null'] = True
        kwargs['blank'] = True
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.hash_key:
            kwargs['hash_key'] = self.hash_key
        if self.encrypted_field_name:
            kwargs['encrypted_field_name'] = self.encrypted_field_name
        return name, path, args, kwargs

    def has_default(self):
        return self.model._meta.get_field(self.encrypted_field_name).has_default()

    def get_default(self):
        return self.model._meta.get_field(self.encrypted_field_name).get_default()

    def get_prep_value(self, value):
        if value is None:
            return value
        value = str(value)
        if callable(self.hash_key):
            hash_key = self.hash_key()
        else:
            hash_key = self.hash_key
        if is_hashed_already(value):
            return value
        value = value + hash_key
        return SEARCH_HASH_PREFIX + hashlib.sha256(value.encode()).hexdigest()

    def formfield(self, **kwargs):
        defaults = {}
        if kwargs.get('label') is None:
            defaults.update({'label': capfirst(self.verbose_name)})
        widget = kwargs.get('widget')
        if isclass(widget) and issubclass(widget, AdminTextInputWidget):
            encrypted_field = self.model._meta.get_field(self.encrypted_field_name)
            if isinstance(encrypted_field, EncryptedEmailField):
                defaults.update({'widget': AdminEmailInputWidget})
            elif isinstance(encrypted_field, EncryptedDateField):
                defaults.update({'widget': AdminDateWidget})
            elif isinstance(encrypted_field, EncryptedDateTimeField):
                defaults.update({'widget': AdminSplitDateTime})
            elif isinstance(encrypted_field, EncryptedIntegerField):
                defaults.update({'widget': AdminIntegerFieldWidget})
            elif isinstance(encrypted_field, EncryptedPositiveIntegerField):
                defaults.update({'widget': AdminIntegerFieldWidget})
            elif isinstance(encrypted_field, EncryptedPositiveSmallIntegerField):
                defaults.update({'widget': AdminIntegerFieldWidget})
            elif isinstance(encrypted_field, EncryptedSmallIntegerField):
                defaults.update({'widget': AdminIntegerFieldWidget})
            elif isinstance(encrypted_field, EncryptedBigIntegerField):
                defaults.update({'widget': AdminBigIntegerFieldWidget})
            elif isinstance(encrypted_field, EncryptedTextField):
                defaults.update({'widget': AdminTextareaWidget})
        kwargs.update(defaults)
        return self.model._meta.get_field(self.encrypted_field_name).formfield(**kwargs)

    def clean(self, value, model_instance):
        if model_instance is None:
            model_instance = get_user_model()
        return model_instance._meta.get_field(self.encrypted_field_name).clean(
            value, model_instance
        )

    def contribute_to_class(self, cls, name, **kwargs):
        super().contribute_to_class(cls, name, **kwargs)
        setattr(cls, self.name, self.descriptor_class(self))


def get_prep_lookup_error(self):
    raise FieldError(
        f'''{self.lhs.field.__class__.__name__} does not support '{self.lookup_name}' lookups'''
    )


for name, lookup in models.Field.class_lookups.items():
    if name != 'isnull':
        lookup_class = type(
            'EncryptedField' + name,
            (lookup,),
            {'get_prep_lookup': get_prep_lookup_error},
        )
        EncryptedFieldMixin.register_lookup(lookup_class)
    if name not in ['isnull', 'exact']:
        lookup_class = type(
            'SearchField' + name,
            (lookup,),
            {'get_prep_lookup': get_prep_lookup_error}
        )
        SearchField.register_lookup(lookup_class)
