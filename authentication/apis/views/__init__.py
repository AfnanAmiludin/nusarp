from authentication.apis.views.user import UserViewSet
from authentication.apis.views.group import GroupViewSet
from authentication.apis.views.permission import UserPermissionViewSet, GroupPermissionViewSet
__all__ = [
    UserViewSet,
    GroupViewSet,
    UserPermissionViewSet,
    GroupPermissionViewSet
]
