import logging

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from authentication.models import Permission
from library.restframeworkflexfields import FlexFieldsModelSerializer

logger = logging.getLogger(__name__)


class PermissionSerializer(FlexFieldsModelSerializer):
    name_translated = serializers.SerializerMethodField(method_name='get_name_translated', )

    class Meta:
        model = Permission
        fields = [
            'id',
            'name',
            'name_translated',
            'content_type',
            'codename',
            'group_set',
        ]
        extra_kwargs = {
            'id': {'required': False, },
            'content_type': {'required': False, },
            'name_translated': {'required': False, },
            'group_set': {'required': False, },
        }
        expandable_fields = {
            'content_type': (
                'authentication.apis.serializers.ContentTypeSerializer', {'many': False, },
            ),
            'group_set': (
                'authentication.apis.serializers.GroupSerializer', {'many': True, },
            ),
        }

    def get_name_translated(self, instance):
        return instance.name_translated if hasattr(instance, 'name_translated') else ' '.join(' '.join([
            _(name)
            .replace('Used', '')
            .replace('Store', '')
            .replace('History', str(_('History')))
            .replace('Can', str(_('Can')))
            .replace('Add', str(_('Add')))
            .replace('Change', str(_('Change')))
            .replace('Delete', str(_('Delete')))
            .replace('View', str(_('View'))) for name in (instance.name.title()).split()
        ]).split())
