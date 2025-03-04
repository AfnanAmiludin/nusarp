import logging
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from authentication.models.user import User
from authentication.apis.serializers import UserSerializer
from rest_framework.response import Response

logger = logging.getLogger(__name__)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            print('AKU MASOKKKK')
            return Response(
                {"message": "User created successfully!", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(
            {"message": "Failed to create user", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
        
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User updated successfully!", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(
            {"message": "Failed to update user", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )