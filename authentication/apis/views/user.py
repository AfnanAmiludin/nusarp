import logging
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from authentication.models.user import User
from authentication.apis.serializers import UserSerializer

logger = logging.getLogger(__name__)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]