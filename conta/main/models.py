from django.db import models

# Create your models here.
class Cuenta(models.Model):
    """Modelo de las cuentas."""
    num = models.CharField(max_length=10, primary_key=True)
    nombre = models.CharField(max_length=50, help_text='Nombre de la cuenta')

    def __str__(self):
        return f'{self.num}: {self.nombre}'


class Movimiento(models.Model):
    num = models.IntegerField()
    fecha = models.DateField()
    descripcion = models.CharField(max_length=200)
    debe = models.DecimalField(max_digits=8, decimal_places=2)
    haber = models.DecimalField(max_digits=8, decimal_places=2)
    cuenta = models.ForeignKey(Cuenta, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.num)
