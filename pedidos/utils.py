from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.conf import settings
import os
from twilio.rest import Client
from django.conf import settings

def generar_pdf(pedido):
    """Genera un comprobante de compra en PDF"""
    ruta_pdf = os.path.join(settings.MEDIA_ROOT, f'comprobantes/pedido_{pedido.id}.pdf')

    os.makedirs(os.path.dirname(ruta_pdf), exist_ok=True)

    c = canvas.Canvas(ruta_pdf, pagesize=letter)
    c.drawString(100, 750, f"Comprobante de Compra - Pedido #{pedido.id}")
    c.drawString(100, 730, f"Cliente: {pedido.nombre_cliente}")
    c.drawString(100, 710, f"Contacto: {pedido.telefono_email}")
    c.drawString(100, 690, f"Método de Entrega: {pedido.get_metodo_entrega_display()}")
    c.drawString(100, 670, f"Método de Pago: {pedido.get_metodo_pago_display()}")
    c.drawString(100, 650, f"Total: ${pedido.total:.2f}")

    c.save()
    return ruta_pdf 

from twilio.rest import Client
from django.conf import settings

def enviar_whatsapp(pedido):
    """Envía un mensaje de WhatsApp con los detalles del pedido al admin y la confirmación al cliente"""
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    mensaje_admin = (
        f"📦 *Nuevo pedido #{pedido.id}*\n"
        f"👤 Cliente: {pedido.nombre_cliente}\n"
        f"📞 Contacto: {pedido.telefono_email}\n"
        f"🚚 Método de Entrega: {pedido.get_metodo_entrega_display()}\n"
        f"💳 Método de Pago: {pedido.get_metodo_pago_display()}\n"
        f"💰 Total: ${pedido.total:.2f}"
    )

    mensaje_cliente = (
        f"✅ *Compra confirmada #{pedido.id}*\n"
        f"Gracias por tu compra, {pedido.nombre_cliente}! 🎉\n"
        f"Tu pedido será procesado con el siguiente detalle:\n"
        f"🚚 Entrega: {pedido.get_metodo_entrega_display()}\n"
        f"💳 Pago: {pedido.get_metodo_pago_display()}\n"
        f"💰 Total: ${pedido.total:.2f}\n\n"
        f"Si tienes dudas, contáctanos. 📞"
    )

    # Enviar mensaje al administrador
    client.messages.create(
        from_='whatsapp:' + settings.TWILIO_PHONE_NUMBER,
        body=mensaje_admin,
        to=settings.ADMIN_WHATSAPP
    )

    # Si el contacto ingresado es un número de WhatsApp, enviamos la confirmación
    if pedido.telefono_email.startswith("+"):
        client.messages.create(
            from_='whatsapp:' + settings.TWILIO_PHONE_NUMBER,
            body=mensaje_cliente,
            to=f'whatsapp:{pedido.telefono_email}'
        )
