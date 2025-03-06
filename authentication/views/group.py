from django.shortcuts import render
from core.views import BaseView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

class GroupView(BaseView):
    """View untuk menampilkan data group"""
    template_name = 'group.html'
    
    @method_decorator(login_required)
    def get(self, request):
        context = self.get_context_data()
        return self.render_response(request, context)