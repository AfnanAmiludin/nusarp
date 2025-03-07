import json
import logging

from django.contrib import auth
from django.contrib.auth.models import Group
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import Permission as DjangoPermission
from authentication.apis.serializers import PermissionSerializer
from authentication.models import Permission
from library.cacheops import invalidate_model
from rest_framework.permissions import IsAuthenticated
from collections import OrderedDict
from authentication.apis.viewsets import FormatViewSet


logger = logging.getLogger(__name__)

User = auth.get_user_model()

class UserPermissionViewSet(FormatViewSet, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PermissionSerializer
    queryset = Permission.objects.all()

    def list(self, request, *args, **kwargs):
        return self.notgranted(request, *args, **kwargs)

    @action(
        detail=False,
        url_path='notgranted',
        url_name='notgranted',
        methods=['get'],
    )
    def notgranted(self, request, *args, **kwargs):
        data = request.query_params.dict()
        user = request.user
        if 'current' in data:
            user = User.objects.get(pk=json.loads(data['current'])['user_id'])
        granted = user.permissions_derivative().union(
            Permission.objects.filter(pk__in=user.user_permissions.values_list('pk', flat=True)),
        )
        if user.is_superuser:
            granted = Permission.objects.all()
        queryset = self.filter_queryset(
            Permission.objects.exclude(pk__in=list(granted.values_list('pk', flat=True))))
        group = request.query_params.get('group')
        print('UASUUUUU', group)
        
        if group is None:
            return self._not_grouped_list(queryset, request)
        else:
            return self._grouped_list(group, queryset, request)

    @action(
        detail=False,
        url_path='granted',
        url_name='granted',
        methods=['get'],
    )
    def granted(self, request, *args, **kwargs):
        data = request.query_params.dict()
        user = request.user
        if 'current' in data:
            user = User.objects.get(pk=json.loads(data['current'])['user_id'])
        queryset = user.permissions_derivative().union(
            Permission.objects.filter(pk__in=user.user_permissions.values_list('pk', flat=True)),
        )
        queryset = self.filter_queryset(Permission.objects.filter(Q(
            pk__in=list(queryset.values_list('pk', flat=True)),
            user=user,
            group__user=user,
            _connector=Q.OR,
        )).distinct())
        if user.is_superuser:
            queryset = self.filter_queryset(Permission.objects.all())
        group = request.query_params.get('group')
        
        if group is None:
            print('UASUUUUU2', self._not_grouped_list(queryset, request))
            return self._not_grouped_list(queryset, request)
        else:
            return self._grouped_list(group, queryset, request)

    @action(
        detail=False,
        url_path='grant',
        url_name='grant',
        methods=['post'],
    )
    def grant(self, request, *args, **kwargs):
        data = request.data.dict()
        user = request.user
        if 'current' in data:
            user = User.objects.get(pk=json.loads(data['current'])['user_id'])
        values = json.loads(data['values'])
        if isinstance(values, list):
            for permission in Permission.objects.filter(pk__in=[permission['id'] for permission in values]):
                user.user_permissions.add(permission.pk)
        else:
            user.user_permissions.add(Permission.objects.get(pk=values['id']).pk)
        invalidate_model(DjangoPermission)
        invalidate_model(Permission)
        return Response(dict(
            message=_('Permission have been successfully granted to user %(user_name)s') % dict(user_name=user.user_name, ),
        ), status=status.HTTP_200_OK, )

    @action(
        detail=False,
        url_path='grantall',
        url_name='grantall',
        methods=['post'],
    )
    def grant_all(self, request, *args, **kwargs):
        data = request.data.dict()
        user = request.user
        if 'current' in data:
            user = User.objects.get(pk=json.loads(data['current'])['user_id'])
        granted = user.permissions_derivative().union(
            Permission.objects.filter(pk__in=user.user_permissions.values_list('pk', flat=True)),
        )
        permissions = Permission.objects.exclude(pk__in=list(granted.values_list('pk', flat=True)))
        for permission in permissions:
            user.user_permissions.add(permission.pk)
        invalidate_model(DjangoPermission)
        invalidate_model(Permission)
        return Response(dict(
            message=_('All permission have been successfully granted to user %(user_name)s') % dict(user_name=user.user_name, ),
        ), status=status.HTTP_200_OK, )

    @action(
        detail=False,
        url_path='revoke',
        url_name='revoke',
        methods=['post'],
    )
    def revoke(self, request, *args, **kwargs):
        data = request.data.dict()
        user = request.user
        if 'current' in data:
            user = User.objects.get(pk=json.loads(data['current'])['user_id'])
        values = json.loads(data['values'])
        if isinstance(values, list):
            for permission in Permission.objects.filter(pk__in=[permission['id'] for permission in values]):
                granted = Permission.objects.filter(Q(
                    user=user,
                    pk=permission.pk,
                    _connector=Q.AND,
                ))
                if not granted.exists():
                    return Response(dict(
                        error=_(
                            'Permission <b>%(permission_name)s</b> can\'t revoked manual from user %(user_name)s, '
                            'revoke from group') % dict(
                            permission_name=permission.name_translated,
                            user_name=user.user_name,
                        ),
                    ), status=status.HTTP_404_NOT_FOUND)
                user.user_permissions.remove(permission.pk)
        else:
            permission = Permission.objects.get(pk=values['id'])
            granted = Permission.objects.filter(Q(
                user=user,
                pk=permission.pk,
                _connector=Q.AND,
            ))
            if not granted.exists():
                return Response(dict(
                    error=_(
                        'Permission <b>%(permission_name)s</b> can\'t revoked manual from user %(user_name)s, '
                        'revoke from group') % dict(
                        permission_name=permission.name_translated,
                        user_name=user.user_name,
                    ),
                ), status=status.HTTP_404_NOT_FOUND)
            user.user_permissions.remove(permission.pk)
        invalidate_model(DjangoPermission)
        invalidate_model(Permission)
        return Response(dict(
            message=_('Permission have been successfully revoked from user %(user_name)s') % dict(user_name=user.user_name),
        ), status=status.HTTP_200_OK, )

    @action(
        detail=False,
        url_path='revokeall',
        url_name='revokeall',
        methods=['post'],
    )
    def revoke_all(self, request, *args, **kwargs):
        data = request.data.dict()
        user = request.user
        if 'current' in data:
            user = User.objects.get(pk=json.loads(data['current'])['user_id'])
        user.user_permissions.clear()
        invalidate_model(DjangoPermission)
        invalidate_model(Permission)
        return Response(dict(
            message=_('All permissions have been successfully revoked from user %(user_name)s') % dict(user_name=user.user_name, ),
        ), status=status.HTTP_200_OK, )


class GroupPermissionViewSet():
    extra_permissions = {}
    serializer_class = PermissionSerializer
    queryset = Permission.objects.all()

    def list(self, request, *args, **kwargs):
        return self.notgranted(request, *args, **kwargs)

    @action(
        detail=False,
        url_path='notgranted',
        url_name='notgranted',
        methods=['get'],
    )
    def notgranted(self, request, *args, **kwargs):
        data = request.query_params.dict()
        group = Group.objects.get(pk=json.loads(data['current'])['id'])
        granted = Permission.objects.filter(group=group)
        queryset = self.filter_queryset(
            Permission.objects.exclude(pk__in=list(granted.values_list('pk', flat=True))))
        group = request.query_params.get('group')
        if group is None:
            return self._not_grouped_list(queryset, request)
        else:
            return self._grouped_list(group, queryset, request)

    @action(
        detail=False,
        url_path='granted',
        url_name='granted',
        methods=['get'],
    )
    def granted(self, request, *args, **kwargs):
        data = request.query_params.dict()
        group = Group.objects.get(pk=json.loads(data['current'])['id'])
        queryset = self.filter_queryset(Permission.objects.filter(group=group))
        group = request.query_params.get('group')
        if group is None:
            return self._not_grouped_list(queryset, request)
        else:
            return self._grouped_list(group, queryset, request)

    @action(
        detail=False,
        url_path='grant',
        url_name='grant',
        methods=['post'],
    )
    def grant(self, request, *args, **kwargs):
        data = request.data.dict()
        group = Group.objects.get(pk=json.loads(data['current'])['id'])
        values = json.loads(data['values'])
        if isinstance(values, list):
            for permission in Permission.objects.filter(pk__in=[permission['id'] for permission in values]):
                group.permissions.add(permission.pk)
        else:
            group.permissions.add(Permission.objects.get(pk=values['id']).pk)
        invalidate_model(DjangoPermission)
        invalidate_model(Permission)
        return Response(dict(
            message=_('Permission have been successfully granted to group %(name)s') % dict(name=group.name, ),
        ), status=status.HTTP_200_OK, )

    @action(
        detail=False,
        url_path='grantall',
        url_name='grantall',
        methods=['post'],
    )
    def grant_all(self, request, *args, **kwargs):
        data = request.data.dict()
        group = Group.objects.get(pk=json.loads(data['current'])['id'])
        granted = Permission.objects.filter(group=group)
        permissions = Permission.objects.exclude(pk__in=list(granted.values_list('pk', flat=True)))
        for permission in permissions:
            group.permissions.add(permission.pk)
        invalidate_model(DjangoPermission)
        invalidate_model(Permission)
        return Response(dict(
            message=_('All permission have been successfully granted to group %(name)s') % dict(name=group.name, ),
        ), status=status.HTTP_200_OK, )

    @action(
        detail=False,
        url_path='revoke',
        url_name='revoke',
        methods=['post'],
    )
    def revoke(self, request, *args, **kwargs):
        data = request.data.dict()
        group = Group.objects.get(pk=json.loads(data['current'])['id'])
        values = json.loads(data['values'])
        if isinstance(values, list):
            for permission in Permission.objects.filter(pk__in=[permission['id'] for permission in values]):
                group.permissions.remove(permission.pk)
        else:
            permission = Permission.objects.get(pk=values['id'])
            group.permissions.remove(permission.pk)
        invalidate_model(DjangoPermission)
        invalidate_model(Permission)
        return Response(dict(
            message=_('Permission have been successfully revoked from grouo %(name)s') % dict(name=group.name, ),
        ), status=status.HTTP_200_OK, )

    @action(
        detail=False,
        url_path='revokeall',
        url_name='revokeall',
        methods=['post'],
    )
    def revoke_all(self, request, *args, **kwargs):
        data = request.data.dict()
        group = Group.objects.get(pk=json.loads(data['current'])['id'])
        group.permissions.clear()
        invalidate_model(DjangoPermission)
        invalidate_model(Permission)
        return Response(dict(
            message=_('All permissions have been successfully revoked from group %(name)s') % dict(name=group.name, ),
        ), status=status.HTTP_200_OK, )
