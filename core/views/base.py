from django.shortcuts import render
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

class BaseView(View):
    """Base view class untuk menangani rendering dengan iframe detection"""
    template_name = None
    
    def get_context_data(self, **kwargs):
        context = kwargs
        return context
    
    def render_response(self, request, context):
        # Deteksi apakah request dari iframe
        is_iframe = request.GET.get('iframe', 'false') == 'true'
        context['is_iframe'] = is_iframe
        
        return render(request, self.template_name, context)
