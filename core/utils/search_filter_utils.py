import json
import logging
from urllib.parse import unquote
from django.db.models import Q, Case, When, Value, IntegerField, F, TextField, CharField, Sum, IntegerField, Value, Case, When, ExpressionWrapper, FloatField
from django.db import connection
from rest_framework.response import Response
from rest_framework import status
from functools import reduce
import operator

logger = logging.getLogger(__name__)

class SearchFilterMixin:
    """
    Optimized mixin class that provides search and filter functionality for Django REST Framework ViewSets.
    Specifically optimized for large datasets (10M+ records).
    """
    
    def get_search_fields(self):
        """
        Returns list of model fields that should be searchable.
        Override this in your ViewSet to customize searchable fields.
        """
        return []
    
    def get_search_config(self):
        """
        Returns search configuration dictionary.
        Override this in your ViewSet to customize search behavior.
        """
        return {
            'use_index': True,  # Set to True if your DB has proper indexes on search fields
            'max_results': 50,  # Limit maximum search results
            'prioritize_exact_matches': True,  # Prioritize exact matches over partial
            'use_trigram': False,  # Use PostgreSQL trigram indexes if available
            'min_length': 3,  # Minimum search query length to process
            'search_fields_weights': {},  # Field-specific weights, e.g. {'name': 10, 'description': 5}
        }
    
    def _explain_query(self, queryset, query_description=''):
        """
        Debug helper that shows the query execution plan.
        Only use during development - expensive for production.
        """
        if not settings.DEBUG:
            return
            
        query = queryset.query
        raw_sql = str(query)
        logger.debug(f"SQL for {query_description}: {raw_sql}")
        
        with connection.cursor() as cursor:
            cursor.execute(f"EXPLAIN ANALYZE {raw_sql}")
            explain = cursor.fetchall()
            for line in explain:
                logger.debug(line[0])
    
    def apply_search(self, queryset, request):
        """
        Apply search filtering to the queryset based on request parameters.
        Optimized for large datasets.
        """
        search_query = request.query_params.get('search', None)
        
        if not search_query:
            return queryset
        
        # Get search configuration
        config = self.get_search_config()
        
        # Clean and prepare search query
        search_query = unquote(search_query).strip()
        logger.debug(f"Decoded Search Query: {search_query}")
        
        # Skip processing if search query is too short
        if len(search_query) < config.get('min_length', 3):
            return queryset.none()
        
        # Get columns to search within
        columns = request.query_params.getlist('columns[]', [])
        model = queryset.model
        
        # Only include columns that actually exist in the model
        valid_columns = columns if columns else self.get_search_fields()
        valid_columns = [col for col in valid_columns if hasattr(model, col)]
        
        if not valid_columns:
            return queryset.none()
        
        # Get field weights
        field_weights = config.get('search_fields_weights', {})
        
        # Check if we can use database specific optimizations
        db_engine = connection.vendor
        use_trigram = config.get('use_trigram', False) and db_engine == 'postgresql'
        
        # Start with an optimized base query - add filters to base queryset
        base_query = queryset.filter(is_removed=False)
        
        # For PostgreSQL with trigram indexes
        # Inside the PostgreSQL trigram section where you calculate similarity
        if use_trigram and db_engine == 'postgresql':
            from django.contrib.postgres.search import TrigramSimilarity
            from django.db.models import TextField, CharField, DateField, DateTimeField, IntegerField, FloatField, DecimalField
            
            # Calculate similarity for each field
            similarity_expressions = []
            for column in valid_columns:
                # Get the field object from the model to check its type
                try:
                    field = model._meta.get_field(column)
                    
                    # Only apply trigram similarity to text-based fields
                    if isinstance(field, (TextField, CharField)):
                        weight = field_weights.get(column, 1.0)
                        similarity_expressions.append(
                            TrigramSimilarity(column, search_query) * weight
                        )
                    # Skip date, numeric, and other non-text fields
                    else:
                        logger.debug(f"Skipping non-text field for trigram search: {column} (type: {type(field).__name__})")
                except Exception as e:
                    logger.error(f"Error determining field type for {column}: {str(e)}")
                    continue
            
            # Use aggregated similarity score - only if we have valid expressions
            if similarity_expressions:
                from django.db.models import Sum, F, ExpressionWrapper, FloatField
                
                # If there's only one expression, use it directly
                if len(similarity_expressions) == 1:
                    combined_similarity = similarity_expressions[0]
                else:
                    # Combine multiple expressions with addition
                    combined_similarity = reduce(lambda x, y: x + y, similarity_expressions)
                
                # Annotate with combined similarity score
                annotated_query = base_query.annotate(
                    similarity=combined_similarity
                ).filter(similarity__gt=0.3)
                
                # Apply ordering before slicing
                ordered_query = annotated_query.order_by('-similarity')
                
                # Apply slice after ordering
                return ordered_query[:config.get('max_results', 50)]
        
        # For databases without trigram support or when not using trigram
        # Create exact match query
        exact_queries = []
        for column in valid_columns:
            exact_queries.append(Q(**{f'{column}__iexact': search_query}))
        
        if exact_queries:
            exact_q = reduce(operator.or_, exact_queries)
            exact_matches = base_query.filter(exact_q)
            
            # If we have exact matches and want to prioritize them
            if exact_matches.exists() and config.get('prioritize_exact_matches', True):
                # Get primary key field name
                pk_field = model._meta.pk.name
                
                # Get exact match IDs without slicing the queryset itself
                exact_ids = list(exact_matches.values_list(pk_field, flat=True))
                
                # Limit the IDs in Python instead of slicing the queryset
                max_exact = config.get('max_results', 20)
                exact_ids = exact_ids[:max_exact]
                
                # Create partial match query
                partial_queries = []
                for column in valid_columns:
                    partial_queries.append(Q(**{f'{column}__icontains': search_query}))
                    
                if partial_queries:
                    partial_q = reduce(operator.or_, partial_queries)
                    
                    # Get partial matches excluding exact matches
                    partial_matches = base_query.filter(partial_q).exclude(exact_q)
                    
                    # Get IDs without slicing the queryset
                    partial_ids = list(partial_matches.values_list(pk_field, flat=True))
                    
                    # Limit the IDs in Python
                    remaining_slots = config.get('max_results', 50) - len(exact_ids)
                    partial_ids = partial_ids[:remaining_slots]
                    
                    # Combine IDs and ensure ordering
                    combined_ids = exact_ids + partial_ids
                    
                    if combined_ids:
                        # Use Case/When for custom ordering based on position
                        when_clauses = [
                            When(**{pk_field: pk, 'then': Value(i)})
                            for i, pk in enumerate(combined_ids)
                        ]
                        
                        ordered_query = base_query.filter(**{f'{pk_field}__in': combined_ids})
                        
                        if when_clauses:
                            return ordered_query.annotate(
                                custom_order=Case(
                                    *when_clauses,
                                    default=Value(len(combined_ids)),
                                    output_field=IntegerField(),
                                )
                            ).order_by('custom_order')[:config.get('max_results', 50)]
                
                # If no partial matches or processing failed, just return exact matches
                # Apply slice after ordering
                return exact_matches.order_by('pk')[:config.get('max_results', 50)]
            
            # If not prioritizing exact matches or no exact matches, use partial matching
            partial_queries = []
            for column in valid_columns:
                partial_queries.append(Q(**{f'{column}__icontains': search_query}))
                
            if partial_queries:
                partial_q = reduce(operator.or_, partial_queries)
                # Apply slice after ordering
                return base_query.filter(partial_q).order_by('pk')[:config.get('max_results', 50)]
            
            # Fall back to exact matches if no partial queries defined
            # Apply slice after ordering
            return exact_matches.order_by('pk')[:config.get('max_results', 50)]
        
        # If no exact queries, use contains only
        contains_queries = []
        for column in valid_columns:
            contains_queries.append(Q(**{f'{column}__icontains': search_query}))
            
        if contains_queries:
            contains_q = reduce(operator.or_, contains_queries)
            # Apply slice after ordering
            return base_query.filter(contains_q).order_by('pk')[:config.get('max_results', 50)]
        
        # If all else fails, return empty queryset
        return queryset.none()

    def apply_filters(self, queryset, request):
        """
        Apply additional filters based on request parameters.
        Optimized for performance.
        """
        filter_params = request.query_params.get('filters', None)
        
        if not filter_params:
            return queryset
            
        try:
            # Decode the URL-encoded filter params and parse JSON
            filter_params = json.loads(unquote(filter_params))
            model = queryset.model
            
            # Build a single query object instead of chaining filters
            filter_query = Q()
            
            # Apply each filter
            for filter_item in filter_params:
                field = filter_item.get('field')
                values = filter_item.get('values')
                
                if field and values and hasattr(model, field):
                    field_filter = Q()
                    for value in values:
                        field_filter |= Q(**{f'{field}__iexact': value})
                    filter_query &= field_filter
            
            # Apply all filters at once
            return queryset.filter(filter_query)
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Invalid filter format: {e}")
            return None  # Will be handled in the view
    
    def apply_sorting(self, queryset, request):
        """
        Apply sorting to the queryset based on request parameters.
        Optimized for performance and avoids reordering sliced querysets.
        """
        # Check if the queryset has been sliced already
        if hasattr(queryset, '_result_cache') and queryset._result_cache is not None:
            # If queryset is already evaluated/sliced, return it as is
            return queryset
            
        sort_field = request.query_params.get('sort', None)
        model = queryset.model
        
        if sort_field and hasattr(model, sort_field):
            sort_direction = request.query_params.get('sort_direction', 'asc')
            direction = '-' if sort_direction == 'desc' else ''
            return queryset.order_by(f'{direction}{sort_field}')
        
        # Default sorting by primary key if no search was performed
        pk_field = model._meta.pk.name
        return queryset.order_by(pk_field)