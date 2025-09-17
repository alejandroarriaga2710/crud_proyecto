from django.urls import path
from . import views

app_name = 'crud_personas'

urlpatterns = [
    path('', views.personas_listado, name='listado'),
    path('modal/nuevo/', views.modal_persona_crear, name='modal_crear'),
    path('modal/<int:persona_id>/editar/', views.modal_persona_editar, name='modal_editar'),
    path('modal/<int:persona_id>/eliminar/', views.modal_persona_eliminar, name='modal_eliminar'),
]
