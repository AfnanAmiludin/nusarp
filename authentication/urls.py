from django.urls import path
from django.urls import re_path
from authentication import views

urlpatterns = [
    # Tambahkan URL di sini
    re_path(r'^login/$', views.TestView.as_view(), name='login'),
]
