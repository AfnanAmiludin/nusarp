import logging

from django.contrib import auth
from authentication.models import Group
from library.restframeworkflexfields import FlexFieldsModelSerializer
from rest_framework import serializers

logger = logging.getLogger(__name__)

User = auth.get_user_model()


class GroupSerializer(FlexFieldsModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = [
            'group_id',
            'group_name',
            'parent',
            'status',
            'created',
            'modified',
            'children',
        ]
        expandable_fields = {
            'parent': ('authentication.apis.serializers.group.GroupSerializer', {'many': False}),
        }
        read_only_fields = ['created', 'modified']
        extra_kwargs = {
            'group_id': {'read_only': True},
        }

    def get_children(self, obj):
        children = Group.objects.filter(parent=obj)
        return GroupSerializer(children, many=True).data
        
