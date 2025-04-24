from django.db import models
from django.db.models import F

class Edificio(models.Model):  # O Ubicacion si prefieres un término más amplio
    nombre = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.nombre


class Departamento(models.Model):
    edificio = models.ForeignKey(Edificio, on_delete=models.CASCADE, related_name="departamentos")
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.edificio.nombre} - {self.nombre}"
    
class Trabajo(models.Model):
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, related_name="trabajos")
    descripcion = models.TextField()
    oficial_encargado = models.CharField(max_length=100, blank=True, null=True)
    suboficial_encargado = models.CharField(max_length=100, blank=True, null=True)
    planeamiento = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=50, default='Activo')

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