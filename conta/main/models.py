from django.db import models

# Create your models here.
class Etiqueta(models.Model):
    """Modelo de las cuentas."""
    id = models.CharField(max_length=15, primary_key=True, help_text='etiqueta')
    nombre = models.CharField(max_length=50, help_text='Nombre para los informes')

    def __str__(self):
        return self.id


class Cuenta(models.Model):
    """Modelo de las cuentas."""
    num = models.CharField(max_length=10, primary_key=True)
    nombre = models.CharField(max_length=50, help_text='Nombre de la cuenta')
    etiqueta = models.ManyToManyField(Etiqueta, help_text='Etiqueta o etiquetas para la generación de informes')

    def __str__(self):
        return f'{self.num}: {self.nombre}'


class Movimiento(models.Model):
    """Modelo de los movimientos"""
    num = models.IntegerField()
    fecha = models.DateField()
    descripcion = models.CharField(max_length=200)
    debe = models.DecimalField(max_digits=8, decimal_places=2)
    haber = models.DecimalField(max_digits=8, decimal_places=2)
    cuenta = models.ForeignKey(Cuenta, on_delete=models.PROTECT)

    def __str__(self):
        return str(self.num)


class FiltroCuentas(models.Model):
    """Modelo para el filtro de los asientos/movimientos"""
    CAMPOS = [
        ('num', 'num'),
        ('nombre', 'nombre'),
        ('etiqueta', 'etiqueta'),
    ]

    # filtro
    num = models.CharField(max_length=10, default='')
    nombre = models.CharField(max_length=50, default='')
    etiqueta = models.CharField(max_length=15, default='')
    # orden
    campo = models.CharField(max_length=10, choices=CAMPOS, default='num')
    ascendiente = models.BooleanField(default=True)


class FiltroMovimientos(models.Model):
    """Modelo para el filtro de los asientos/movimientos"""
    CAMPOS = [
        ('num', 'num'),
        ('fecha', 'fecha'),
        ('descripcion', 'descripcion'),
        ('debe', 'debe'),
        ('haber', 'haber'),
        ('cuenta', 'cuenta'),
    ]

    # filtro
    fecha_inicial = models.CharField(max_length=10, default='')
    fecha_final = models.CharField(max_length=10, default='')
    descripcion = models.CharField(max_length=200, default='')
    cuenta = models.CharField(max_length=10, default='')
    asiento = models.CharField(max_length=10, default='')
    etiqueta = models.CharField(max_length=15, default='')

    # orden
    campo = models.CharField(max_length=15, choices=CAMPOS, default='num')
    ascendiente = models.BooleanField(default=True)
