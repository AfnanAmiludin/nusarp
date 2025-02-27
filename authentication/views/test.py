from django.shortcuts import render
from django.views import View
from django.contrib.auth.decorators import login_required

class TestView (View):
    def get(self, request):
        return render(request, 'login.html')


class DashboardView (View):
    def get(self, request):
        return render(request, 'dashboard.html')
