from django.db import models
from django.utils import timezone

class Persona(models.Model):
    nombres = models.CharField("Nombre(s)", max_length=100)
    apellido_paterno = models.CharField("Apellido paterno", max_length=100)
    apellido_materno = models.CharField("Apellido materno", max_length=100, blank=True)
    fecha_nacimiento = models.DateField("Fecha de nacimiento", null=True, blank=True)
    alias = models.CharField("Alias", max_length=100, blank=True)
    fotografia = models.ImageField("Fotografía", upload_to='photos/', blank=True, null=True)
    creado_en = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['apellido_paterno', 'apellido_materno', 'nombres']

    def __str__(self):
        return f"{self.nombres} {self.apellido_paterno} {self.apellido_materno}".strip()

class Correo(models.Model):
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name='correos')
    correo = models.EmailField("Correo electrónico")

    def __str__(self):
        return self.correo

class Telefono(models.Model):
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name='telefonos')
    etiqueta = models.CharField("Etiqueta", max_length=50)  # casa, oficina, celular, etc.
    numero = models.CharField("Teléfono", max_length=30)

    def __str__(self):
        return f"{self.etiqueta}: {self.numero}"

class Direccion(models.Model):
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name='direcciones')
    linea1 = models.CharField("Calle y número", max_length=150)
    linea2 = models.CharField("Colonia / Depto.", max_length=150, blank=True)
    ciudad = models.CharField("Ciudad", max_length=100, blank=True)
    estado = models.CharField("Estado", max_length=100, blank=True)
    cp = models.CharField("C.P.", max_length=20, blank=True)
    pais = models.CharField("País", max_length=100, blank=True)

    def __str__(self):
        return f"{self.linea1}, {self.ciudad}"
