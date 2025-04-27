from django.db import models
from django.db.models import F
from django.core.exceptions import ValidationError
from TRABAJOS.models import OrdenServicio

class Unidad_Medida(models.Model):
    nombre = models.CharField(max_length=50)
    abreviatura = models.CharField(max_length=10,null=True, unique=True)

    def __str__(self):
        return f"{self.nombre} ({self.abreviatura})"

class Categoria(models.Model):
    Nombre=models.CharField(max_length=100)
    def __str__(self):
        return self.Nombre
    

class Articulo(models.Model):
    """Artículo base con datos comunes a cualquier entidad que lo referencie."""
    nombre = models.CharField(max_length=255)
    marca = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    codigo = models.CharField(max_length=50, unique=True, db_index=True)
    precio = models.FloatField()
    numero_serie = models.CharField(max_length=100, blank=True, null=True, unique=True, db_index=True)
    unidad_medida = models.ForeignKey(Unidad_Medida, on_delete=models.CASCADE, related_name='Unidad', null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='Categoria')

    def __str__(self):
        return f"{self.nombre} ({self.codigo}) - {self.marca if self.marca else 'Sin marca'}"

    # Validación del precio
    def clean(self):
        if self.precio < 0:
            raise ValidationError("El precio no puede ser negativo.")
        super().clean()

class Stock(models.Model):
    """Stock general del artículo en el depósito."""
    articulo_asociado = models.ForeignKey(Articulo, on_delete=models.CASCADE, related_name='stock')
    estado = models.CharField(max_length=50, default='Stock')
    cantidad = models.PositiveIntegerField(default=0)
    pendiente_a_entregar = models.PositiveIntegerField(default=0)

    def agregar_stock(self, cantidad):
        if cantidad > 0:
            self.cantidad += cantidad
            self.save()

    def reducir_stock(self, cantidad):
        if cantidad > 0 and self.cantidad >= cantidad:
            self.cantidad -= cantidad
            self.save()
            return True
        return False

    def __str__(self):
        return f"{self.articulo_asociado.nombre} - {self.cantidad} en stock"

class Bienes(models.Model):
    """Bienes asociados a un artículo, con su propia cantidad y tipo."""
    TIPO_BIENES = [
        ('uso', 'Bien de Uso'),
        ('consumo', 'Bien de Consumo'),
    ]
    articulo_asociado = models.ForeignKey(Articulo, on_delete=models.CASCADE, related_name='bienes')
    cantidad = models.PositiveIntegerField(default=0)
    licitacion = models.CharField(max_length=250)
    tipo = models.CharField(max_length=10, choices=TIPO_BIENES)
    requiere_identificador = models.BooleanField(default=False)

    def __str__(self):
        marca = f" ({self.articulo_asociado.marca})" if self.articulo_asociado.marca else ""
        return f"{self.articulo_asociado.nombre}{marca} - Cantidad: {self.cantidad}"

class UnidadBien(models.Model):
    bien = models.ForeignKey(Bienes, on_delete=models.CASCADE, related_name='unidades')
    identificador_unico = models.CharField(max_length=100, unique=True)
    disponible = models.BooleanField(default=True)
    ubicacion_actual = models.CharField(max_length=255, blank=True, null=True)  # Edificio/Dep
    estado = models.CharField(max_length=50, choices=[
        ('disponible', 'Disponible'),
        ('asignado', 'Asignado'),
        ('mantenimiento', 'Mantenimiento'),
        ('proceso_baja', 'En proceso de baja'),
        ('baja_confirmada', 'Baja confirmada')
    ], default='disponible')

    def __str__(self):
        return f"{self.identificador_unico} ({self.bien.articulo_asociado.nombre})"

    def asignar_ubicacion(unidad: 'UnidadBien', ubicacion: str):
        if not unidad.disponible:
            raise ValueError(f"La unidad {unidad} ya está asignada.")
        unidad.ubicacion_actual = ubicacion
        unidad.disponible = False
        unidad.estado = 'asignado'
        unidad.save()

    def devolver_unidad(unidad: 'UnidadBien'):
        unidad.disponible = True
        unidad.estado = 'proceso_baja'
        unidad.ubicacion_actual = 'Depósito central'  # o donde quieras ponerla temporalmente
        unidad.save()

    def confirmar_baja_unidad(unidad: 'UnidadBien'):
        if unidad.estado != 'proceso_baja':
            raise ValueError(f"La unidad {unidad} no está en proceso de baja.")
        unidad.delete()
        
class Provedor(models.Model):
    RazonSocial = models.CharField(max_length=100)  
    Direccion = models.CharField(max_length=100, blank=True)
    Email = models.EmailField()
    Telefono = models.CharField(max_length=15, blank=True, null=True)
    Estado = models.BooleanField(default=True)
    RUC = models.CharField(max_length=20, unique=True, blank=True, null=True) #Número de Identificación Fiscal
    Notas = models.TextField(blank=True, null=True)
    Categorizacion = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.RazonSocial  
     
class OrdenDeCompra(models.Model):
    numero_orden = models.CharField(max_length=50, unique=True)
    proveedor = models.ForeignKey('Proveedor', on_delete=models.SET_NULL, null=True, blank=True)
    fecha_orden = models.DateField(auto_now_add=True)

    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('finalizado', 'Finalizado'),
    )
    estado = models.CharField(max_length=15, choices=ESTADOS, default='pendiente')

    articulos = models.ManyToManyField('Articulo', through='ArticuloEnOrden', related_name='ordenes_de_compra')

    def __str__(self):
        return f"Orden #{self.numero_orden} - {self.estado}"

    def actualizar_estado(self):
        if all(aeo.entregado for aeo in self.articuloenorden_set.all()):
            self.estado = 'finalizado'
            self.save()

class ArticuloEnOrden(models.Model):
    orden = models.ForeignKey(OrdenDeCompra, on_delete=models.CASCADE)
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE)
    cantidad_pedida = models.PositiveIntegerField()
    cantidad_recibida = models.PositiveIntegerField(default=0)
    entregado = models.BooleanField(default=False)

    class Meta:
        unique_together = ('orden', 'articulo')

    def __str__(self):
        return f"{self.articulo} - Pedido: {self.cantidad_pedida} - Recibido: {self.cantidad_recibida}"

    def registrar_entrega(self, cantidad):
        stock, _ = Stock.objects.get_or_create(articulo_asociado=self.articulo)
        cantidad = max(0, cantidad)  # Previene negativos
        restante = self.cantidad_pedida - self.cantidad_recibida

        if cantidad > restante:
            cantidad = restante

        self.cantidad_recibida += cantidad
        stock.cantidad += cantidad
        stock.pendiente_a_entregar = max(0, stock.pendiente_a_entregar - cantidad)

        if self.cantidad_recibida >= self.cantidad_pedida:
            self.entregado = True

        stock.save()
        self.save()
        self.orden.actualizar_estado()

class BienesAsignados(models.Model):
    trabajo = models.ForeignKey(OrdenServicio, on_delete=models.CASCADE, related_name='bienes_usados')
    bien = models.ForeignKey(Bienes, on_delete=models.PROTECT)
    cantidad_usada = models.PositiveIntegerField()
    unidades_asignadas = models.ManyToManyField(UnidadBien, blank=True)

    def clean(self):
        if self.cantidad_usada > self.bien.cantidad:
            raise ValidationError("No se puede asignar más bienes de los disponibles.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

        self.bien.cantidad -= self.cantidad_usada
        self.bien.save()

        if self.bien.requiere_identificador:
            for unidad in self.unidades_asignadas.all():
                unidad.disponible = False
                unidad.save()

    def __str__(self):
        return f"{self.cantidad_usada} de {self.bien} en {self.trabajo}"

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100, blank=True, null=True)
    direccion = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.nombre or "Proveedor sin nombre"

class MaterialAsignado(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    trabajo = models.ForeignKey(OrdenServicio, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        if self.pk:
            original = MaterialAsignado.objects.get(pk=self.pk)
            diferencia = self.cantidad - original.cantidad
        else:
            diferencia = self.cantidad

        if diferencia > 0 and not self.stock.reducir_stock(diferencia):
            raise ValidationError("No hay suficiente stock para asignar esta cantidad.")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.stock.articulo_asociado.nombre} asignado a {self.trabajo}, existen: {self.cantidad} unidades"

class Sobrante(models.Model):
    material_asignado = models.ForeignKey(MaterialAsignado, on_delete=models.SET_NULL, related_name="sobrantes", null=True, blank=True)
    nombre = models.CharField(max_length=255)
    cantidad = models.PositiveIntegerField()
    trabajo_origen = models.ForeignKey(OrdenServicio, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.material_asignado:
            if not self.nombre:
                self.nombre = self.material_asignado.stock.articulo_asociado.nombre

            if self.pk:
                anterior = Sobrante.objects.get(pk=self.pk)
                diferencia = self.cantidad - anterior.cantidad
            else:
                diferencia = self.cantidad

            if diferencia > self.material_asignado.cantidad:
                raise ValidationError("No hay suficiente stock asignado para registrar este sobrante.")

            self.material_asignado.cantidad = F('cantidad') - diferencia
            self.material_asignado.save()
            self.material_asignado.refresh_from_db()

            if self.material_asignado.cantidad <= 0:
                self.material_asignado.delete()
                self.material_asignado = None

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} - {self.cantidad} unidades"

class SobranteAsignado(models.Model):
    trabajo = models.ForeignKey(OrdenServicio, on_delete=models.CASCADE, related_name='sobrantes_usados')
    nombre = models.CharField(max_length=255)
    sobrante = models.ForeignKey(Sobrante, on_delete=models.SET_NULL, null=True, blank=True)
    cantidad_usada = models.PositiveIntegerField()

    def clean(self):
        if not self.sobrante_id:
            raise ValidationError("El sobrante debe estar guardado antes de asignarlo.")

        if self.cantidad_usada > self.sobrante.cantidad:
            raise ValidationError("No se puede usar más sobrante del disponible.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

        self.sobrante.cantidad -= self.cantidad_usada
        if self.sobrante.cantidad <= 0:
            self.sobrante.delete()
        else:
            self.sobrante.save()

    def __str__(self):
        return f"{self.cantidad_usada} de {self.nombre} en {self.trabajo}"

class MaterialUtilizado(models.Model):
    trabajo = models.ForeignKey(OrdenServicio, on_delete=models.CASCADE, related_name="materiales_utilizados")
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.cantidad} de {self.stock.articulo_asociado.nombre} en {self.trabajo}"
