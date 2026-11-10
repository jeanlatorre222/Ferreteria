from django.contrib import admin
from .models import Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "categoria", "precio", "stock")
    search_fields = ("nombre", "categoria")
    list_filter = ("categoria",)
