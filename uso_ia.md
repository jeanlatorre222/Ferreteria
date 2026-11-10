# Registro del Uso de IA - Evaluación Sumativa 2

**Asignatura:** Programación Back End
**Estudiante:** Jean La Torre

---
### Parte 1
### 1. Creación del Modelo Producto (Etapa 1)
- **Prompt textual:**
  > En mi app Django 'catalogo', edita el archivo 'catalogo/models.py' para definir el modelo 'Producto' con los siguientes campos:
  > - nombre: CharField (max_length=150)
  > - categoria: CharField (max_length=100)
  > - precio: IntegerField
  > - stock: IntegerField
  > - imagen: URLField (max_length=500, blank=True, null=True)
  > Incluye el método __str__ devolviendo f"{self.nombre} - ${self.precio}".
- **Resumen de la respuesta:**
  La IA me generó la estructura de la clase `Producto` heredando de `models.Model` con los tipos de datos requeridos para la base de datos de la ferretería.
- **Usó o modificó antes de integrarla:**
  Se integró directamente en `catalogo/models.py` sin modificaciones.

---

### 2. Registro del Modelo en Django Admin (Etapa 2)
- **Prompt textual:**
  > En mi app Django 'catalogo', edita 'catalogo/admin.py' para registrar el modelo 'Producto'. 
  > Usa la clase 'ProductoAdmin' con:
  > - list_display mostrando 'id', 'nombre', 'categoria', 'precio' y 'stock'
  > - search_fields por 'nombre' y 'categoria'
  > - list_filter por 'categoria'
- **Resumen de la respuesta:**
  La IA configuró la clase `ProductoAdmin` en `admin.py` con filtros laterales por categoría, barra de búsqueda y columnas personalizadas para el panel de administración.
- **Usó o modificó antes de integrarla:**
  Se integró directamente sin modificaciones.

---

### 3. Generación de Fixture JSON (Etapa 3)
- **Prompt textual:**
  > Genera una fixture JSON de Django para el modelo 'catalogo.producto' con 40 productos de ferreteria chilenos realistas. 
  > Campos: nombre (string), categoria (string: Herramientas, Materiales, Electricidad, Gasfitería, Pinturas), precio (int, entre 1000 y 150000), stock (int, entre 0 y 50, donde al menos 8 productos tengan stock 0) e imagen (URL de Unsplash o similar).
  > Formato: lista de objetos con 'model', 'pk' (del 1 al 40) y 'fields', lista para cargar directamente con 'loaddata'.
- **Resumen de la respuesta:**
  La IA generó una lista JSON con 40 productos de ferretería formateados correctamente para Django.
- **Usó o modificó antes de integrarla:**
  Se guardó en `catalogo/fixtures/productos.json` y se cargó a SQLite usando el comando `python manage.py loaddata catalogo/fixtures/productos.json`.

---

### 4. Consultas ORM y Vistas Básicas (Etapa 3)
- **Prompt textual:**
  > En mi proyecto Django, modifica 'catalogo/views.py' para reemplazar la lectura manual del archivo JSON por consultas ORM a la base de datos SQLite:
  > 1. Importa el modelo 'Producto' desde '.models' y 'Q' desde 'django.db.models'.
  > 2. En la vista 'lista_productos':
  >    - Si existe un parámetro 'q' en request.GET, filtra los productos usando Producto.objects.filter() buscando por nombre o categoría (icontains).
  >    - Si no hay parámetro 'q', obtiene todos los productos con Producto.objects.all().
  >    - Calcula 'total_registros' usando .count() y 'con_stock' usando .filter(stock__gt=0).count().
  >    - Pasa 'productos', 'total_registros', 'con_stock' y 'query' al template 'catalogo/lista.html'.
  > 3. En 'detalle_producto', utiliza 'get_object_or_404(Producto, id=producto_id)' para obtener el producto desde la base de datos.
- **Resumen de la respuesta:**
  La IA reestructuró `views.py` para consultar la base de datos `db.sqlite3` mediante el ORM de Django en lugar de usar datos estáticos.
- **Usó o modificó antes de integrarla:**
  Se integró directamente sin modificaciones

---

### 5. Sincronización del Carrito con la Base de Datos y Corrección 404 (Etapa 3)
- **Prompt textual:**
  > Tengo dos problemas en mi app Django 'catalogo' tras migrar a SQLite:
  > 1. Algunos productos en el carrito dan 404 porque quedaron IDs antiguas guardadas.
  > 2. El stock se descuenta en la interfaz con JS pero no se actualiza en la base de datos SQLite.
  > 
  >  realiza lo siguiente:
  > 1. En 'views.py', crea una vista 'procesar_compra(request)' que reciba los IDs y cantidades compradas desde el carrito, reste la cantidad al atributo 'stock' del producto en la BD y ejecute 'producto.save()'.
  > 2. Registra la vista 'procesar_compra' en 'catalogo/urls.py'.
  > 3. En el script del carrito, actualiza la función de 'Finalizar Compra' para enviar una petición POST a 'procesar_compra' con el token CSRF.
  > 4. Asegúrate de que los enlaces usen {% url 'detalle_producto' producto.id %}.
- **Resumen de la respuesta:**
  La IA implementó la vista backend para procesar compras y actualizar dinámicamente el stock en la base de datos, además de corregir las etiquetas de URL en la plantilla.
- **Usó o modificó antes de integrarla:**
 Se integró directamente sin modificaciones



---

### 6. Edición y Eliminación de Productos 
- **Prompt textual:**
  > Tengo dos problemas en mi app Django 'catalogo' al editar y eliminar productos desde la interfaz web:
  > 1. Al presionar 'Editar', el formulario muestra el precio y stock antiguos en vez de los valores reales de la BD SQLite.
  > 2. El botón 'Eliminar' de la web no borra el registro en la base de datos y al presionar de nuevo da 404.
  > 
  > Realiza lo siguiente:
  > 1. En 'views.py', crea/actualiza 'editar_producto(request, producto_id)' para actualizar 'precio', 'stock', etc., con 'producto.save()'.
  > 2. En 'views.py', crea/actualiza 'eliminar_producto(request, producto_id)' ejecutando 'producto.delete()'.
  > 3. En 'catalogo/urls.py', asegura que las rutas existan para ambas vistas.
  > 4. En los templates/modales HTML, asegura que los inputs usen value="{{ producto.precio }}" y value="{{ producto.stock }}", y que el borrado envíe un POST con {% csrf_token %}.
- **Resumen de la respuesta:**
  La IA vinculó los formularios de la interfaz con los métodos .save() y .delete() del ORM de Django y corrigió la carga de valores en los campos de edición.
- **Usó o modificó antes de integrarla:**
  Se integró directamente sin modificaciones.---





### 6. Edición y Eliminación de Productos 
- **Prompt textual:**
  > Tengo dos problemas en mi app Django 'catalogo' al editar y eliminar productos desde la interfaz web:
  > 1. Al presionar 'Editar', el formulario muestra el precio y stock antiguos en vez de los valores reales de la BD SQLite.
  > 2. El botón 'Eliminar' de la web no borra el registro en la base de datos y al presionar de nuevo da 404.
  
- **Resumen de la respuesta:**
  La IA vinculó los formularios de la interfaz con los métodos .save() y .delete() del ORM de Django y corrigió la carga de valores en los campos de edición.
- **Usó o modificó antes de integrarla:**
  Se integró directamente sin modificaciones.













### Parte 2
Al realizar esta segunda evaluación volví a apoyarme en la IA para agilizar varios procesos como la migración
 de mi página pasando ademas de la lectura de archivos estáticos JSON que tenía en la evaluacion 1 a una base
 de datos SQLite administrada con el ORM de Django. Le pedí a la IA que me generara la estructura del modelo
 Producto en models.py con sus tipos de datos y la configuración del archivo admin.py para tener un panel de
 administración con búsquedas y filtros por categoría, lo cual me funciono sin la necesidad de modificar. También
 le pedí la lista de 40 productos en formato de fixture JSON con el prompt que dejo al final del pdf asi para 
no hacerlo a mano y cargarlos con el comando "python manage.py loaddata catalogo/fixtures/productos.json" 
segun la ia  además de actualizar las vistas para cambiar la lectura manual del JSON por consultas con el ORM.

Aunque durante el desarrollo tuve varios errores menores que tuve que solucionar. Por ejemplo, al cargar la fixture
 porque la ruta del archivo estaba errónea, además de errores de la misma página por las antiguas IDs, aunque
 lo más tardado fue hacer los productos a mano debido a las imágenes.