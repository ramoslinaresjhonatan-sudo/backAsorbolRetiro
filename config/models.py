from django.db import models

class Iglesia(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre


class Inscrito(models.Model):
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]

    nombre = models.CharField(max_length=50)
    paterno = models.CharField(max_length=50)
    materno = models.CharField(max_length=50, null=True, blank=True)
    edad = models.PositiveIntegerField()
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    primer_retiro = models.BooleanField(default=False)
    motivo_retiro = models.CharField(max_length=250, null=True, blank=True)

    pagoTelefono = models.CharField(max_length=20, null=True, blank=True)
    pagoFecha = models.DateField(null=True, blank=True)
    pagoHora = models.TimeField(null=True, blank=True)
    pagoComprobante = models.CharField(max_length=500, null=True, blank=True)

    verificado = models.BooleanField(default=False)

    iglesia = models.ForeignKey(
        Iglesia,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} {self.paterno}"
