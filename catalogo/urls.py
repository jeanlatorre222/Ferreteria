from django.urls import path

from . import views

urlpatterns = [
    path('', views.lista_productos, name='lista_productos'),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('producto/editar/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    path('producto/eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('producto/crear/', views.crear_producto, name='crear_producto'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
