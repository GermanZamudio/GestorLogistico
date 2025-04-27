from django.contrib import admin
from .models import (
    TipoContenedorDispositivo,
    TipoEstado,
    Estado,
    ContenedorDispositivos,
    Dispositivo,
    OrdenServicio
)

@admin.register(TipoContenedorDispositivo)
class TipoContenedorDispositivoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(TipoEstado)
class TipoEstadoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo')
    search_fields = ('nombre', 'tipo__nombre')
    list_filter = ('tipo',)

@admin.register(ContenedorDispositivos)
class ContenedorDispositivosAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'codigo')
    search_fields = ('nombre', 'codigo')
    list_filter = ('tipo',)

@admin.register(Dispositivo)
class DispositivoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'contenedor', 'codigo', 'estado')
    search_fields = ('nombre', 'codigo', 'contenedor__nombre')
    list_filter = ('estado', 'contenedor__tipo')

@admin.register(OrdenServicio)
class OrdenServicioAdmin(admin.ModelAdmin):
    list_display = ('dispositivo', 'descripcion', 'oficial_encargado', 'estado')
    search_fields = ('descripcion', 'dispositivo__nombre', 'oficial_encargado')
    list_filter = ('estado',)
