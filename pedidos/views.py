from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from django.core.files.storage import default_storage
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime
import mercadopago
import os 

from .models import Compra
from productos.models import Producto, Categoria
def seleccionar_localidad(request):
    if request.method == 'POST':
        localidad = request.POST.get('localidad')
        costos_envio = {
            'Mayu Sumaj': 3000,
            'San Antonio': 3000,
            'Icho Cruz': 3000,
            'Otro': 0
        }
        request.session['localidad'] = localidad
        request.session['envio'] = costos_envio.get(localidad, 0)
        return redirect('finalizar_compra')

    return render(request, 'pedidos/seleccionar_localidad.html')

def escoger_entrega(request):
    if request.method == 'POST':
        metodo_entrega = request.POST.get('metodo_entrega')

        if metodo_entrega == 'retiro':
            request.session['metodo_entrega'] = 'retiro'
            request.session['localidad'] = 'Local'  # O lo que uses por defecto
            request.session['envio'] = 0
        else:
            request.session['metodo_entrega'] = 'envio'
            # Redireccionamos a la misma selección de localidad de antes
            return redirect('seleccionar_localidad')  

        return redirect('finalizar_compra')

    return render(request, 'pedidos/escoger_entrega.html')

def lista_productos_por_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)

    # Obtener esta categoría + sus subcategorías
    subcategorias = categoria.subcategorias.all()
    ids_categorias = [categoria.id] + [sub.id for sub in subcategorias]

    # Filtrar productos que pertenezcan a cualquiera de esas categorías
    productos = Producto.objects.filter(categoria__id__in=ids_categorias)

    categorias = Categoria.objects.filter(categoria_padre__isnull=True)
    todas_subcategorias = Categoria.objects.filter(categoria_padre__isnull=False)

    return render(request, 'pedidos/lista_productos.html', {
        'productos': productos,
        'categoria': categoria,
        'categorias': categorias,
        'subcategorias': todas_subcategorias,
    })

def compra_exitosa(request, compra_id):
    compra = get_object_or_404(Compra, id=compra_id)
    return render(request, 'pedidos/compra_exitosa.html', {'compra': compra})
def compra_fallida(request):
    return render(request, 'pedidos/compra_fallida.html')
def compra_pendiente(request):
    return render(request, 'pedidos/compra_pendiente.html')

# Vista para finalizar una compra
from django.shortcuts import render, redirect
from carrito.carrito import Carrito
from pedidos.models import Compra  # Asegurate de importar tu modelo
from django.http import HttpResponse
import urllib.parse

def generar_link_whatsapp(mensaje):
    numero = "5493541620247"  # número con código país (sin +)
    mensaje_encoded = urllib.parse.quote(mensaje)
    return f"https://wa.me/{numero}?text={mensaje_encoded}"

from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Compra
import urllib.parse

def generar_link_whatsapp(mensaje):
    numero = "5493541620247"
    mensaje_codificado = urllib.parse.quote(mensaje)
    return f"https://wa.me/{numero}?text={mensaje_codificado}"

def finalizar_compra(request):
    carrito = Carrito(request)

    if request.method == 'POST':
        try:
            cliente_nombre = request.POST.get('nombre') or 'Anónimo'
            metodo_pago = request.POST.get('metodo_pago')
            metodo_entrega = request.POST.get('metodo_entrega') or 'retiro'

            # Guardamos el método de entrega en la sesión
            request.session['metodo_entrega'] = metodo_entrega

            if not metodo_pago:
                return render(request, 'pedidos/finalizar_compra.html', {
                    'error': 'Debe seleccionar un método de pago.',
                    'carrito': carrito
                })

            localidad = request.session.get('localidad', 'Otro')
            costo_envio = request.session.get('envio', 0)

            total = 0
            for item in carrito:
                Compra.objects.create(
                    producto=item['producto'],
                    cantidad=item['cantidad'],
                    precio=item['precio'],
                    cliente_nombre=cliente_nombre,
                    metodo_pago=metodo_pago,
                    localidad=localidad
                )
                total += item['precio'] * item['cantidad']

            total_final = total + (costo_envio if metodo_entrega == 'envio' else 0)

            if metodo_pago == "transferencia":
                return render(request, 'pedidos/transferencia.html', {
                    'carrito': carrito,
                    'cliente_nombre': cliente_nombre,
                    'total': total_final,
                    'costo_envio': costo_envio,
                    'metodo_entrega': metodo_entrega
                })

            elif metodo_pago == "tarjeta":
                ultima_compra = Compra.objects.filter(cliente_nombre=cliente_nombre).last()
                return redirect('pagar_mercadopago', compra_id=ultima_compra.id)

            elif metodo_pago == "efectivo":
                mensaje = (
                    f"🛒 *Nueva compra en efectivo*%0A"
                    f"👤 Cliente: {cliente_nombre}%0A"
                    f"📍 Localidad: {localidad}%0A"
                    f"🚚 Entrega: {'Envío a domicilio' if metodo_entrega == 'envio' else 'Retiro en el local'}%0A%0A"
                    f"📦 Productos:%0A"
                )

                for item in carrito:
                    subtotal = item['precio'] * item['cantidad']
                    mensaje += f"- {item['nombre']} x {item['cantidad']} = ${subtotal}%0A"

                if metodo_entrega == 'envio':
                    mensaje += f"%0A🚚 Costo de envío: ${costo_envio}%0A"

                mensaje += f"%0A💰 Total: ${total_final}%0A"
                mensaje += "%0A📍 Dirección del local: https://g.co/kgs/CbiCBXx"

                link_whatsapp = generar_link_whatsapp(mensaje)

                return render(request, 'pedidos/efectivo.html', {
                    'carrito': carrito,
                    'cliente_nombre': cliente_nombre,
                    'localidad': localidad,
                    'total': total_final,
                    'costo_envio': costo_envio,
                    'metodo_entrega': metodo_entrega,
                    'link_whatsapp': link_whatsapp
                })

        except Exception as e:
            return HttpResponse(f"Ocurrió un error: {e}")

    return render(request, 'pedidos/finalizar_compra.html', {
        'carrito': carrito
    })
    


# Vista para procesar pagos manuales (tarjeta)
def procesar_pago(request, compra_id):
    compra = get_object_or_404(Compra, id=compra_id)

    if request.method == 'POST':
        # Simulación de pago
        compra.estado = 'pagado'
        compra.save()
        return render(request, 'pago_exitoso.html', {'compra': compra})

    return render(request, 'pedidos/tarjeta.html', {'compra': compra})

def pagar_mercadopago(request, compra_id):
    compra = get_object_or_404(Compra, id=compra_id)

    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

    envio = 0
    localidades_envio_gratis = ["Mayu Sumaj", "San Antonio", "Icho Cruz"]
    if compra.localidad in localidades_envio_gratis:
        if compra.precio < 50000:
            envio = 3500
    else:
        envio = 3000

    items = [
        {
            "title": str(compra.producto),
            "quantity": int(compra.cantidad),
            "unit_price": float(compra.precio),
            "currency_id": "ARS",
        }
    ]

    if envio > 0:
        items.append({
            "title": "Costo de envío",
            "quantity": 1,
            "unit_price": envio,
            "currency_id": "ARS",
        })

    preference_data = {
        "items": items,
        "payer": {
            "name": compra.cliente_nombre,
        },
        "back_urls": {
            "success": request.build_absolute_uri(f"/compra-exitosa/{compra.id}/"),
            "failure": request.build_absolute_uri(f"/compra-fallida/{compra.id}/"),
            "pending": request.build_absolute_uri(f"/compra-pendiente/{compra.id}/")
        },
        "auto_return": "approved",
        "external_reference": str(compra.id)
    }

    preference_response = sdk.preference().create(preference_data)
    preference = preference_response["response"]

    return redirect(preference["init_point"])

# Vista para generar comprobante PDF
def generar_comprobante(request, compra_id):
    compra = get_object_or_404(Compra, id=compra_id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="comprobante_{compra.id}.pdf"'

    envio = 0
    localidades_envio_gratis = ["Mayu Sumaj", "San Antonio", "Icho Cruz"]
    if compra.localidad in localidades_envio_gratis:
        if compra.precio < 50000:
            envio = 3500
    else:
        envio = 3000

    total = compra.precio + envio

    p = canvas.Canvas(response, pagesize=letter)
    p.setFont("Helvetica", 12)
    p.drawString(100, 750, "Comprobante de Compra")
    p.drawString(100, 730, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    p.drawString(100, 710, f"Cliente: {compra.cliente_nombre}")
    p.drawString(100, 690, f"Producto: {compra.producto}")
    p.drawString(100, 670, f"Cantidad: {compra.cantidad}")
    p.drawString(100, 650, f"Precio: ${compra.precio}")
    p.drawString(100, 630, f"Localidad: {compra.localidad}")
    p.drawString(100, 610, f"Costo de Envío: ${envio}")
    p.drawString(100, 590, f"Método de Pago: {compra.metodo_pago}")
    p.drawString(100, 570, f"Total Final: ${total}")
    p.showPage()
    p.save()

    return response


# Vista para subir comprobante (ej: transferencia)
def subir_comprobante(request, compra_id):
    if request.method == 'POST' and request.FILES.get('comprobante'):
        compra = get_object_or_404(Compra, id=compra_id)
        archivo = request.FILES['comprobante']
        ruta = default_storage.save(f'comprobantes/{archivo.name}', archivo)

        compra.comprobante = ruta
        compra.estado = "en revisión"
        compra.save()

        return redirect('compra_exitosa')

    return HttpResponse("Error al subir comprobante", status=400)

# Vista de resumen de compra
def resumen_compra(request, compra_id):
    compra = get_object_or_404(Compra, id=compra_id)
    return render(request, 'pedidos/resumen_compra.html', {'compra': compra})

from django.shortcuts import render, get_object_or_404
from productos.models import Producto, Categoria


from django.shortcuts import render
from .models import Categoria

from productos.models import Producto, Categoria  # ✅ Correcto

def lista_productos(request):
    categorias = Categoria.objects.filter(categoria_padre__isnull=True)
    subcategorias = Categoria.objects.filter(categoria_padre__isnull=False)
    productos = Producto.objects.all()

    # Obtener el carrito desde la sesión (si existe)
    carrito = request.session.get('carrito', {})
    total_items = sum(item['cantidad'] for item in carrito.values())

    return render(request, 'pedidos/lista_productos.html', {
        'categorias': categorias,
        'subcategorias': subcategorias,
        'productos': productos,
        'total_items_carrito': total_items,  # Esta es la variable que usará el HTML
    })
