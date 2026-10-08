from django.urls import path
from . import views

app_name = "programadas"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("novo/", views.editar, name="novo"),
    path("<int:pk>/editar/", views.editar, name="editar"),
    path("<int:pk>/apagar/", views.apagar, name="apagar"),
    path("<int:pk>/alternar/", views.alternar, name="alternar"),
]