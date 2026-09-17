from django.db import IntegrityError
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from ..models import Iglesia


def normalizar_nombre(valor):
    return ' '.join((valor or '').split()).title()


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def create_iglesia(request):
    nombre = normalizar_nombre(request.data.get('nombre'))

    # 1️⃣ Validar vacío
    if not nombre or nombre.strip() == '':
        return Response(
            {'error': 'El nombre es obligatorio'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 2️⃣ Normalizar (Mayúscula cada palabra)
    nombre_normalizado = nombre

    # 3️⃣ Verificar duplicado (sin importar mayúsculas)
    if Iglesia.objects.filter(nombre__iexact=nombre_normalizado).exists():
        return Response(
            {'error': 'La iglesia ya está registrada'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 4️⃣ Crear
    try:
        nueva_iglesia = Iglesia.objects.create(nombre=nombre_normalizado)
    except IntegrityError:
        return Response({'error': 'La iglesia ya está registrada'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 5️⃣ Devolver datos de la iglesia creada
    return Response({
        'id': nueva_iglesia.id,
        'nombre': nueva_iglesia.nombre
    }, status=status.HTTP_201_CREATED)

    
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def list_iglesias(request):
    iglesias = Iglesia.objects.all().order_by('nombre')
    return Response(iglesias.values(), status=status.HTTP_200_OK)

@api_view(['DELETE'])
@authentication_classes([])
@permission_classes([AllowAny])
def delete_iglesia(request, id):
    try:
        iglesia = Iglesia.objects.get(id=id)
        iglesia.delete()
        return Response({'message': 'Iglesia eliminada correctamente'}, status=status.HTTP_200_OK)
    except Iglesia.DoesNotExist:
        return Response({'error': 'Iglesia no encontrada'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
@authentication_classes([])
@permission_classes([AllowAny])
def update_iglesia(request, id):
    try:
        iglesia = Iglesia.objects.get(id=id)
        nombre = normalizar_nombre(request.data.get('nombre'))
        if not nombre:
            return Response({'error': 'El nombre es obligatorio'}, status=status.HTTP_400_BAD_REQUEST)
        if Iglesia.objects.filter(nombre__iexact=nombre).exclude(id=id).exists():
            return Response({'error': 'La iglesia ya está registrada'}, status=status.HTTP_400_BAD_REQUEST)
        iglesia.nombre = nombre
        iglesia.save(update_fields=['nombre'])
        return Response({'message': 'Iglesia actualizada correctamente', 'iglesia': {'id': iglesia.id, 'nombre': iglesia.nombre}}, status=status.HTTP_200_OK)
    except Iglesia.DoesNotExist:
        return Response({'error': 'Iglesia no encontrada'}, status=status.HTTP_404_NOT_FOUND)
