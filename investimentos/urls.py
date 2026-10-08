from django.urls import path
from . import views

app_name = "investimentos"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("novo/", views.editar, name="novo"),
    path("<int:pk>/editar/", views.editar, name="editar"),
    path("<int:pk>/apagar/", views.apagar, name="apagar"),
    path("capturar/", views.capturar, name="capturar"),
    path("historico/", views.historico, name="historico"),
    path("historico/<int:pk>/", views.captura, name="captura"),
    path("historico/<int:pk>/apagar/", views.apagar_captura, name="apagar_captura"),
]