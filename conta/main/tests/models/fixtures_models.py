import pytest
from django.urls import reverse
from main.models import Cuenta, Movimiento, Etiqueta


# give access to the database
pytestmark = pytest.mark.django_db

# common fixtures
@pytest.fixture
def create_etiqueta():
    return Etiqueta.objects.create(id='gastos', nombre='Gastos correintes')

@pytest.fixture
def create_cuenta(create_etiqueta):
    etiqueta = create_etiqueta
    cuenta = Cuenta.objects.create(num='100', nombre='Cuenta nómina')
    cuenta.etiqueta.set([etiqueta])
    return etiqueta, cuenta

@pytest.fixture
def create_movimiento(create_cuenta):
    etiqueta, cuenta = create_cuenta
    movimiento = Movimiento.objects.create(
        num = 1,
        fecha = "2021-12-07",
        descripcion = "Movimiento de prueba",
        debe = 250,
        haber = 0,
        cuenta = cuenta
    )
    return etiqueta, cuenta, movimiento
