from django.shortcuts import render, get_object_or_404
from .models import Producto, Categoria

def lista_productos(request):
    categorias = Categoria.objects.filter(categoria_padre__isnull=True)  # Solo las categorías principales
    subcategorias = Categoria.objects.filter(categoria_padre__isnull=False)  # Subcategorías
    productos = Producto.objects.all()  # Obtener todos los productos

    return render(request, 'pedidos/lista_productos.html', {
        'categorias': categorias,
        'subcategorias': subcategorias,
        'productos': productos,  # Agregar esto para que los productos se vean
    })