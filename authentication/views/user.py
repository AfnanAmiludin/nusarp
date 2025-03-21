from django.shortcuts import render
from core.views import BaseView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


class UserView(LoginRequiredMixin, PermissionRequiredMixin, BaseView):
    permission_required = 'authentication.view_user'
    
    def get(self, request):
        return render(request, 'user.html')
