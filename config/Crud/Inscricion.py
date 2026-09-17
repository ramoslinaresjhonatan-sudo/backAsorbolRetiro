import re

from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from ..models import Iglesia, Inscrito


CAPACIDAD_MAXIMA = 200


def limpiar_texto(valor):
    return ' '.join(str(valor or '').split())


def serializar_inscrito(inscrito):
    return {
        'id': inscrito.id,
        'nombre': inscrito.nombre,
        'paterno': inscrito.paterno,
        'materno': inscrito.materno,
        'edad': inscrito.edad,
        'genero': inscrito.genero,
        'telefono': inscrito.telefono,
        'fecha_nacimiento': inscrito.fecha_nacimiento,
        'primer_retiro': inscrito.primer_retiro,
        'motivo_retiro': inscrito.motivo_retiro,
        'iglesia': inscrito.iglesia.nombre if inscrito.iglesia else None,
    }


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def create_inscrito(request):
    data = request.data
    nombre = limpiar_texto(data.get('nombre')).title()
    paterno = limpiar_texto(data.get('paterno')).title()
    materno = limpiar_texto(data.get('materno')).title() or None
    try:
        edad = int(data.get('edad'))
    except (TypeError, ValueError):
        edad = None
    genero = limpiar_texto(data.get('genero')).upper()
    iglesia = data.get('iglesia')
    telefono = limpiar_texto(data.get('telefono')) or None
    fecha_nacimiento_valor = data.get('fecha_nacimiento')
    fecha_nacimiento = parse_date(fecha_nacimiento_valor) if isinstance(fecha_nacimiento_valor, str) and fecha_nacimiento_valor else None
    primer_retiro = data.get('primer_retiro') in (True, 'true', 'True', 1, '1')
    motivo_retiro = limpiar_texto(data.get('motivo_retiro')).capitalize() or None

    if not nombre or not paterno or edad is None or genero not in {'M', 'F'} or not iglesia:
        return Response({'error': 'Completa los datos obligatorios.'}, status=status.HTTP_400_BAD_REQUEST)
    if not 1 <= edad <= 120:
        return Response({'error': 'La edad debe estar entre 1 y 120 años.'}, status=status.HTTP_400_BAD_REQUEST)
    if fecha_nacimiento_valor and not fecha_nacimiento:
        return Response({'error': 'La fecha de nacimiento no es válida.'}, status=status.HTTP_400_BAD_REQUEST)
    if fecha_nacimiento and fecha_nacimiento > timezone.localdate():
        return Response({'error': 'La fecha de nacimiento no puede ser futura.'}, status=status.HTTP_400_BAD_REQUEST)
    if len(nombre) > 50 or len(paterno) > 50 or len(materno or '') > 50 or len(telefono or '') > 20 or len(motivo_retiro or '') > 250:
        return Response({'error': 'Uno de los datos excede el límite permitido.'}, status=status.HTTP_400_BAD_REQUEST)
    if telefono and not re.fullmatch(r'[0-9+()\-\s]{6,20}', telefono):
        return Response({'error': 'El número de teléfono no es válido.'}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        # Todas las inscripciones bloquean las mismas iglesias durante esta
        # comprobación. Así dos solicitudes simultáneas no pueden ocupar el
        # mismo último cupo ni crear un duplicado en paralelo.
        list(Iglesia.objects.select_for_update().order_by('pk').values_list('pk', flat=True))
        try:
            iglesia_obj = Iglesia.objects.get(pk=iglesia)
        except (Iglesia.DoesNotExist, TypeError, ValueError):
            return Response({'error': 'La iglesia seleccionada no existe.'}, status=status.HTTP_400_BAD_REQUEST)
        existe = Inscrito.objects.filter(nombre=nombre, paterno=paterno, edad=edad, iglesia=iglesia_obj).exists()
        if existe:
            return Response({'error': 'Esta persona ya está inscrita.'}, status=status.HTTP_400_BAD_REQUEST)
        if Inscrito.objects.count() >= CAPACIDAD_MAXIMA:
            return Response({'error': 'Los cupos para el retiro ya están completos.'}, status=status.HTTP_400_BAD_REQUEST)

        inscrito = Inscrito.objects.create(
            nombre=nombre, paterno=paterno, materno=materno, edad=edad, genero=genero,
            iglesia=iglesia_obj, telefono=telefono, fecha_nacimiento=fecha_nacimiento,
            primer_retiro=primer_retiro, motivo_retiro=motivo_retiro if primer_retiro else None,
        )

    return Response(serializar_inscrito(inscrito), status=status.HTTP_201_CREATED)


@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def list_inscritos(request):
    inscritos = Inscrito.objects.select_related('iglesia').values(
        'id', 'nombre', 'paterno', 'materno', 'edad', 'genero', 'telefono',
        'fecha_nacimiento', 'primer_retiro', 'motivo_retiro', 'creado_en', 'iglesia__id', 'iglesia__nombre',
    )
    return Response(inscritos, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def cupo_inscritos(request):
    return Response(Inscrito.objects.count(), status=status.HTTP_200_OK)

