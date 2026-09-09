import json
from pathlib import Path

from django.conf import settings


PRODUCTOS_JSON = Path(settings.BASE_DIR) / 'catalogo' / 'data' / 'productos.json'


def carrito(request):
    carrito_sesion = request.session.get('carrito', {})
    if not carrito_sesion:
        return {'carrito_items': [], 'carrito_total': 0, 'carrito_cantidad': 0}

    with PRODUCTOS_JSON.open(encoding='utf-8') as archivo:
        productos = json.load(archivo)

    productos_por_id = {str(producto['id']): producto for producto in productos}
    items = []
    total = 0
    cantidad_total = 0

    for producto_id, cantidad in carrito_sesion.items():
        producto = productos_por_id.get(str(producto_id))
        if producto is None:
            continue
        cantidad = int(cantidad)
        subtotal = producto['precio'] * cantidad
        items.append({
            'producto': producto,
            'cantidad': cantidad,
            'subtotal': subtotal,
        })
        total += subtotal
        cantidad_total += cantidad

    return {
        'carrito_items': items,
        'carrito_total': total,
        'carrito_cantidad': cantidad_total,
    }
