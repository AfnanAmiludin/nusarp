from rest_framework.permissions import IsAuthenticated
from authentication.models.group import Group
from authentication.apis.serializers import GroupSerializer
from core.utils.base_viewset import SearchFilterViewSet
from django.db.models import Index, F
import logging

logger = logging.getLogger(__name__)

class GroupViewSet(SearchFilterViewSet):
    """
    ViewSet for Group model with optimized search capabilities.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]
    select_related_fields = ['parent']
    
    def get_search_fields(self):
        """
        Define searchable fields for the Group model.
        """
        return ['group_id', 'group_name', 'group_hierarchy',]
    
    def get_search_config(self):
        """
        Configure search behavior with optimizations for large datasets.
        """
        return {
            'use_index': True,
            'max_results': 50,
            'prioritize_exact_matches': True,
            'use_trigram': True,  # Enable if using PostgreSQL with trigram extension
            'min_length': 2,
            'search_fields_weights': {
                'group_id': 10,  # Primary identifier gets highest weight
                'group_name': 5,       # Name is next most important
                'group_hierarchy': 1 # Description is least important for matching
            }
        }
    
    def get_related_fields(self):
        """
        Define related fields to prefetch with optimized approach.
        """
        return {
            'children': {
                'related_name': 'parent',
                'filter_kwargs': {'is_removed': False},
                'property_name': 'children_list'
            }
        }
    
    def get_queryset(self):
        """
        Optimize initial queryset with selective loading.
        """
        # Start with only necessary fields for listing
        queryset = super().get_queryset().filter(is_removed=False)
        
        # Get the search term if provided
        search_term = self.request.query_params.get('search', None)

        # Get the filters term if provided
        filters_term = self.request.query_params.get('filters', None)
        
        # Check if tree_mode is specified in the request
        tree_mode = self.request.query_params.get('tree_mode', 'parent_only')
        
        # If searching, don't filter by parent to ensure all matching groups are found
        # Otherwise, apply the tree_mode filter
        if not search_term and not filters_term and tree_mode == 'parent_only':
            queryset = queryset.filter(parent__isnull=True)
        
        # Use `.only()` to fetch only the fields we need for listing
        return queryset.only(
            'group_id', 'group_name', 'group_hierarchy', 'parent'
        )