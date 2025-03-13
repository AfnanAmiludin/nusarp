import logging
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from authentication.apis.viewsets import FormatViewSet
from master.models.area import Area
from master.apis.serializers import AreaSerializer
from rest_framework.response import Response
from core.utils.redis_cache import RedisCacheMixin

logger = logging.getLogger(__name__)

class AreaViewSet(FormatViewSet, viewsets.ModelViewSet):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    permission_classes = [IsAuthenticated]