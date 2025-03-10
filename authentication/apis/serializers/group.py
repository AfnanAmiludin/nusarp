import logging

from django.contrib import auth
from authentication.models import Group
from library.restframeworkflexfields import FlexFieldsModelSerializer

logger = logging.getLogger(__name__)

User = auth.get_user_model()


class GroupSerializer(FlexFieldsModelSerializer, ):
    class Meta:
        model = Group
        fields = [
            'base64pk',
            'id',
            'name',
            'parent',
            'derivative_permission',
            'permissions',
            'created',
            'modified',
            'read_only',
            'enable',
            'properties',
            'description',
            'has_children',
            'is_removed',
        ]
        extra_kwargs = {
            'base64pk': {'required': False, },
            'id': {'required': False, },
            'permissions': {'required': False, 'read_only': True, },
            'is_removed': {'required': False, },
        }
        expandable_fields = {
            'parent': (
                'authentication.apis.serializers.GroupSerializer', {'many': False, },
            ),
            'permissions': (
                'authentication.apis.serializers.PermissionSerializer', {'many': True, },
            ),
        }
