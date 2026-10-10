from django.urls import path
from . import views

app_name = "patrimonio"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("novo/", views.novo_registo, name="novo"),
    path("<int:pk>/editar/", views.editar_registo, name="editar"),
    path("<int:pk>/apagar/", views.apagar_registo, name="apagar"),
    path("categoria/nova/", views.nova_categoria, name="nova_categoria"),
    path("categorias/", views.categorias, name="categorias"),
    path("categorias/<int:pk>/alternar/", views.alternar_categoria, name="alternar_categoria"),
    path("categorias/<int:pk>/editar/", views.editar_categoria, name="editar_categoria"),
    path("categorias/<int:pk>/apagar/", views.apagar_categoria, name="apagar_categoria"),
]