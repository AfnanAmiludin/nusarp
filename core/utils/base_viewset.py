from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db.models import Q

from core.utils.search_filter_utils import SearchFilterMixin
from core.utils.pagination import CustomPageNumberPagination
from core.utils.prefetch_utils import PrefetchRelatedMixin

class SearchFilterViewSet(viewsets.ModelViewSet, SearchFilterMixin, PrefetchRelatedMixin):
    """
    Base ViewSet that provides search, filter, and prefetch functionalities.
    Other ViewSets can inherit from this to get these features.
    """
    pagination_class = CustomPageNumberPagination
    
    def get_base_queryset(self):
        """
        Return the base queryset with common filters applied.
        Override this in your ViewSet if needed.
        """
        return self.get_queryset().filter(is_removed=False)
    
    def list(self, request, *args, **kwargs):
        """
        Enhanced list method with search, filter, and efficient prefetching.
        """
        # Start with the base queryset
        queryset = self.get_base_queryset()
        
        # Apply search
        queryset = self.apply_search(queryset, request)
        
        # Apply filters
        filtered_queryset = self.apply_filters(queryset, request)
        if filtered_queryset is None:
            return Response(
                {"detail": "Invalid filter format"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        queryset = filtered_queryset
        
        # Apply sorting
        queryset = self.apply_sorting(queryset, request)
        
        # Add common select_related fields if defined
        if hasattr(self, 'select_related_fields') and self.select_related_fields:
            queryset = queryset.select_related(*self.select_related_fields)
        
        # Paginate the queryset
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            # Efficiently prefetch related objects for the current page
            page = self.prefetch_related_objects(queryset, page)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        # If not paginated, prefetch for the whole queryset
        queryset = self.prefetch_related_objects(queryset)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)