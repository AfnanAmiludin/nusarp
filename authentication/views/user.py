from django.shortcuts import render
from core.views import BaseView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

class UserView(BaseView):
    def get(self, request):
        return render(request, 'user.html')
