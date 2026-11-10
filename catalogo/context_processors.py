from .models import Producto


def carrito(request):
    carrito_sesion = request.session.get('carrito', {})
    if not carrito_sesion:
        return {'carrito_items': [], 'carrito_total': 0, 'carrito_cantidad': 0}

    ids_producto = []
    for producto_id in carrito_sesion:
        try:
            ids_producto.append(int(producto_id))
        except (TypeError, ValueError):
            continue

    productos_por_id = {
        str(producto.id): producto
        for producto in Producto.objects.filter(id__in=ids_producto)
    }
    items = []
    total = 0
    cantidad_total = 0

    for producto_id, cantidad in carrito_sesion.items():
        producto = productos_por_id.get(str(producto_id))
        if producto is None:
            continue
        try:
            cantidad = int(cantidad)
        except (TypeError, ValueError):
            continue
        subtotal = producto.precio * cantidad
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
