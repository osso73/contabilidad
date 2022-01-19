import pytest
from django.urls import reverse

from main.models import Cuenta, Movimiento, Etiqueta


# give access to the database
pytestmark = pytest.mark.django_db

# common fixtures, used by several tests
@pytest.fixture
def populate_database_etiquetas():
    etiquetas_raw = [
        ['gastos', 'Gastos corrientes'],
        ['ingresos', 'Ingresos'],
        ['balance', 'Cuentas balance'],
        ['casa', 'Gastos de la casa'],
    ]
    etiquetas = list()
    for id, nombre in etiquetas_raw:
        e = Etiqueta.objects.create(id=id, nombre=nombre)
        etiquetas.append(e)
    return etiquetas

@pytest.fixture
def populate_database_cuentas(populate_database_etiquetas):
    etiquetas = populate_database_etiquetas
    cuentas_raw = [
        ['100', 'Caja', [etiquetas[2]] ],
        ['101', 'Tickets restaurant', [etiquetas[2]] ],
        ['1101', 'Cuenta nómina', [etiquetas[2]] ],
        ['1110', 'Cuenta ahorro', [etiquetas[2]] ],
        ['1200', 'Tarjeta Visa', [etiquetas[2]] ],
        ['1201', 'Tarjeta Amex', [etiquetas[2]] ],
        ['1210', 'Tarjeta prepago', [etiquetas[2]] ],
        ['15', 'Hipoteca', [etiquetas[0], etiquetas[3]] ],
        ['2001', 'Gas casa', [etiquetas[0], etiquetas[3]] ],
        ['2000', 'Electricidad casa', [etiquetas[0], etiquetas[3]] ],
        ['203', 'Impuestos casa', [etiquetas[0], etiquetas[3]] ],
        ['300', 'Comida', [etiquetas[0]] ],
        ['312', 'Cenas, pinchos…', [etiquetas[0]] ],
        ['324', 'Gastos coche', [etiquetas[0]] ],
    ]
    cuentas = list()
    for num, nombre, etiqueta in cuentas_raw:
        c = Cuenta.objects.create(num=num, nombre=nombre)
        c.etiqueta.set(etiqueta)
        cuentas.append(c)
    return etiquetas, cuentas


@pytest.fixture
def populate_database(populate_database_cuentas):
    etiquetas, cuentas = populate_database_cuentas
    movimientos = list()
    movimientos_raw = [
        [1, '2021-12-28', 'Compra del pan', 2.50, 0, cuentas[0]],
        [1, '2021-12-28', 'Compra del pan', 0, 2.50, cuentas[3]],
        [2, '2021-12-15', 'Compra de fruta', 10.75, 0, cuentas[0]],
        [2, '2021-12-15', 'Compra de fruta', 0, 10.75, cuentas[3]],
        [3, '2021-12-18', 'Calcetines y calzoncillos', 15.85, 0, cuentas[1]],
        [3, '2021-12-18', 'Calcetines y calzoncillos', 0, 15.85, cuentas[3]],
        [4, '2021-12-20', 'Abrigo de invierno', 54, 0, cuentas[1]],
        [4, '2021-12-20', 'Abrigo de invierno', 0, 54, cuentas[3]],
    ]
    for num, fecha, descripcion, debe, haber, cuenta in movimientos_raw:
        m = Movimiento.objects.create(num=num, fecha=fecha,
            descripcion=descripcion, debe=debe, haber=haber, cuenta=cuenta)
        movimientos.append(m)

    return etiquetas, cuentas, movimientos
