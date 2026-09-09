import json
from pathlib import Path

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse


PRODUCTOS_JSON = Path(settings.BASE_DIR) / 'catalogo' / 'data' / 'productos.json'
CLAVE_CARRITO = 'carrito'


def _cargar_productos():
	with PRODUCTOS_JSON.open(encoding='utf-8') as archivo:
		return json.load(archivo)


def _guardar_productos(productos):
	with PRODUCTOS_JSON.open('w', encoding='utf-8') as archivo:
		json.dump(productos, archivo, ensure_ascii=False, indent=2)


def login_view(request):
	if request.user.is_authenticated:
		return redirect('lista_productos')

	formulario = AuthenticationForm(request, data=request.POST or None)
	if request.method == 'POST' and formulario.is_valid():
		usuario = formulario.get_user()
		login(request, usuario)
		return redirect('lista_productos')

	return render(request, 'catalogo/login.html', {'formulario': formulario})


def logout_view(request):
	logout(request)
	return redirect('lista_productos')


def landing_page(request):
	return render(request, 'catalogo/landing.html')


def lista_productos(request):
	productos = _cargar_productos()
	consulta = request.GET.get('q', '').strip()
	if consulta:
		consulta = consulta.casefold()
		productos = [
			producto for producto in productos
			if consulta in producto['nombre'].casefold()
			or consulta in producto['categoria'].casefold()
		]

	total_registros = len(productos)
	con_stock = sum(1 for producto in productos if producto['stock'] > 0)
	contexto = {
		'productos': productos,
		'total_registros': total_registros,
		'con_stock': con_stock,
		'q': consulta,
	}
	return render(request, 'catalogo/lista.html', contexto)



def prueba(request):
	return HttpResponse('Vista de prueba del catalogo')


def detalle_producto(request, producto_id):
	productos = _cargar_productos()
	producto = next((producto for producto in productos if producto['id'] == producto_id), None)

	if producto is None:
		raise Http404('Producto no encontrado')

	return render(request, 'catalogo/detalle.html', {'producto': producto})


def _buscar_producto(productos, producto_id):
	return next((producto for producto in productos if producto['id'] == producto_id), None)


def agregar_al_carrito(request, producto_id):
	productos = _cargar_productos()
	producto = _buscar_producto(productos, producto_id)

	if producto is None:
		raise Http404('Producto no encontrado')
	if producto['stock'] <= 0:
		raise Http404('Producto sin stock')

	carrito = request.session.get(CLAVE_CARRITO, {})
	cantidad_actual = int(carrito.get(str(producto_id), 0))
	carrito[str(producto_id)] = min(cantidad_actual + 1, producto['stock'])
	request.session[CLAVE_CARRITO] = carrito
	return redirect('lista_productos')


def sumar_carrito(request, producto_id):
	agregar_al_carrito(request, producto_id)
	return redirect(f"{reverse('lista_productos')}?carrito=abierto#carritoOffcanvas")


def restar_carrito(request, producto_id):
	carrito = request.session.get(CLAVE_CARRITO, {})
	clave_producto = str(producto_id)

	if clave_producto in carrito:
		cantidad = int(carrito[clave_producto]) - 1
		if cantidad > 0:
			carrito[clave_producto] = cantidad
		else:
			carrito.pop(clave_producto)

	request.session[CLAVE_CARRITO] = carrito
	return redirect(f"{reverse('lista_productos')}?carrito=abierto#carritoOffcanvas")


def eliminar_del_carrito(request, producto_id):
	carrito = request.session.get(CLAVE_CARRITO, {})
	carrito.pop(str(producto_id), None)
	request.session[CLAVE_CARRITO] = carrito
	return redirect(f"{reverse('lista_productos')}?carrito=abierto#carritoOffcanvas")


def vaciar_carrito(request):
	request.session.pop(CLAVE_CARRITO, None)
	return redirect(f"{reverse('lista_productos')}?carrito=abierto#carritoOffcanvas")


def finalizar_compra(request):
	carrito = request.session.get(CLAVE_CARRITO, {})
	productos = _cargar_productos()

	seleccionados = []
	for clave_producto, cantidad in carrito.items():
		producto_id = int(clave_producto)
		producto = _buscar_producto(productos, producto_id)
		cantidad = int(cantidad)
		if producto is None:
			raise Http404('Producto no encontrado')
		if cantidad <= 0 or producto['stock'] < cantidad:
			raise Http404('Stock insuficiente')
		seleccionados.append((producto, cantidad))

	for producto, cantidad in seleccionados:
		producto['stock'] -= cantidad

	_guardar_productos(productos)
	request.session.pop(CLAVE_CARRITO, None)
	return redirect('lista_productos')


@login_required(login_url='login')
def editar_producto(request, producto_id):
	productos = _cargar_productos()
	producto = next((item for item in productos if item['id'] == producto_id), None)

	if producto is None:
		raise Http404('Producto no encontrado')

	if request.method == 'POST':
		producto['nombre'] = request.POST.get('nombre', '').strip()
		producto['categoria'] = request.POST.get('categoria', '').strip()
		producto['precio'] = int(request.POST.get('precio', producto['precio']))
		producto['stock'] = int(request.POST.get('stock', producto['stock']))
		producto['imagen'] = request.POST.get('imagen', '').strip()
		_guardar_productos(productos)
		return redirect('detalle_producto', producto_id=producto_id)

	return render(request, 'catalogo/formulario_producto.html', {'producto': producto, 'modo': 'Editar'})


@login_required(login_url='login')
def crear_producto(request):
	productos = _cargar_productos()

	if request.method == 'POST':
		producto = {
			'id': max((item['id'] for item in productos), default=0) + 1,
			'nombre': request.POST.get('nombre', '').strip(),
			'categoria': request.POST.get('categoria', '').strip(),
			'precio': int(request.POST.get('precio', 0)),
			'stock': int(request.POST.get('stock', 0)),
			'imagen': request.POST.get('imagen', '').strip(),
		}
		productos.append(producto)
		_guardar_productos(productos)
		return redirect('detalle_producto', producto_id=producto['id'])

	return render(request, 'catalogo/formulario_producto.html', {'modo': 'Crear'})


@login_required(login_url='login')
def eliminar_producto(request, producto_id):
	productos = _cargar_productos()
	productos_actualizados = [producto for producto in productos if producto['id'] != producto_id]

	if len(productos_actualizados) == len(productos):
		raise Http404('Producto no encontrado')

	_guardar_productos(productos_actualizados)
	return redirect('lista_productos')
