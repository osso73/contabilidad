import pytest
from decimal import InvalidOperation

from main.models import Cuenta, Movimiento, FiltroCuentas, FiltroMovimientos
from django.db.models.deletion import ProtectedError
from django.core.exceptions import ValidationError

from main.models import Cuenta, Movimiento, FiltroCuentas, FiltroMovimientos


# give access to the database
pytestmark = pytest.mark.django_db


class TestCuentaModel():
    @pytest.fixture
    def create_cuenta(self):
        # Set up non-modified objects used by all test methods
        return Cuenta.objects.create(num='100', nombre='Cuenta nómina')

    def test_object_name_is_num_colon_nombre(self, create_cuenta):
        cuenta = create_cuenta
        expected_name = f'{cuenta.num}: {cuenta.nombre}'
        assert str(cuenta) == expected_name

    def test_nombre_max_length(self, create_cuenta):
        cuenta = create_cuenta
        max_length = cuenta._meta.get_field('nombre').max_length
        assert max_length == 50

    def test_delete_protected_account(self, create_cuenta):
        cuenta = create_cuenta
        nombre = cuenta.nombre
        movimiento = Movimiento.objects.create(
            num = 1,
            fecha = "2021-12-07",
            descripcion = "Movimiento de prueba",
            debe = 250,
            haber = 0,
            cuenta = cuenta
        )

        with pytest.raises(ProtectedError):
            cuenta.delete()


class TestAsientoModel():
    @pytest.fixture
    def create_movimiento(self):
        # Set up non-modified objects used by all test methods
        cuenta = Cuenta.objects.create(num='100', nombre='Cuenta nómina')
        movimiento = Movimiento.objects.create(
            num = 1,
            fecha = "2021-12-07",
            descripcion = "Movimiento de prueba",
            debe = 250,
            haber = 0,
            cuenta = cuenta
        )
        return cuenta, movimiento

    def test_object_name_is_num(self, create_movimiento):
        _, movimiento = create_movimiento
        expected_name = str(movimiento.num)
        assert str(movimiento) == expected_name

    def test_descripcion_max_length(self, create_movimiento):
        _, movimiento = create_movimiento
        max_length = movimiento._meta.get_field('descripcion').max_length
        assert max_length == 200

    def test_debe_has_two_decimals(self, create_movimiento):
        _, movimiento = create_movimiento
        movimiento.debe = 10 / 3
        movimiento.save()
        movimiento = Movimiento.objects.get(pk=1)
        assert str(movimiento.debe) == '3.33'
        movimiento.debe = 5
        movimiento.save()
        movimiento = Movimiento.objects.get(pk=1)
        assert str(movimiento.debe) == '5.00'

    def test_haber_has_two_decimals(self, create_movimiento):
        _, movimiento = create_movimiento
        movimiento.haber = 10 / 3
        movimiento.save()
        movimiento = Movimiento.objects.get(pk=1)
        assert str(movimiento.haber) == '3.33'
        movimiento.haber = 5
        movimiento.save()
        movimiento = Movimiento.objects.get(pk=1)
        assert str(movimiento.haber) == '5.00'

    def test_debe_has_eight_digits_max(self, create_movimiento):
        _, movimiento = create_movimiento
        movimiento.debe = 1234567890
        with pytest.raises(InvalidOperation):
            movimiento.save()

    def test_debe_ok_if_less_than_eight_digits(self, create_movimiento):
        _, movimiento = create_movimiento
        movimiento.debe = 123456
        movimiento.save()
        movimiento = Movimiento.objects.get(pk=1)
        assert movimiento.debe == 123456

    def test_haber_has_eight_digits_max(self, create_movimiento):
        _, movimiento = create_movimiento
        movimiento.haber = 1234567890
        with pytest.raises(InvalidOperation):
            movimiento.save()

    def test_haber_ok_if_less_than_eight_digits(self, create_movimiento):
        _, movimiento = create_movimiento
        movimiento.haber = 123456
        movimiento.save()
        movimiento = Movimiento.objects.get(pk=1)
        assert movimiento.haber == 123456.00


class TestFiltroCuentas():
    @pytest.fixture
    def create_filtro_cuentas(self):
        # Set up non-modified objects used by all test methods
        return  FiltroCuentas.objects.create()

    def test_num_max_length(self, create_filtro_cuentas):
        filtro = create_filtro_cuentas
        max_length = filtro._meta.get_field('num').max_length
        assert max_length == 10

    def test_nombre_max_length(self, create_filtro_cuentas):
        filtro = create_filtro_cuentas
        max_length = filtro._meta.get_field('nombre').max_length
        assert max_length == 50

    def test_campo_max_length(self, create_filtro_cuentas):
        filtro = create_filtro_cuentas
        max_length = filtro._meta.get_field('campo').max_length
        assert max_length == 10

    def test_num_default(self, create_filtro_cuentas):
        filtro = create_filtro_cuentas
        assert filtro.num == ''

    def test_nombre_default(self, create_filtro_cuentas):
        filtro = create_filtro_cuentas
        assert filtro.nombre == ''

    def test_campo_default(self, create_filtro_cuentas):
        filtro = create_filtro_cuentas
        assert filtro.campo == 'num'

    def test_ascendiente_default(self, create_filtro_cuentas):
        filtro = create_filtro_cuentas
        assert filtro.ascendiente is True

    def test_campo_choices(self, create_filtro_cuentas):
        filtro = create_filtro_cuentas
        filtro.num = '100'
        filtro.nombre = 'Caja'
        for c in ['num', 'nombre']:
            filtro.campo = c
            filtro.save()
            filtro.full_clean()

        filtro.campo = 'wrong'
        filtro.save()
        with pytest.raises(ValidationError):
            filtro.full_clean()


class TestFiltroMovimientos():
    @pytest.fixture
    def create_filtro_movimientos(self):
        # Set up non-modified objects used by all test methods
        return FiltroMovimientos.objects.create()

    def test_fecha_inicial_max_length(self, create_filtro_movimientos):
        filtro = create_filtro_movimientos
        max_length = filtro._meta.get_field('fecha_inicial').max_length
        assert max_length == 10

    def test_fecha_final_max_length(self, create_filtro_movimientos):
        filtro = create_filtro_movimientos
        max_length = filtro._meta.get_field('fecha_final').max_length
        assert max_length == 10

    def test_descripcion_max_length(self, create_filtro_movimientos):
        filtro = create_filtro_movimientos
        max_length = filtro._meta.get_field('descripcion').max_length
        assert max_length == 200

    def test_cuenta_max_length(self, create_filtro_movimientos):
        filtro = create_filtro_movimientos
        max_length = filtro._meta.get_field('cuenta').max_length
        assert max_length == 10

    def test_asiento_max_length(self, create_filtro_movimientos):
        filtro = create_filtro_movimientos
        max_length = filtro._meta.get_field('asiento').max_length
        assert max_length == 10

    def test_campo_max_length(self, create_filtro_movimientos):
        filtro = create_filtro_movimientos
        max_length = filtro._meta.get_field('campo').max_length
        assert max_length == 15

    def test_fecha_inicial_default(self, create_filtro_movimientos):
        filtro = create_filtro_movimientos
        assert filtro.fecha_inicial == ''

    def test_fecha_final_default(self, create_filtro_movimientos):
        filtro = create_filtro_movimientos
        assert filtro.fecha_final == ''

    def test_descripcion_default(self, create_filtro_movimientos):
        filtro = create_filtro_movimientos
        assert filtro.descripcion == ''

    def test_cuenta_default(self, create_filtro_movimientos):
        filtro = create_filtro_movimientos
        assert filtro.cuenta == ''

    def test_asiento_default(self, create_filtro_movimientos):
        filtro = create_filtro_movimientos
        assert filtro.asiento == ''

    def test_campo_default(self, create_filtro_movimientos):
        filtro = create_filtro_movimientos
        assert filtro.campo == 'num'

    def test_campo_choices(self, create_filtro_movimientos):
        filtro = create_filtro_movimientos
        filtro.fecha_inicial = '2021-10-31'
        filtro.fecha_final = '2021-12-31'
        filtro.descripcion = 'Probando'
        filtro.cuenta = '100'
        filtro.asiento = '1'
        for c in ['num', 'fecha', 'descripcion', 'debe', 'haber', 'cuenta']:
            filtro.campo = c
            filtro.save()
            filtro.full_clean()

        filtro.campo = 'wrong'
        filtro.save()
        with pytest.raises(ValidationError):
            filtro.full_clean()
