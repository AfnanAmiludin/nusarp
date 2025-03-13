class PrefetchRelatedMixin:
    """
    Mixin to provide efficient prefetching of related objects.
    """
    
    def get_related_fields(self):
        """
        Returns a dictionary mapping field names to related model fields.
        Override this in your ViewSet.
        
        Example:
        {
            'children': {
                'related_name': 'parent',  # Foreign key field pointing to parent
                'filter_kwargs': {'is_removed': False},  # Additional filters
                'property_name': 'children_list'  # Property to set on parent objects
            }
        }
        """
        return {}
    
    def prefetch_related_objects(self, queryset, objects=None):
        """
        Efficiently prefetch related objects for the given queryset or objects list.
        Can be used for both paginated and non-paginated results.
        """
        related_fields = self.get_related_fields()
        if not related_fields:
            return objects or queryset
            
        # If objects is provided, we're working with a already retrieved objects
        # (e.g., for paginated results)
        if objects is not None:
            model = queryset.model
            
            for field_name, config in related_fields.items():
                # Get the FK field on the related model pointing to the parent
                related_name = config.get('related_name')
                property_name = config.get('property_name', f'{field_name}_list')
                filter_kwargs = config.get('filter_kwargs', {})
                
                if not related_name:
                    continue
                
                # Get parent IDs from the current objects
                parent_ids = [getattr(obj, model._meta.pk.name) for obj in objects]
                
                # Fetch all related objects in a single query
                if parent_ids:
                    filter_kwargs[f'{related_name}_id__in'] = parent_ids
                    related_objects = model.objects.filter(**filter_kwargs)
                    
                    # Group related objects by parent ID
                    grouped_objects = {}
                    parent_id_field = f'{related_name}_id'
                    for related_obj in related_objects:
                        parent_id = getattr(related_obj, parent_id_field)
                        if parent_id not in grouped_objects:
                            grouped_objects[parent_id] = []
                        grouped_objects[parent_id].append(related_obj)
                    
                    # Attach related objects to their parents
                    for obj in objects:
                        obj_id = getattr(obj, model._meta.pk.name)
                        setattr(obj, property_name, grouped_objects.get(obj_id, []))
            
            return objects
            
        # For non-paginated results, just return the queryset
        # The serializer will handle the rest
        return queryset