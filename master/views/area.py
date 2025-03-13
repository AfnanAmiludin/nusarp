from django.shortcuts import render
from core.views import BaseView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

class AreaView(BaseView, LoginRequiredMixin, PermissionRequiredMixin):
    permission_required = [
        "view_area",
    ]
    def get(self, request):
        return render(request, 'area.html')
