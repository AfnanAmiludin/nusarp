from django.urls import path
from django.urls import re_path
from authentication import views

urlpatterns = [
    # Tambahkan URL di sini
    re_path(r'^login/$', views.TestView.as_view(), name='login'),
    re_path(r'^dashboard/$', views.DashboardView.as_view(), name='dashboard'),
    re_path(r'^user/$', views.UserView.as_view(), name='user'),
    re_path(r'^logout/$', views.LogoutView.as_view(), name='logout'),
]
