import json
from pathlib import Path

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render


PRODUCTOS_JSON = Path(settings.BASE_DIR) / 'catalogo' / 'data' / 'productos.json'


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


def lista_productos(request):
	productos = _cargar_productos()
	total_registros = len(productos)
	con_stock = sum(1 for producto in productos if producto['stock'] > 0)
	contexto = {
		'productos': productos,
		'total_registros': total_registros,
		'con_stock': con_stock,
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
