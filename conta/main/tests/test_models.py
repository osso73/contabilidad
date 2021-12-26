from django.test import TestCase
from unittest import skip

from main.models import Cuenta, Movimiento
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

    @skip("Needs an exception mgmt function")
    def test_debe_has_eight_digits_max(self):
        self.movimiento.debe = 1234567890
        self.movimiento.save()
        self.movimiento = Movimiento.objects.get(pk=1)
        self.assertNotEqual(self.movimiento.debe, 1234567890)
        self.movimiento.debe = 123456
        self.movimiento.save()
        self.movimiento = Movimiento.objects.get(pk=1)
        self.assertEqual(self.movimiento.debe, 123456.00)

    @skip("Needs an exception mgmt function")
    def test_haber_has_eight_digits_max(self):
        self.movimiento.haber = 1234567890
        self.movimiento.save()
        self.movimiento = Movimiento.objects.get(pk=1)
        self.assertNotEqual(self.movimiento.haber, 1234567890)
        self.movimiento.haber = 123456
        self.movimiento.save()
        self.movimiento = Movimiento.objects.get(pk=1)
        self.assertEqual(self.movimiento.haber, 123456.00)
