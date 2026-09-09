from django.urls import path

from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('productos/', views.lista_productos, name='lista_productos'),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/sumar/<int:producto_id>/', views.sumar_carrito, name='sumar_carrito'),
    path('carrito/restar/<int:producto_id>/', views.restar_carrito, name='restar_carrito'),
    path('carrito/eliminar/<int:producto_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('carrito/vaciar/', views.vaciar_carrito, name='vaciar_carrito'),
    path('carrito/finalizar/', views.finalizar_compra, name='finalizar_compra'),
    path('producto/editar/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    path('producto/eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('producto/crear/', views.crear_producto, name='crear_producto'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
