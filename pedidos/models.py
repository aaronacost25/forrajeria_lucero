from django.db import models

class Pedido(models.Model):
    METODO_ENTREGA = [
        ('local', 'Retiro en el local'),
        ('cadete', 'Envío por cadete (+$3000, solo Carlos Paz)')
    ]

    METODO_PAGO = [
        ('transferencia', 'Transferencia bancaria'),
        ('tarjeta', 'Tarjeta de débito/crédito')
    ]

    nombre_cliente = models.CharField(max_length=255)
    telefono_email = models.CharField(max_length=255)
    metodo_entrega = models.CharField(max_length=10, choices=METODO_ENTREGA)
    metodo_pago = models.CharField(max_length=15, choices=METODO_PAGO)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido {self.id} - {self.nombre_cliente}" 


class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    categoria_padre = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='subcategorias'
    )

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre


class Compra(models.Model):
    producto = models.CharField(max_length=100)
    cantidad = models.PositiveIntegerField()
    precio = models.FloatField()
    cliente_nombre = models.CharField(max_length=100)
    metodo_pago = models.CharField(max_length=50)
    comprobante = models.FileField(upload_to='comprobantes/', null=True, blank=True)
    estado = models.CharField(max_length=20, default="pendiente")
    fecha = models.DateTimeField(auto_now_add=True)
    localidad = models.CharField(max_length=100, blank=True, null=True)


    def __str__(self):
        return f"{self.cliente_nombre} - {self.producto} ({self.metodo_pago})"
