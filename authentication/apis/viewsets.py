import json
import logging
import sys
from collections import OrderedDict

from django.db import models
from django.db.models import Count
from django.http import QueryDict
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.core.cache import cache

logger = logging.getLogger(__name__)


def format_items(level_dict, level_items):
    if level_dict is None:
        return
    for key in level_dict:
        key_dict = level_dict[key]
        item = {'key': key}
        level_items.append(item)
        if 'count' in key_dict:
            item['count'] = key_dict['count']
        if 'summary' in key_dict:
            item['summary'] = key_dict['summary']
        if key_dict['items'] is None:
            item['items'] = None
        else:
            item['items'] = []
            format_items(key_dict['items'], item['items'])


class FormatViewSet(ModelViewSet):
    
    @property
    def cache_key(self):
        return f"{self.__class__.__name__}_queryset"

    def list(self, request, *args, **kwargs):
        cached_data = cache.get(self.cache_key)
        if cached_data:
            return Response(cached_data)

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        cache.set(self.cache_key, serializer.data, timeout=3600)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            cache.delete(self.cache_key)
            return Response(
                {"message": "Created successfully!", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(
            {"message": "Failed to create", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
        
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            cache.delete(self.cache_key)
            return Response(
                {"message": "Updated successfully!", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(
            {"message": "Failed to update", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
        
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        cache.delete(self.cache_key)
        return Response(
            {"message": "Deleted successfully!"},
            status=status.HTTP_204_NO_CONTENT
        )

    def _grouped_list(self, groups, queryset, request):
        require_group_count = request.query_params.get('requireGroupCount')
        require_total_count = request.query_params.get('requireTotalCount')
        if not isinstance(groups, list):
            groups = [groups]
        group_field_names = {self.get_group_field_name(group) for group in groups}
        ordering = self.get_ordering(groups)
        group_queryset = queryset.values(*group_field_names).annotate(count=Count('pk')).order_by(*ordering).distinct()
        group_summary = request.query_params.get('groupSummary')
        if group_summary is not None and group_summary:
            group_summary_list = group_summary if isinstance(group_summary, list) else [group_summary]
            group_queryset = self.add_summary_annotate(group_queryset, group_summary_list)
        page = self.paginate_queryset(group_queryset)
        response_dict = {}
        if require_group_count:
            response_dict['groupCount'] = group_queryset.count()
        if require_total_count:
            response_dict['totalCount'] = queryset.count()
        group_sets = page if page is not None else group_queryset
        data_dict = {}
        for row in group_sets:
            level_dict = data_dict
            for group in groups:
                group_field_name = self.get_group_field_name(group)
                key = row[group_field_name]
                key = key[0] if isinstance(key, list) else key
                if key in level_dict:
                    key_dict = level_dict[key]
                else:
                    key_dict = {}
                    level_dict[key] = key_dict
                if 'isExpanded' in group and group['isExpanded']:
                    if 'items' not in key_dict:
                        key_dict['items'] = {}
                    level_dict = key_dict['items']
                else:
                    key_dict['items'] = None
                    key_dict['count'] = row['count']
                    summary_pairs = list(filter(lambda current: current[0].startswith('gs__'), row.items()))
                    if summary_pairs:
                        summary_pairs.sort(key=lambda current: current[0])
                        summary = [current[1] for current in summary_pairs]
                        key_dict['summary'] = summary
        response_dict['data'] = []
        format_items(data_dict, response_dict['data'])
        return Response(response_dict)

    def _not_grouped_list(self, queryset, request):
        response_dict = OrderedDict()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response_dict['totalCount'] = self.paginator.count
        else:
            serializer = self.get_serializer(queryset, many=True)
        total_summary = request.query_params.get('totalSummary')
        if total_summary is not None and total_summary:
            total_summary_list = total_summary if isinstance(total_summary, list) else [total_summary]
            response_dict['summary'] = self.calc_total_summary(queryset, total_summary_list)
        response_dict['data'] = serializer.data
        return Response(response_dict)

    def get_group_field_name(self, group):
        if 'groupInterval' in group:
            return group['selector'].replace('.', '__') + '__' + group['groupInterval']
        else:
            return group['selector'].replace('.', '__')