# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (ArticuloViewSet, CategoriaViewSet, UnidadMedidaViewSet)

router = DefaultRouter()
router.register(r'articulos', ArticuloViewSet, basename='articulo')
router.register(r'categorias', CategoriaViewSet)
router.register(r'unidades-medida', UnidadMedidaViewSet)
urlpatterns = [
    path('api/', include(router.urls)),
]