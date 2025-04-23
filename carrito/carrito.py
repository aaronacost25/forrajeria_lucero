from productos.models import Producto  # Asegúrate de importar tu modelo correctamente

class Carrito:
    def __init__(self, request):
        self.session = request.session
        carrito = self.session.get('carrito')
        if not carrito:
            carrito = self.session['carrito'] = {}
        self.carrito = carrito

    def __iter__(self):
        producto_ids = map(int, self.carrito.keys())
        productos = Producto.objects.filter(id__in=producto_ids)

        productos_dict = {producto.id: producto for producto in productos}

        for producto_id_str, item in self.carrito.items():
            producto_id = int(producto_id_str)
            producto = productos_dict.get(producto_id)

            if producto:
                yield {
                    'producto': producto,
                    'nombre': item['nombre'],
                    'imagen': item['imagen'],
                    'cantidad': item['cantidad'],
                    'precio': item['precio'],
                    'subtotal': item['precio'] * item['cantidad'],
                }



    def agregar(self, producto, cantidad=1):
        producto_id = str(producto.id)
        if producto_id not in self.carrito:
            self.carrito[producto_id] = {
                'producto_id': producto.id,
                'nombre': producto.nombre,
                'precio': float(producto.precio),
                'cantidad': cantidad,
                'imagen': producto.imagen.url if producto.imagen else ''
            }
        else:
            self.carrito[producto_id]['cantidad'] += cantidad
        self.guardar()

    def eliminar(self, producto):
        producto_id = str(producto.id)
        if producto_id in self.carrito:
            del self.carrito[producto_id]
            self.guardar()

    def restar(self, producto):
        producto_id = str(producto.id)
        if producto_id in self.carrito:
            self.carrito[producto_id]['cantidad'] -= 1
            if self.carrito[producto_id]['cantidad'] <= 0:
                self.eliminar(producto)
            else:
                self.guardar()

    def limpiar(self):
        self.session['carrito'] = {}
        self.session.modified = True

    def guardar(self):
        self.session['carrito'] = self.carrito
        self.session.modified = True

    def total_carrito(self):
        # Asegúrate de que 'precio' y 'cantidad' sean números (int o float)
        return sum(float(item['precio']) * int(item['cantidad']) for item in self.carrito.values())

    def obtener_total(self):
        total = 0
        for key, value in self.carrito.items():
            total += float(value["precio"]) * int(value["cantidad"])
        return total
