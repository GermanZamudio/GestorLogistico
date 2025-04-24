from rest_framework import serializers
from .models import (
    Articulo, Bienes, UnidadBien, Stock,
    OrdenDeCompra, ArticuloEnOrden, BienesAsignados,
    Proveedor, MaterialAsignado, Sobrante,
    SobranteAsignado, MaterialUtilizado,
    Categoria, Unidad_Medida
)

from TRABAJOS.models import Trabajo

class ArticuloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Articulo
        fields = '__all__'

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'

class UnidadMedidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unidad_Medida
        fields = '__all__'

class BienesSerializer(serializers.ModelSerializer):
    articulo_asociado = serializers.PrimaryKeyRelatedField(queryset=Articulo.objects.all())

    class Meta:
        model = Bienes
        fields = '__all__'


class UnidadBienSerializer(serializers.ModelSerializer):
    bien = serializers.PrimaryKeyRelatedField(queryset=Bienes.objects.all())

    class Meta:
        model = UnidadBien
        fields = '__all__'


class StockSerializer(serializers.ModelSerializer):
    articulo_asociado = serializers.PrimaryKeyRelatedField(queryset=Articulo.objects.all())

    class Meta:
        model = Stock
        fields = '__all__'


class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = '__all__'


class OrdenDeCompraSerializer(serializers.ModelSerializer):
    proveedor = serializers.PrimaryKeyRelatedField(queryset=Proveedor.objects.all(), allow_null=True)
    articulos = serializers.PrimaryKeyRelatedField(queryset=Articulo.objects.all(), many=True)

    class Meta:
        model = OrdenDeCompra
        fields = '__all__'


class ArticuloEnOrdenSerializer(serializers.ModelSerializer):
    orden = serializers.PrimaryKeyRelatedField(queryset=OrdenDeCompra.objects.all())
    articulo = serializers.PrimaryKeyRelatedField(queryset=Articulo.objects.all())

    class Meta:
        model = ArticuloEnOrden
        fields = '__all__'


class BienesAsignadosSerializer(serializers.ModelSerializer):
    trabajo = serializers.PrimaryKeyRelatedField(queryset=Trabajo.objects.all())
    bien = serializers.PrimaryKeyRelatedField(queryset=Bienes.objects.all())
    unidades_asignadas = serializers.PrimaryKeyRelatedField(queryset=UnidadBien.objects.all(), many=True)

    class Meta:
        model = BienesAsignados
        fields = '__all__'


class MaterialAsignadoSerializer(serializers.ModelSerializer):
    stock = serializers.PrimaryKeyRelatedField(queryset=Stock.objects.all())
    trabajo = serializers.PrimaryKeyRelatedField(queryset=Trabajo.objects.all())

    class Meta:
        model = MaterialAsignado
        fields = '__all__'


class SobranteSerializer(serializers.ModelSerializer):
    material_asignado = serializers.PrimaryKeyRelatedField(queryset=MaterialAsignado.objects.all(), allow_null=True)
    trabajo_origen = serializers.PrimaryKeyRelatedField(queryset=Trabajo.objects.all())

    class Meta:
        model = Sobrante
        fields = '__all__'


class SobranteAsignadoSerializer(serializers.ModelSerializer):
    trabajo = serializers.PrimaryKeyRelatedField(queryset=Trabajo.objects.all())
    sobrante = serializers.PrimaryKeyRelatedField(queryset=Sobrante.objects.all(), allow_null=True)

    class Meta:
        model = SobranteAsignado
        fields = '__all__'


class MaterialUtilizadoSerializer(serializers.ModelSerializer):
    trabajo = serializers.PrimaryKeyRelatedField(queryset=Trabajo.objects.all())
    stock = serializers.PrimaryKeyRelatedField(queryset=Stock.objects.all())

    class Meta:
        model = MaterialUtilizado
        fields = '__all__'
