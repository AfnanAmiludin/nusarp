from core.models import MenuCategory, Menu

def seed():
    print("🔹 Menjalankan Menu Seeder...")

    # Hapus data lama
    Menu.objects.all().delete()
    MenuCategory.objects.all().delete()

    # Buat Kategori
    main_category = MenuCategory.objects.create(name="Main", order=1)
    general_category = MenuCategory.objects.create(name="General", order=2)

    # Buat Menu Induk (Dashboard)
    dashboard_menu = Menu.objects.create(title="Dashboards", icon="ri-home-8-line", url="#", category=main_category, order=1)

    # Submenu Dashboards
    sales_menu = Menu.objects.create(title="Sales", parent=dashboard_menu, url="#", order=2)
    ecommerce_menu = Menu.objects.create(title="Ecommerce", parent=dashboard_menu, url="#", order=3)
    crypto_menu = Menu.objects.create(title="Crypto", parent=dashboard_menu, url="#", order=4)

    # Submenu level 2 untuk "Sales"
    sales_reports = Menu.objects.create(title="Reports", parent=sales_menu, url="sales_reports.html", order=1)
    sales_analytics = Menu.objects.create(title="Analytics", parent=sales_menu, url="sales_analytics.html", order=2)

    # Submenu level 2 untuk "Ecommerce"
    ecommerce_products = Menu.objects.create(title="Products", parent=ecommerce_menu, url="products.html", order=1)
    ecommerce_orders = Menu.objects.create(title="Orders", parent=ecommerce_menu, url="orders.html", order=2)

    # Submenu level 3 untuk "Products" dari Ecommerce
    ecommerce_products_add = Menu.objects.create(title="Add Product", parent=ecommerce_products, url="add_product.html", order=1)
    ecommerce_products_list = Menu.objects.create(title="Product List", parent=ecommerce_products, url="product_list.html", order=2)

    # Buat Menu Induk lainnya
    components_menu = Menu.objects.create(title="Components", icon="ri-inbox-line", url="#", category=general_category, order=1)

    # Submenu Components
    accordion_menu = Menu.objects.create(title="Accordion", parent=components_menu, url="#", order=1)
    alerts_menu = Menu.objects.create(title="Alerts", parent=components_menu, url="#", order=2)

    # Submenu level 2 untuk "Accordion"
    accordion_basic = Menu.objects.create(title="Basic", parent=accordion_menu, url="accordion_basic.html", order=1)
    accordion_advanced = Menu.objects.create(title="Advanced", parent=accordion_menu, url="accordion_advanced.html", order=2)

    print("✅ Menu Seeder selesai!")

