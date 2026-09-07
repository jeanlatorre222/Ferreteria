from django.http import HttpResponse


def prueba(request):
	return HttpResponse('Vista de prueba del catalogo')
