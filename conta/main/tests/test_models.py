from django.test import TestCase
from unittest import skip
from decimal import InvalidOperation

from main.models import Cuenta, Movimiento, FiltroCuentas, FiltroMovimientos
from django.db.models.deletion import ProtectedError


class CuentaModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        cls.cuenta = Cuenta.objects.create(num='100', nombre='Cuenta nómina')

    def test_object_name_is_num_colon_nombre(self):
        expected_name = f'{self.cuenta.num}: {self.cuenta.nombre}'
        self.assertEqual(str(self.cuenta), expected_name)

    def test_nombre_max_length(self):
        max_length = self.cuenta._meta.get_field('nombre').max_length
        self.assertEqual(max_length, 50)

    def test_delete_protected_account(self):
        nombre = self.cuenta.nombre
        movimiento = Movimiento.objects.create(
            num = 1,
            fecha = "2021-12-07",
            descripcion = "Movimiento de prueba",
            debe = 250,
            haber = 0,
            cuenta = self.cuenta
        )

        with self.assertRaises(ProtectedError):
            self.cuenta.delete()


class AsientoModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        cls.cuenta = cuenta = Cuenta.objects.create(num='100', nombre='Cuenta nómina')
        cls.movimiento = Movimiento.objects.create(
            num = 1,
            fecha = "2021-12-07",
            descripcion = "Movimiento de prueba",
            debe = 250,
            haber = 0,
            cuenta = cls.cuenta
        )

    def test_object_name_is_num(self):
        expected_name = str(self.movimiento.num)
        self.assertEqual(str(self.movimiento), expected_name)

    def test_descripcion_max_length(self):
        max_length = self.movimiento._meta.get_field('descripcion').max_length
        self.assertEqual(max_length, 200)

    def test_debe_has_two_decimals(self):
        self.movimiento.debe = 10 / 3
        self.movimiento.save()
        self.movimiento = Movimiento.objects.get(pk=1)
        self.assertEqual(float(self.movimiento.debe), 3.33)
        self.movimiento.debe = 5
        self.movimiento.save()
        self.movimiento = Movimiento.objects.get(pk=1)
        self.assertEqual(float(self.movimiento.debe), 5.00)

    def test_haber_has_two_decimals(self):
        self.movimiento.haber = 10 / 3
        self.movimiento.save()
        self.movimiento = Movimiento.objects.get(pk=1)
        self.assertEqual(float(self.movimiento.haber), 3.33)
        self.movimiento.haber = 5
        self.movimiento.save()
        self.movimiento = Movimiento.objects.get(pk=1)
        self.assertEqual(float(self.movimiento.haber), 5.00)

    def test_debe_has_eight_digits_max(self):
        self.movimiento.debe = 1234567890
        with self.assertRaises(InvalidOperation):
            self.movimiento.save()

    def test_debe_ok_if_less_than_eight_digits(self):
        self.movimiento.debe = 123456
        self.movimiento.save()
        self.movimiento = Movimiento.objects.get(pk=1)
        self.assertEqual(self.movimiento.debe, 123456.00)

    def test_haber_has_eight_digits_max(self):
        self.movimiento.haber = 1234567890
        with self.assertRaises(InvalidOperation):
            self.movimiento.save()

    def test_haber_ok_if_less_than_eight_digits(self):
        self.movimiento.haber = 123456
        self.movimiento.save()
        self.movimiento = Movimiento.objects.get(pk=1)
        self.assertEqual(self.movimiento.haber, 123456.00)
        

class FiltroCuentasTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        cls.filtro = FiltroCuentas.objects.create()

    def test_num_max_length(self):
        max_length = self.filtro._meta.get_field('num').max_length
        self.assertEqual(max_length, 10)

    def test_nombre_max_length(self):
        max_length = self.filtro._meta.get_field('nombre').max_length
        self.assertEqual(max_length, 50)

    def test_num_default(self):
        self.assertEqual(self.filtro.num, '')

    def test_nombre_default(self):
        self.assertEqual(self.filtro.nombre, '')



class FiltroMovimientosTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        cls.filtro = FiltroMovimientos.objects.create()

    def test_fecha_inicial_max_length(self):
        max_length = self.filtro._meta.get_field('fecha_inicial').max_length
        self.assertEqual(max_length, 10)

    def test_fecha_final_max_length(self):
        max_length = self.filtro._meta.get_field('fecha_final').max_length
        self.assertEqual(max_length, 10)

    def test_descripcion_max_length(self):
        max_length = self.filtro._meta.get_field('descripcion').max_length
        self.assertEqual(max_length, 200)

    def test_cuenta_max_length(self):
        max_length = self.filtro._meta.get_field('cuenta').max_length
        self.assertEqual(max_length, 10)

    def test_asiento_max_length(self):
        max_length = self.filtro._meta.get_field('asiento').max_length
        self.assertEqual(max_length, 10)

    def test_fecha_inicial_default(self):
        self.assertEqual(self.filtro.fecha_inicial, '')

    def test_fecha_final_default(self):
        self.assertEqual(self.filtro.fecha_final, '')

    def test_descripcion_default(self):
        self.assertEqual(self.filtro.descripcion, '')

    def test_cuenta_default(self):
        self.assertEqual(self.filtro.cuenta, '')

    def test_asiento_default(self):
        self.assertEqual(self.filtro.asiento, '')
