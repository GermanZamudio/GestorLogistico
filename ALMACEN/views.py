# views.py
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from .models import Articulo,Categoria, Unidad_Medida
from .serializers import (ArticuloSerializer, 
    CategoriaSerializer, UnidadMedidaSerializer)

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

class UnidadMedidaViewSet(viewsets.ModelViewSet):
    queryset = Unidad_Medida.objects.all()
    serializer_class = UnidadMedidaSerializer

class ArticuloViewSet(viewsets.ModelViewSet):
    queryset = Articulo.objects.all()
    serializer_class = ArticuloSerializer
   # permission_classes = [IsAuthenticated]