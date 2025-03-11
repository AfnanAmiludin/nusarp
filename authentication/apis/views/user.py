import logging
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from authentication.apis.viewsets import FormatViewSet
from authentication.models.user import User
from authentication.apis.serializers import UserSerializer
from rest_framework.response import Response
from core.utils.redis_cache import RedisCacheMixin

logger = logging.getLogger(__name__)

class UserViewSet(FormatViewSet, viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]