from core.models import MenuCategory

def sidebar_context(request):
    """Mengambil data kategori menu untuk semua template"""
    categories = MenuCategory.objects.prefetch_related('menus__submenus').all()
    return {'categories': categories}
