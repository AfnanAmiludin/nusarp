from django.urls import path, include
from rest_framework.routers import DefaultRouter
from authentication.apis import views

router = DefaultRouter()
router.register(r'asset', views.AssetViewSet, basename='asset')

urlpatterns = [
    path('', include(router.urls)),
]
