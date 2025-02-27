from django.shortcuts import render
from django.views import View
from django.contrib.auth.decorators import login_required

class TestView (View):
    def get(self, request):
        return render(request, 'index.html')
    
class TerproteksiView(View):
    @login_required
    def get(request):
        return render(request, 'home.html')
    
class TidakTerproteksiView(View):
    def halaman_tidak_terproteksi(request):
        return render(request, 'pengalih.html')