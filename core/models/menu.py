from core import settings
from django.db import models

class MenuCategory(models.Model):
    id = models.AutoField(primary_key=True)  # Primary Key eksplisit
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Nama kategori menu, harus unik.",
        verbose_name="Nama Kategori"
    )
    order = models.IntegerField(
        default=0,
        help_text="Urutan tampilan kategori dalam sidebar.",
        verbose_name="Urutan"
    )

    class Meta:
        managed = True
        db_table = u'\"{}\".\"menu_category\"'.format(settings.SCHEMA)
        verbose_name = 'Used store menu category'

    def __str__(self):
        return self.name


class Menu(models.Model):
    id = models.AutoField(primary_key=True)  # Primary Key eksplisit
    title = models.CharField(
        max_length=255,
        unique=True,
        help_text="Nama menu yang akan ditampilkan di sidebar.",
        verbose_name="Judul Menu"
    )
    icon = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Class ikon untuk menu (contoh: 'ri-home-8-line').",
        verbose_name="Ikon"
    )
    url = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="URL tujuan menu. Kosongkan jika hanya sebagai kategori.",
        verbose_name="URL"
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='submenus',
        help_text="Parent menu jika ini adalah submenu.",
        verbose_name="Menu Induk"
    )
    category = models.ForeignKey(
        MenuCategory,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='menus',
        help_text="Kategori utama menu ini.",
        verbose_name="Kategori"
    )
    order = models.IntegerField(
        default=0,
        help_text="Urutan tampilan menu dalam kategori atau submenu.",
        verbose_name="Urutan"
    )

    class Meta:
        ordering = ['category__order', 'order']
        constraints = [
            models.UniqueConstraint(fields=['title', 'parent'], name='unique_menu_per_parent')
        ]
        managed = True
        db_table = u'\"{}\".\"menu\"'.format(settings.SCHEMA)
        verbose_name = 'Used store menu'

    def __str__(self):
        return self.title
