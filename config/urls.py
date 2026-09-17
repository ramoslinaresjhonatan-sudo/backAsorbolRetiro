from django.urls import path
from .Crud.Iglesia import *
from .Crud.Inscricion import *
from .Crud.Reporte import reporte_general
urlpatterns = [
    path('iglesia/crear/', create_iglesia), 
    path('iglesia/listar/', list_iglesias),
    path('iglesia/eliminar/<int:id>/', delete_iglesia),
    path('iglesia/actualizar/<int:id>/', update_iglesia),

    path('Inscripcion/crear/', create_inscrito), 
    path('Inscripcion/listar/', list_inscritos), 
    path('Inscripcion/cupo/', cupo_inscritos), 

    # 📊 REPORTE
    path('reporte/general/', reporte_general),
]
