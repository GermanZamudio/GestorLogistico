from django.contrib import admin
from .models import (
    Articulo, Bienes, Stock, OrdenDeCompra, ArticuloEnOrden, UnidadBien,
    BienesAsignados, Proveedor, MaterialAsignado, Sobrante,
    SobranteAsignado, MaterialUtilizado
)
from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages

from .models import UnidadBien, Bienes
@admin.register(UnidadBien)
class UnidadBienAdmin(admin.ModelAdmin):
    list_display = ('identificador_unico', 'bien', 'estado', 'ubicacion_actual', 'disponible', 'acciones')
    list_filter = ('estado', 'disponible')
    search_fields = ('identificador_unico', 'bien__articulo_asociado__nombre')

    def acciones(self, obj):
        botones = ""
        if obj.disponible:
            botones += format_html(
                '<a class="button" href="asignar/{}/" style="color:green;">Asignar</a>&nbsp;', obj.id
            )
        elif obj.estado == "asignado":
            botones += format_html(
                '<a class="button" href="devolver/{}/" style="color:orange;">Devolver</a>&nbsp;', obj.id
            )
        if obj.estado == "proceso_baja":
            botones += format_html(
                '<a class="button" href="confirmar_baja/{}/" style="color:red;">Eliminar</a>', obj.id
            )
        return botones

    acciones.short_description = "Acciones"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('asignar/<int:unidad_id>/', self.admin_site.admin_view(self.asignar_view)),
            path('devolver/<int:unidad_id>/', self.admin_site.admin_view(self.devolver_view)),
            path('confirmar_baja/<int:unidad_id>/', self.admin_site.admin_view(self.confirmar_baja_view)),
        ]
        return custom_urls + urls

    def asignar_view(self, request, unidad_id):
        unidad = get_object_or_404(UnidadBien, id=unidad_id)
        try:
            unidad.asignar('Asignado desde admin')  # Llama al método del modelo
            self.message_user(request, f"Unidad {unidad} asignada correctamente.", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, str(e), messages.ERROR)
        return redirect('..')

    def devolver_view(self, request, unidad_id):
        unidad = get_object_or_404(UnidadBien, id=unidad_id)
        unidad.devolver()  # Llama al método del modelo
        self.message_user(request, f"Unidad {unidad} devuelta al depósito.", messages.INFO)
        return redirect('..')

    def confirmar_baja_view(self, request, unidad_id):
        unidad = get_object_or_404(UnidadBien, id=unidad_id)
        try:
            unidad.confirmar_baja()  # Llama al método del modelo
            self.message_user(request, f"Unidad {unidad} eliminada del sistema.", messages.WARNING)
        except Exception as e:
            self.message_user(request, str(e), messages.ERROR)
        return redirect('..')
    
@admin.register(Articulo)
class ArticuloAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'marca', 'codigo')
    search_fields = ('nombre', 'codigo')
    list_filter = ('marca',)


@admin.register(Bienes)
class BienesAdmin(admin.ModelAdmin):
    list_display = ('articulo_asociado', 'cantidad', 'tipo', 'licitacion', 'requiere_identificador')
    list_filter = ('tipo', 'requiere_identificador')
    search_fields = ('articulo_asociado__nombre', 'licitacion')


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('articulo_asociado', 'cantidad', 'pendiente_a_entregar', 'estado')
    search_fields = ('articulo_asociado__nombre',)
    list_filter = ('estado',)


@admin.register(OrdenDeCompra)
class OrdenDeCompraAdmin(admin.ModelAdmin):
    list_display = ('numero_orden', 'proveedor', 'fecha_orden', 'estado')
    list_filter = ('estado', 'fecha_orden')
    search_fields = ('numero_orden', 'proveedor__nombre')


@admin.register(ArticuloEnOrden)
class ArticuloEnOrdenAdmin(admin.ModelAdmin):
    list_display = ('orden', 'articulo', 'cantidad_pedida', 'cantidad_recibida', 'entregado')
    list_filter = ('entregado',)
    search_fields = ('articulo__nombre', 'orden__numero_orden')

@admin.register(BienesAsignados)
class BienesAsignadosAdmin(admin.ModelAdmin):
    list_display = ('trabajo', 'bien', 'cantidad_usada')
    search_fields = ('trabajo__nombre', 'bien__articulo_asociado__nombre')
    filter_horizontal = ('unidades_asignadas',)


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion')
    search_fields = ('nombre',)


@admin.register(MaterialAsignado)
class MaterialAsignadoAdmin(admin.ModelAdmin):
    list_display = ('trabajo', 'stock', 'cantidad')
    search_fields = ('trabajo__nombre', 'stock__articulo_asociado__nombre')


@admin.register(Sobrante)
class SobranteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cantidad', 'trabajo_origen')
    search_fields = ('nombre', 'trabajo_origen__nombre')


@admin.register(SobranteAsignado)
class SobranteAsignadoAdmin(admin.ModelAdmin):
    list_display = ('trabajo', 'nombre', 'cantidad_usada')
    search_fields = ('nombre', 'trabajo__nombre')


@admin.register(MaterialUtilizado)
class MaterialUtilizadoAdmin(admin.ModelAdmin):
    list_display = ('trabajo', 'stock', 'cantidad')
    search_fields = ('trabajo__nombre', 'stock__articulo_asociado__nombre')
