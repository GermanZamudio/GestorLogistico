from django.db import models
from django.db.models import F

class TipoContenedorDispositivo(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre
    
class TipoEstado(models.Model):
    nombre = models.CharField(max_length=50)  # Ej: "Dispositivo", "Orden de Servicio"

    def __str__(self):
        return self.nombre


class Estado(models.Model):
    nombre = models.CharField(max_length=100)
    tipo = models.ForeignKey(TipoEstado, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"

class ContenedorDispositivos(models.Model):
    nombre = models.CharField(max_length=150)
    tipo = models.ForeignKey(TipoContenedorDispositivo, on_delete=models.PROTECT)
    codigo= models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"


class Dispositivo(models.Model):
    contenedor = models.ForeignKey(ContenedorDispositivos, on_delete=models.CASCADE, related_name='dispositivos')
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    codigo= models.CharField(max_length=100)
    estado=models.ForeignKey(Estado,on_delete=models.CASCADE, related_name='estado_dispositivo')
    def __str__(self):
        return self.nombre
    
class OrdenServicio(models.Model):
    dispositivo = models.ForeignKey(Dispositivo, on_delete=models.CASCADE, related_name="trabajos")
    descripcion = models.TextField()
    oficial_encargado = models.CharField(max_length=100, blank=True, null=True)
    estado=models.ForeignKey(Estado,on_delete=models.CASCADE, related_name='estado_orden')

    def cerrar_trabajo(self):
        """Mueve materiales asignados a MaterialUtilizado y cierra el trabajo sin modificar sobrantes."""
        if self.estado == "Cerrado":
            return  # Evita ejecutar el proceso si el trabajo ya está cerrado

        from ALMACEN.models import MaterialAsignado, MaterialUtilizado

        # === Mover MaterialAsignado a MaterialUtilizado ===
        materiales_asignados = MaterialAsignado.objects.filter(trabajo=self)
        materiales_utilizados = [
            MaterialUtilizado(trabajo=self, stock=material.stock, cantidad=material.cantidad)
            for material in materiales_asignados
        ]
        MaterialUtilizado.objects.bulk_create(materiales_utilizados)

        # Eliminar MaterialAsignado después de moverlo a MaterialUtilizado
        materiales_asignados.delete()

        # Cambiar estado del trabajo
        self.estado = "Cerrado"
        self.save()

    def __str__(self):
        return f"Trabajo en {self.departamento} - {self.descripcion}"