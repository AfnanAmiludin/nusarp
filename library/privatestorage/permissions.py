"""
Possible functions for the ``PRIVATE_STORAGE_AUTH_FUNCTION`` setting.
"""


def allow_authenticated(private_file):
    return private_file.request.user.is_authenticated


def allow_staff(private_file):
    request = private_file.request
    return request.user.is_authenticated and request.user.is_staff


def allow_superuser(private_file):
    request = private_file.request
    return request.user.is_authenticated and request.user.is_superuser
