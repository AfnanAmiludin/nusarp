from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin

class TestView(View):
    def post(self, request):
        user_name = request.POST.get('user_name')
        password = request.POST.get('password')
        user = authenticate(request, user_name=user_name, password=password)
        print("MASOKKK22", user_name)
        print("MASOKKK22", password)
        if user is not None:
            
            login(request, user)
            messages.success(request, f'Login berhasil! Selamat datang, {user.user_name}')
            return redirect('dashboard')  # Pastikan URL-nya benar
        else:
            messages.error(request, 'Username atau password salah. Silakan coba lagi.')

        return render(request, 'login.html')

    def get(self, request):
        return render(request, 'login.html')
    
class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, 'Anda berhasil logout.')
        return redirect('login')

class DashboardView (LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'dashboard.html')
