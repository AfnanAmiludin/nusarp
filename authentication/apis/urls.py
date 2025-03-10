from django.urls import path, include
from rest_framework.routers import DefaultRouter
from authentication.apis import views

router = DefaultRouter()
router.register(r'user', views.UserViewSet, basename='user')
router.register(r'userpermission', views.UserPermissionViewSet, basename='userpermission')

urlpatterns = [
    path('', include(router.urls)),
]