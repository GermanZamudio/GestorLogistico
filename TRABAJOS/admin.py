from django.contrib import admin
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Trabajo, Departamento, Edificio
from ALMACEN.models import MaterialUtilizado, SobranteAsignado

class MaterialUtilizadoInline(admin.TabularInline):
    model = MaterialUtilizado
    extra = 0
    readonly_fields = ('stock', 'cantidad')

class SobranteAsignadoInline(admin.TabularInline):
    model = SobranteAsignado
    extra = 1

def cerrar_trabajo_action(modeladmin, request, queryset):
    """Cierra los trabajos seleccionados y mueve los materiales asignados a utilizados."""
    for trabajo in queryset:
        if trabajo.estado != "Cerrado":
            trabajo.cerrar_trabajo()
    modeladmin.message_user(request, "Se cerraron los trabajos seleccionados correctamente.", messages.SUCCESS)

cerrar_trabajo_action.short_description = "Cerrar trabajos seleccionados"

@admin.register(Trabajo)
class TrabajoAdmin(admin.ModelAdmin):
    list_display = ('get_edificio', 'departamento', 'descripcion', 'estado', 'cerrar_trabajo_button')
    search_fields = ('departamento__nombre', 'descripcion')
    list_filter = ('estado', 'departamento__edificio')
    inlines = [MaterialUtilizadoInline, SobranteAsignadoInline]
    actions = [cerrar_trabajo_action]

    def get_edificio(self, obj):
        return obj.departamento.edificio.nombre
    get_edificio.short_description = "Edificio"

    def cerrar_trabajo_button(self, obj):
        if obj.estado != "Cerrado":
            url = reverse('admin:cerrar_trabajo', args=[obj.id])
            return format_html('<a href="{}" style="color: red;">Cerrar</a>', url)
        return "Cerrado"
    cerrar_trabajo_button.short_description = "Acción"

    def cerrar_trabajo_view(self, request, trabajo_id):
        trabajo = get_object_or_404(Trabajo, id=trabajo_id)
        if trabajo.estado != "Cerrado":
            trabajo.cerrar_trabajo()
            self.message_user(request, f"El trabajo '{trabajo.descripcion}' ha sido cerrado correctamente.", messages.SUCCESS)
        return redirect('/admin/TRABAJOS/trabajo/')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('trabajo/cerrar_trabajo/<int:trabajo_id>/', self.admin_site.admin_view(self.cerrar_trabajo_view), name="cerrar_trabajo"),
        ]
        return custom_urls + urls

# Registrar solo los modelos necesarios
admin.site.register(Edificio)
admin.site.register(Departamento)
