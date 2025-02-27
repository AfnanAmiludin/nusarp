import logging

from django.contrib import auth
from django.contrib.auth.base_user import BaseUserManager
from django.utils import translation, timezone

from library.modelutils.managers import SoftDeletableManager

logger = logging.getLogger(__name__)


class UserManager(BaseUserManager, SoftDeletableManager):
    def _create_user(self, user_name, email, password, **extra_fields):
        if user_name is None:
            raise ValueError('The given username must be set')
        extra_fields.setdefault('real_name', user_name.title())
        email = self.normalize_email(email)
        user = self.model(user_name=user_name, email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, user_name, email=None, password=None, **extra_fields):
        extra_fields.setdefault('locale', translation.get_language())
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('enable', True)
        extra_fields.setdefault('is_active', False)
        extra_fields.setdefault('date_joined', timezone.now())
        return self._create_user(user_name, email, password, **extra_fields)

    def create_superuser(self, user_name, email=None, password=None, **extra_fields):
        extra_fields.setdefault('locale', translation.get_language())
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('enable', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('date_joined', timezone.now())
        extra_fields.setdefault('actived_date', timezone.now())
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(user_name, email, password, **extra_fields)

    def with_perm(self, perm, is_active=True, include_superusers=True, backend=None, obj=None):
        if backend is None:
            backends = auth._get_backends(return_tuples=True)
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    'You have multiple authentication backends configured and '
                    'therefore must provide the `backend` argument.'
                )
        elif not isinstance(backend, str):
            raise TypeError(
                'backend must be a dotted import path string (got %r).'
                % backend
            )
        else:
            backend = auth.load_backend(backend)
        if hasattr(backend, 'with_perm'):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()
