from rest_framework.permissions import IsAuthenticated
from authentication.models.group import Group
from authentication.apis.serializers import GroupSerializer
from core.utils import SearchFilterViewSet

import logging

logger = logging.getLogger(__name__)

class GroupViewSet(SearchFilterViewSet):
    """
    ViewSet for Group model inheriting search, filter and prefetch capabilities.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]
    select_related_fields = ['parent']  # Fields to always select_related
    
    def get_search_fields(self):
        """
        Define searchable fields for the Group model.
        """
        return ['group_id', 'name', 'description']  # Adjust based on your Group model fields
    
    def get_related_fields(self):
        """
        Define related fields to prefetch.
        """
        return {
            'children': {
                'related_name': 'parent',
                'filter_kwargs': {'is_removed': False},
                'property_name': 'children_list'
            }
        }