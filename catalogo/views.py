import json
from pathlib import Path

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import PerfilDatosForm
from .models import ItemPedido, Pedido, Producto


PRODUCTOS_JSON = Path(settings.BASE_DIR) / 'catalogo' / 'data' / 'productos.json'
CLAVE_CARRITO = 'carrito'
CLAVE_SUBTOTALES_CARRITO = 'carrito_subtotales'


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


@login_required(login_url='login')
def perfil_view(request):
	usuario = request.user
	datos_iniciales = {
		'first_name': usuario.first_name,
		'last_name': usuario.last_name,
		'email': usuario.email,
	}
	formulario = PerfilDatosForm(request.POST or None, initial=datos_iniciales)

	if request.method == 'POST' and formulario.is_valid():
		usuario.first_name = formulario.cleaned_data['first_name']
		usuario.last_name = formulario.cleaned_data['last_name']
		usuario.email = formulario.cleaned_data['email']
		usuario.save(update_fields=['first_name', 'last_name', 'email'])
		messages.success(request, 'Tus datos personales se actualizaron correctamente.')
		return redirect('perfil')

	pedidos = Pedido.objects.filter(usuario=usuario).prefetch_related('items')
	return render(request, 'catalogo/perfil.html', {
		'formulario': formulario,
		'pedidos': pedidos,
		'cantidad_pedidos': pedidos.count(),
	})


def landing_page(request):
	productos_destacados = Producto.objects.filter(stock__gt=0).order_by('id')[:4]
	return render(request, 'catalogo/landing.html', {
		'productos_destacados': productos_destacados,
	})


def lista_productos(request):
	query = request.GET.get('q', '').strip()
	if query:
		productos = Producto.objects.filter(
			Q(nombre__icontains=query) | Q(categoria__icontains=query)
		)
	else:
		productos = Producto.objects.all()

	total_registros = productos.count()
	con_stock = productos.filter(stock__gt=0).count()
	contexto = {
		'productos': productos,
		'total_registros': total_registros,
		'con_stock': con_stock,
		'query': query,
	}
	return render(request, 'catalogo/lista.html', contexto)



def prueba(request):
	return HttpResponse('Vista de prueba del catalogo')


def detalle_producto(request, producto_id):
	producto = get_object_or_404(Producto, id=producto_id)
	return render(request, 'catalogo/detalle.html', {'producto': producto})


def _buscar_producto(productos, producto_id):
	return next((producto for producto in productos if producto['id'] == producto_id), None)


def _guardar_cantidad_carrito(request, producto, cantidad):
	clave_producto = str(producto.id)
	carrito = request.session.get(CLAVE_CARRITO, {})
	subtotales = request.session.get(CLAVE_SUBTOTALES_CARRITO, {})
	carrito[clave_producto] = cantidad
	subtotales[clave_producto] = producto.precio * cantidad
	request.session[CLAVE_CARRITO] = carrito
	request.session[CLAVE_SUBTOTALES_CARRITO] = subtotales


def agregar_al_carrito(request, producto_id):
	producto = get_object_or_404(Producto, id=producto_id)
	if producto.stock <= 0:
		raise Http404('Producto sin stock')

	carrito = request.session.get(CLAVE_CARRITO, {})
	cantidad_actual = int(carrito.get(str(producto_id), 0))
	_guardar_cantidad_carrito(request, producto, min(cantidad_actual + 1, producto.stock))
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
			producto = Producto.objects.filter(id=producto_id).first()
			if producto is not None:
				_guardar_cantidad_carrito(request, producto, cantidad)
			else:
				carrito.pop(clave_producto)
				request.session[CLAVE_CARRITO] = carrito
				subtotales = request.session.get(CLAVE_SUBTOTALES_CARRITO, {})
				subtotales.pop(clave_producto, None)
				request.session[CLAVE_SUBTOTALES_CARRITO] = subtotales
		else:
			carrito.pop(clave_producto)
			request.session[CLAVE_CARRITO] = carrito
			subtotales = request.session.get(CLAVE_SUBTOTALES_CARRITO, {})
			subtotales.pop(clave_producto, None)
			request.session[CLAVE_SUBTOTALES_CARRITO] = subtotales
	return redirect(f"{reverse('lista_productos')}?carrito=abierto#carritoOffcanvas")


def actualizar_cantidad_carrito(request, producto_id):
	if request.method != 'POST':
		return redirect('lista_productos')

	producto = Producto.objects.filter(id=producto_id).first()

	try:
		cantidad = int(request.POST.get('cantidad', '0'))
	except (TypeError, ValueError):
		messages.warning(request, 'Ingresa una cantidad válida.')
		cantidad = None

	carrito = request.session.get(CLAVE_CARRITO, {})
	subtotales = request.session.get(CLAVE_SUBTOTALES_CARRITO, {})
	clave_producto = str(producto_id)

	if producto is None:
		carrito.pop(clave_producto, None)
		subtotales.pop(clave_producto, None)
		messages.warning(request, 'El producto ya no existe y se eliminó del carrito.')
	elif cantidad is not None:
		if cantidad <= 0:
			carrito.pop(clave_producto, None)
			subtotales.pop(clave_producto, None)
		else:
			if cantidad > producto.stock:
				cantidad = producto.stock
				messages.warning(
					request,
					f"La cantidad se ajustó al stock disponible ({producto.stock}).",
				)
			if cantidad <= 0:
				carrito.pop(clave_producto, None)
				subtotales.pop(clave_producto, None)
			else:
				carrito[clave_producto] = cantidad
				subtotales[clave_producto] = producto.precio * cantidad

	request.session[CLAVE_CARRITO] = carrito
	request.session[CLAVE_SUBTOTALES_CARRITO] = subtotales
	url_anterior = request.META.get('HTTP_REFERER', '')
	if not url_anterior or not url_has_allowed_host_and_scheme(
		url_anterior,
		allowed_hosts={request.get_host()},
		require_https=request.is_secure(),
	):
		url_anterior = reverse('lista_productos')

	separador = '&' if '?' in url_anterior else '?'
	return redirect(f'{url_anterior}{separador}carrito=abierto#carritoOffcanvas')


def eliminar_del_carrito(request, producto_id):
	carrito = request.session.get(CLAVE_CARRITO, {})
	clave_producto = str(producto_id)
	carrito.pop(clave_producto, None)
	request.session[CLAVE_CARRITO] = carrito
	subtotales = request.session.get(CLAVE_SUBTOTALES_CARRITO, {})
	subtotales.pop(clave_producto, None)
	request.session[CLAVE_SUBTOTALES_CARRITO] = subtotales
	return redirect(f"{reverse('lista_productos')}?carrito=abierto#carritoOffcanvas")


def vaciar_carrito(request):
	request.session.pop(CLAVE_CARRITO, None)
	request.session.pop(CLAVE_SUBTOTALES_CARRITO, None)
	return redirect(f"{reverse('lista_productos')}?carrito=abierto#carritoOffcanvas")


@require_POST
def procesar_compra(request):
	carrito = request.session.get(CLAVE_CARRITO, {})
	if not carrito:
		messages.warning(request, 'El carrito está vacío.')
		return redirect('lista_productos')

	with transaction.atomic():
		seleccionados = []
		ids_obsoletos = []
		for clave_producto, cantidad in carrito.items():
			try:
				id_producto = int(clave_producto)
				cantidad = int(cantidad)
			except (TypeError, ValueError):
				messages.error(request, 'El carrito contiene un producto o una cantidad inválida.')
				return redirect('lista_productos')

			producto = Producto.objects.filter(id=id_producto).first()
			if producto is None:
				ids_obsoletos.append(clave_producto)
				continue

			if cantidad <= 0:
				messages.error(request, 'La cantidad de compra debe ser mayor que cero.')
				return redirect('lista_productos')
			if producto.stock < cantidad:
				messages.warning(
					request,
					f'Stock insuficiente para {producto.nombre}. Disponible: {producto.stock}.',
				)
				return redirect('lista_productos')

			seleccionados.append((producto, cantidad))

		if ids_obsoletos:
			for id_obsoleto in ids_obsoletos:
				carrito.pop(id_obsoleto, None)
			request.session[CLAVE_CARRITO] = carrito
			subtotales = request.session.get(CLAVE_SUBTOTALES_CARRITO, {})
			for id_obsoleto in ids_obsoletos:
				subtotales.pop(id_obsoleto, None)
			request.session[CLAVE_SUBTOTALES_CARRITO] = subtotales
			messages.warning(
				request,
				'Se eliminaron del carrito productos que ya no existen. Revisa y vuelve a finalizar la compra.',
			)
			return redirect('lista_productos')

		for producto, cantidad in seleccionados:
			producto.stock = max(producto.stock - cantidad, 0)
			producto.save()

		if request.user.is_authenticated:
			pedido = Pedido.objects.create(
				usuario=request.user,
				total=sum(producto.precio * cantidad for producto, cantidad in seleccionados),
			)
			ItemPedido.objects.bulk_create([
				ItemPedido(
					pedido=pedido,
					producto=producto,
					nombre_producto=producto.nombre,
					precio_unitario=producto.precio,
					cantidad=cantidad,
				)
				for producto, cantidad in seleccionados
			])

	request.session.pop(CLAVE_CARRITO, None)
	request.session.pop(CLAVE_SUBTOTALES_CARRITO, None)
	messages.success(request, 'La compra se procesó correctamente.')
	return redirect('lista_productos')


@login_required(login_url='login')
def editar_producto(request, producto_id):
	producto = get_object_or_404(Producto, id=producto_id)

	if request.method == 'POST':
		producto.nombre = request.POST.get('nombre', '').strip()
		producto.categoria = request.POST.get('categoria', '').strip()
		producto.precio = int(request.POST.get('precio', producto.precio))
		producto.stock = int(request.POST.get('stock', producto.stock))
		producto.imagen = request.POST.get('imagen', '').strip()
		producto.save()
		messages.success(request, 'El producto se actualizó correctamente.')
		return redirect('lista_productos')

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
@require_POST
def eliminar_producto(request, producto_id):
	producto = get_object_or_404(Producto, id=producto_id)
	producto.delete()
	messages.success(request, 'El producto se eliminó correctamente.')
	return redirect('lista_productos')