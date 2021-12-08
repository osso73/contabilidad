from django.test import TestCase
from unittest import skip

from main.models import Cuenta, Movimiento


class CuentaModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Cuenta.objects.create(num='100', nombre='Cuenta nómina')

    def test_object_name_is_num_colon_nombre(self):
        cuenta = Cuenta.objects.get(pk='100')
        expected_name = f'{cuenta.num}: {cuenta.nombre}'
        self.assertEqual(str(cuenta), expected_name)

    def test_nombre_max_length(self):
        cuenta = Cuenta.objects.get(pk='100')
        max_length = cuenta._meta.get_field('nombre').max_length
        self.assertEqual(max_length, 50)




class AsientoModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        cuenta = Cuenta.objects.create(num='100', nombre='Cuenta nómina')
        Movimiento.objects.create(
            num = 1,
            fecha = "2021-12-07",
            descripcion = "Movimiento de prueba",
            debe = 250,
            haber = 0,
            cuenta = cuenta
        )

    def test_object_name_is_num(self):
        movimiento = Movimiento.objects.get(pk=1)
        expected_name = str(movimiento.num)
        self.assertEqual(str(movimiento), expected_name)

    def test_descripcion_max_length(self):
        movimiento = Movimiento.objects.get(pk=1)
        max_length = movimiento._meta.get_field('descripcion').max_length
        self.assertEqual(max_length, 200)

    def test_debe_has_two_decimals(self):
        movimiento = Movimiento.objects.get(pk=1)
        movimiento.debe = 10 / 3
        movimiento.save()
        movimiento = Movimiento.objects.get(pk=1)
        self.assertEqual(float(movimiento.debe), 3.33)
        movimiento.debe = 5
        movimiento.save()
        movimiento = Movimiento.objects.get(pk=1)
        self.assertEqual(float(movimiento.debe), 5.00)

    def test_haber_has_two_decimals(self):
        movimiento = Movimiento.objects.get(pk=1)
        movimiento.haber = 10 / 3
        movimiento.save()
        movimiento = Movimiento.objects.get(pk=1)
        self.assertEqual(float(movimiento.haber), 3.33)
        movimiento.haber = 5
        movimiento.save()
        movimiento = Movimiento.objects.get(pk=1)
        self.assertEqual(float(movimiento.haber), 5.00)

    @skip("Needs an exception mgmt function")
    def test_debe_has_eight_digits_max(self):
        movimiento = Movimiento.objects.get(pk=1)
        movimiento.debe = 1234567890
        movimiento.save()
        movimiento = Movimiento.objects.get(pk=1)
        self.assertNotEqual(movimiento.debe, 1234567890)
        movimiento.debe = 123456
        movimiento.save()
        movimiento = Movimiento.objects.get(pk=1)
        self.assertEqual(movimiento.debe, 123456.00)

    @skip("Needs an exception mgmt function")
    def test_haber_has_eight_digits_max(self):
        movimiento = Movimiento.objects.get(pk=1)
        movimiento.haber = 1234567890
        movimiento.save()
        movimiento = Movimiento.objects.get(pk=1)
        self.assertNotEqual(movimiento.haber, 1234567890)
        movimiento.haber = 123456
        movimiento.save()
        movimiento = Movimiento.objects.get(pk=1)
        self.assertEqual(movimiento.haber, 123456.00)
