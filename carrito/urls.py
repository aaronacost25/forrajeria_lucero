from django.urls import path
from . import views

urlpatterns = [
    path('agregar-al-carrito/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('restar/<int:producto_id>/', views.restar_producto, name='restar_producto'),
    path('limpiar/', views.limpiar_carrito, name='limpiar_carrito'),
    path('ver/', views.ver_carrito, name='ver_carrito'),
]
