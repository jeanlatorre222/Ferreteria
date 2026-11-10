from django.db import models
from django.conf import settings

class Producto(models.Model):
    nombre = models.CharField(max_length=150)
    categoria = models.CharField(max_length=100)
    precio = models.IntegerField()
    stock = models.IntegerField()
    imagen = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} - ${self.precio}"


class Pedido(models.Model):
    class Estado(models.TextChoices):
        EN_PREPARACION = 'en_preparacion', 'En preparación'

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pedidos',
    )
    creado = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=24,
        choices=Estado.choices,
        default=Estado.EN_PREPARACION,
    )
    total = models.PositiveIntegerField()

    class Meta:
        ordering = ['-creado', '-id']

    def __str__(self):
        return f'Pedido #{self.id} - {self.usuario}'


class ItemPedido(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='items',
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='items_pedido',
    )
    nombre_producto = models.CharField(max_length=150)
    precio_unitario = models.PositiveIntegerField()
    cantidad = models.PositiveIntegerField()

    @property
    def subtotal(self):
        return self.precio_unitario * self.cantidad

    def __str__(self):
        return f'{self.nombre_producto} x {self.cantidad}'
