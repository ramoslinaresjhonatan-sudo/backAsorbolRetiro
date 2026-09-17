from datetime import date, timedelta

from django.utils import timezone
from rest_framework.test import APITestCase
from .models import Iglesia, Inscrito


class IglesiaApiTests(APITestCase):
    def test_registration_stores_optional_care_fields(self):
        iglesia = Iglesia.objects.create(nombre='Iglesia Central')

        response = self.client.post('/api/Inscripcion/crear/', {
            'nombre': 'Marta',
            'paterno': 'Ríos',
            'edad': 19,
            'genero': 'F',
            'iglesia': iglesia.id,
            'telefono': '70000000',
            'fecha_nacimiento': '2007-05-12',
            'primer_retiro': True,
            'motivo_retiro': 'Me invitó una amiga',
        }, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['telefono'], '70000000')
        self.assertTrue(response.data['primer_retiro'])
        self.assertEqual(response.data['motivo_retiro'], 'Me invitó una amiga')

    def test_create_update_duplicate_and_delete(self):
        creada = self.client.post('/api/iglesia/crear/', {'nombre': '  iglesia   central  '}, format='json')
        self.assertEqual(creada.status_code, 201)
        iglesia_id = creada.data['id']
        self.assertEqual(creada.data['nombre'], 'Iglesia Central')

        actualizada = self.client.put(f'/api/iglesia/actualizar/{iglesia_id}/', {'nombre': 'Iglesia Nueva'}, format='json')
        self.assertEqual(actualizada.status_code, 200)
        self.assertEqual(actualizada.data['iglesia']['nombre'], 'Iglesia Nueva')

        duplicada = self.client.post('/api/iglesia/crear/', {'nombre': 'iglesia nueva'}, format='json')
        self.assertEqual(duplicada.status_code, 400)
        self.assertEqual(duplicada.data['error'], 'La iglesia ya está registrada')

        eliminada = self.client.delete(f'/api/iglesia/eliminar/{iglesia_id}/')
        self.assertEqual(eliminada.status_code, 200)
        self.assertEqual(list(self.client.get('/api/iglesia/listar/').data), [])

    def test_report_returns_graph_data(self):
        iglesia = Iglesia.objects.create(nombre='Iglesia Central')
        Inscrito.objects.create(nombre='Ana', paterno='Paz', edad=18, genero='F', iglesia=iglesia, telefono='70000000', fecha_nacimiento=date(2008, 10, 3), primer_retiro=True, motivo_retiro='Me invitó una amiga')
        Inscrito.objects.create(nombre='Luis', paterno='Sol', edad=22, genero='M', iglesia=iglesia)

        response = self.client.get('/api/reporte/general/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['totales'], {'inscritos': 2, 'mujeres': 1, 'hombres': 1})
        self.assertEqual(response.data['edades'][0]['edad'], 18)
        self.assertEqual(response.data['iglesias'][0]['total'], 2)
        self.assertEqual(response.data['acompanamiento']['primer_retiro_total'], 1)
        self.assertEqual(response.data['acompanamiento']['primeras_veces'][0]['telefono'], '70000000')
        self.assertEqual(response.data['acompanamiento']['cumpleanios_campamento'][0]['fecha_cumpleanos'], '03 de octubre')

        listado = self.client.get('/api/Inscripcion/listar/')
        self.assertEqual(listado.status_code, 200)
        self.assertIn('creado_en', listado.data[0])

    def test_multiple_registrations_and_invalid_data_are_handled(self):
        iglesia = Iglesia.objects.create(nombre='Iglesia Norte')
        base = {'paterno': 'Paz', 'edad': 20, 'genero': 'F', 'iglesia': iglesia.id}

        primera = self.client.post('/api/Inscripcion/crear/', {**base, 'nombre': 'Elena', 'telefono': '+591 70000000'}, format='json')
        segunda = self.client.post('/api/Inscripcion/crear/', {**base, 'nombre': 'Sofía', 'genero': 'M'}, format='json')
        duplicada = self.client.post('/api/Inscripcion/crear/', {**base, 'nombre': 'Elena'}, format='json')
        edad_texto = self.client.post('/api/Inscripcion/crear/', {**base, 'nombre': 'Lucía', 'edad': 'veinte'}, format='json')
        edad_negativa = self.client.post('/api/Inscripcion/crear/', {**base, 'nombre': 'Rosa', 'edad': -1}, format='json')
        telefono_invalido = self.client.post('/api/Inscripcion/crear/', {**base, 'nombre': 'Mara', 'telefono': 'telefono'}, format='json')
        fecha_futura = self.client.post('/api/Inscripcion/crear/', {**base, 'nombre': 'Nora', 'fecha_nacimiento': str(timezone.localdate() + timedelta(days=1))}, format='json')
        iglesia_inexistente = self.client.post('/api/Inscripcion/crear/', {**base, 'nombre': 'Lina', 'iglesia': 999999}, format='json')

        self.assertEqual(primera.status_code, 201)
        self.assertEqual(segunda.status_code, 201)
        self.assertEqual(duplicada.status_code, 400)
        self.assertEqual(edad_texto.status_code, 400)
        self.assertEqual(edad_negativa.status_code, 400)
        self.assertEqual(telefono_invalido.status_code, 400)
        self.assertEqual(fecha_futura.status_code, 400)
        self.assertEqual(iglesia_inexistente.status_code, 400)
        self.assertEqual(Inscrito.objects.count(), 2)

    def test_registration_is_rejected_when_capacity_is_full(self):
        iglesia = Iglesia.objects.create(nombre='Iglesia Cupos')
        Inscrito.objects.bulk_create([
            Inscrito(nombre=f'Persona {index}', paterno='Prueba', edad=20, genero='M', iglesia=iglesia)
            for index in range(200)
        ])

        response = self.client.post('/api/Inscripcion/crear/', {
            'nombre': 'Último', 'paterno': 'Intento', 'edad': 21, 'genero': 'F', 'iglesia': iglesia.id,
        }, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Los cupos para el retiro ya están completos.')
        self.assertEqual(Inscrito.objects.count(), 200)
