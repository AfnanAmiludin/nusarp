from core.models import MenuCategory, Menu

def seed():
    print("🔹 Menjalankan Menu Seeder...")

    # Hapus data lama
    Menu.objects.all().delete()
    MenuCategory.objects.all().delete()

    # Buat Kategori
    main_category = MenuCategory.objects.create(name="Main", order=1)
    authentication_category = MenuCategory.objects.create(name="Authentication", order=2)

    # Buat Menu Induk (Dashboard)
    dashboard_menu = Menu.objects.create(title="Dashboards", icon="ri-home-8-line", url="#", category=main_category, order=1)

    # Buat Menu Induk lainnya
    user_menu = Menu.objects.create(title="Users", icon="ri-user-2-line", url="/user", category=authentication_category, order=1)
    group_menu = Menu.objects.create(title="Groups", icon="ri-group-line", url="/group", category=authentication_category, order=2)

    print("✅ Menu Seeder selesai!")

