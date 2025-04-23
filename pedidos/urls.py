from django.urls import path
from . import views

urlpatterns = [
    path('finalizar-compra/', views.finalizar_compra, name='finalizar_compra'),
    path('productos/', views.lista_productos, name='lista_productos'),
    path('productos/categoria/<int:categoria_id>/', views.lista_productos_por_categoria, name='lista_productos_por_categoria'),
    path('generar-comprobante/<int:compra_id>/', views.generar_comprobante, name='generar_comprobante'),
    path('subir-comprobante/<int:compra_id>/', views.subir_comprobante, name='subir_comprobante'),
    path('resumen-compra/<int:compra_id>/', views.resumen_compra, name='resumen_compra'),
    path('procesar-pago/<int:compra_id>/', views.procesar_pago, name='procesar_pago'),
    path('pagar-mercadopago/<int:compra_id>/', views.pagar_mercadopago, name='pagar_mercadopago'),
    path('compra-exitosa/<int:compra_id>/', views.compra_exitosa, name='compra_exitosa'),
    path('compra-fallida/<int:compra_id>/', views.compra_fallida, name='compra_fallida'),
    path('compra-pendiente/<int:compra_id>/', views.compra_pendiente, name='compra_pendiente'),
]
