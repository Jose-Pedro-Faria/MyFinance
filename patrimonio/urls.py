from django.urls import path
from . import views

app_name = "patrimonio"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("novo/", views.novo_registo, name="novo"),
    path("categoria/nova/", views.nova_categoria, name="nova_categoria"),
]