from django.shortcuts import render
from core.views import BaseView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

class UserView(BaseView):
    """View untuk menampilkan data user"""
    template_name = 'user.html'
    
    # @method_decorator(login_required)
    def get(self, request):
        context = self.get_context_data()
        return self.render_response(request, context)
