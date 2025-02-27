from django.urls import path
from django.urls import re_path
from authentication import views

urlpatterns = [
    # Tambahkan URL di sini
    re_path(r'^login/$', views.TestView.as_view(), name='login'),
    re_path(r'^pengalih/$', views.TidakTerproteksiView.as_view(), name='pengalih'),
    re_path(r'^terproteksi/$', views.TerproteksiView.as_view(), name='terproteksi'),
]