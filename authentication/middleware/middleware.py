from django.shortcuts import redirect
from django.contrib import messages

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated and request.path != '/login/':
            messages.error(request, 'Anda harus login terlebih dahulu.')
            return redirect('login')
        return self.get_response(request)