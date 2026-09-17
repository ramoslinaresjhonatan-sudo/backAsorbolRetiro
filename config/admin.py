from django.contrib import admin
from .models import Iglesia, Inscrito

@admin.register(Iglesia)
class IglesiaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)

@admin.register(Inscrito)
class InscritoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'paterno', 'iglesia', 'verificado')
    list_filter = ('iglesia', 'verificado', 'genero')
    search_fields = ('nombre', 'paterno', 'materno')
