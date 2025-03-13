from django.urls import path
from django.urls import re_path
from master import views

urlpatterns = [
    # Tambahkan URL di sini
    re_path(r'^area/$', views.AreaView.as_view(), name='area'),
]