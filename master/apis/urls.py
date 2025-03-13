from django.urls import path, include
from rest_framework.routers import DefaultRouter
from master.apis import views

router = DefaultRouter()
router.register(r'area', views.AreaViewSet, basename='area')

urlpatterns = [
    path('', include(router.urls)),
]