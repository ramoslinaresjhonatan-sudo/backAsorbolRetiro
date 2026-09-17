from django.contrib import admin
from django.urls import path, include
#from config.views import home  # importar la vista para la raíz

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('config.urls')),  # todas las rutas de tu app config
]
