from core.views import BaseView
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


class AssetView(LoginRequiredMixin, PermissionRequiredMixin, BaseView):
    permission_required = 'authentication.view_asset'

    def get(self, request):
        return render(request, 'assets/index.html')
