from datetime import date

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Count, Avg, Min, Max
from ..models import Inscrito, Iglesia


@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def reporte_general(request):
    # 🔹 Totales
    total_inscritos = Inscrito.objects.count()
    total_mujeres = Inscrito.objects.filter(genero='F').count()
    total_hombres = Inscrito.objects.filter(genero='M').count()

    # 🔹 Estadísticas de edad
    edades_stats = Inscrito.objects.aggregate(
        edad_min=Min('edad'),
        edad_max=Max('edad'),
        edad_promedio=Avg('edad')
    )

    # 🔹 Conteo por edades
    edades = (
        Inscrito.objects
        .values('edad')
        .annotate(total=Count('id'))
        .order_by('edad')
    )

    # 🔹 Iglesias con cantidad de inscritos
    iglesias = (
        Iglesia.objects
        .annotate(total=Count('inscrito'))
        .values('nombre', 'total')
        .order_by('-total')
    )

    primeras_veces = list(
        Inscrito.objects
        .filter(primer_retiro=True)
        .select_related('iglesia')
        .values('id', 'nombre', 'paterno', 'materno', 'telefono', 'motivo_retiro', 'iglesia__nombre')
        .order_by('nombre', 'paterno')
    )
    total_primer_retiro = len(primeras_veces)

    dias_campamento = {2: '02 de octubre', 3: '03 de octubre', 4: '04 de octubre'}
    cumpleanios_campamento = [
        {
            **persona,
            'fecha_cumpleanos': dias_campamento[persona['fecha_nacimiento'].day],
        }
        for persona in Inscrito.objects.filter(
            fecha_nacimiento__month=10,
            fecha_nacimiento__day__in=list(dias_campamento),
        ).select_related('iglesia').values(
            'id', 'nombre', 'paterno', 'materno', 'telefono', 'fecha_nacimiento', 'iglesia__nombre',
        ).order_by('fecha_nacimiento__day', 'nombre', 'paterno')
    ]

    return Response({
        'totales': {
            'inscritos': total_inscritos,
            'mujeres': total_mujeres,
            'hombres': total_hombres,
        },
        'edades_stats': edades_stats,
        'edades': list(edades),
        'iglesias': list(iglesias),
        'acompanamiento': {
            'primer_retiro_total': total_primer_retiro,
            'primer_retiro_porcentaje': round((total_primer_retiro / total_inscritos) * 100, 1) if total_inscritos else 0,
            'primeras_veces': primeras_veces,
            'cumpleanios_campamento': cumpleanios_campamento,
        },
    })
