from django.urls import path
from . import views

app_name = "relatorios"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("novo/", views.novo_relatorio, name="novo"),
    path("<int:pk>/editar/", views.editar_relatorio, name="editar"),
    path("<int:pk>/apagar/", views.apagar_relatorio, name="apagar"),
    path("subcategoria/nova/", views.nova_subcategoria, name="nova_subcategoria"),
]