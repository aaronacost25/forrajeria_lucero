from django.contrib import admin
from .models import Categoria, Producto

class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria_padre')
    list_filter = ('categoria_padre',)

admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Producto)
