from django.shortcuts import redirect, get_object_or_404, render
from productos.models import Producto
from .carrito import Carrito

def agregar_al_carrito(request, producto_id):
    carrito = Carrito(request)
    producto = get_object_or_404(Producto, id=producto_id)
    carrito.agregar(producto=producto)
    print(request.session['carrito'])  # <-- Agregá esto
    return redirect('ver_carrito')


def eliminar_producto(request, producto_id):
    carrito = Carrito(request)
    producto = get_object_or_404(Producto, id=producto_id)
    carrito.eliminar(producto)
    return redirect('ver_carrito')

def restar_producto(request, producto_id):
    carrito = Carrito(request)
    producto = get_object_or_404(Producto, id=producto_id)
    carrito.restar(producto)
    return redirect('ver_carrito')

def limpiar_carrito(request):
    carrito = Carrito(request)
    carrito.limpiar()
    return redirect('ver_carrito')
def ver_carrito(request):
    carrito = Carrito(request)
    localidad = request.POST.get('localidad') or request.session.get('localidad', '')
    request.session['localidad'] = localidad  # Guardamos la localidad en sesión

    total = carrito.total_carrito()
    envio = 0

    zonas_envio_gratis = ['Mayu Sumaj', 'San Antonio', 'Icho Cruz']

    if localidad in zonas_envio_gratis:
        if total < 50000:
            envio = 3500
    elif localidad == 'Otro':
        envio = 3000

    total_final = total + envio

    # Lista de productos en el carrito
    productos = list(carrito)  # carrito.__iter__() también funciona

    context = {
        'carrito': carrito,
        'productos': productos,
        'total': total,
        'envio': envio,
        'total_final': total_final,
        'localidad': localidad,
    }

    return render(request, 'carrito/carrito.html', context)
 