import datetime

from django.test import TestCase
from django.urls import reverse

from main.models import Cuenta, Movimiento


class IndexViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        """test absolute URL (excluding domain)"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """test URL from domain configuration in urls.py"""
        response = self.client.get(reverse('main:index'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('main:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/index.html')


class CuentasViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        """test absolute URL (excluding domain)"""
        response = self.client.get('/cuentas/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """test URL from domain configuration in urls.py"""
        response = self.client.get(reverse('main:cuentas'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('main:cuentas'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/cuentas.html')


class AsientosViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        """test absolute URL (excluding domain)"""
        response = self.client.get('/asientos/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """test URL from domain configuration in urls.py"""
        response = self.client.get(reverse('main:asientos'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('main:asientos'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/asientos.html')


class ModificarAsientoViewTest(TestCase):
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

    def test_view_url_exists_at_desired_location(self):
        """test absolute URL (excluding domain)"""
        response = self.client.get('/modificar/asiento/1/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """test URL from domain configuration in urls.py"""
        response = self.client.get(reverse('main:modificar_asiento', args=[1]))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('main:modificar_asiento', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/modificar_asiento.html')


class ModificarCuentaViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Cuenta.objects.create(num='100', nombre='Cuenta nómina')

    def test_view_url_exists_at_desired_location(self):
        """test absolute URL (excluding domain)"""
        response = self.client.get('/modificar/cuenta/100/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """test URL from domain configuration in urls.py"""
        response = self.client.get(reverse('main:modificar_cuenta', args=[100]))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('main:modificar_cuenta', args=[100]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/modificar_cuenta.html')


class AnadirMovimientoViewTest(TestCase):
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

    def test_view_url_creates_new_movimiento_by_url(self):
        """test absolute URL"""
        self.client.get('/anadir/movimiento/1/2021-08-07/')
        lista_movimientos = Movimiento.objects.all()
        self.assertEqual(len(lista_movimientos), 2)
        last = lista_movimientos[1]
        self.assertEqual(last.fecha, datetime.date(day=7, month=8, year=2021))

    def test_view_url_creates_new_movimiento_by_name(self):
        """test URL from domain configuration in urls.py"""
        self.client.get(reverse('main:anadir_movimiento', args=[1, '2021-08-15']))
        lista_movimientos = Movimiento.objects.all()
        self.assertEqual(len(lista_movimientos), 2)
        last = lista_movimientos[1]
        self.assertEqual(last.fecha, datetime.date(day=15, month=8, year=2021))

    def test_view_redirect(self):
        """test that view is redirected to the right page"""
        resp = self.client.get('/anadir/movimiento/1/2021-08-07/', follow=True)
        self.assertEqual(len(resp.redirect_chain), 1)
        page_redirected = resp.redirect_chain[0][0]
        self.assertEqual(page_redirected, '/modificar/asiento/1/')


class BorrarMovimientoViewTest(TestCase):
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

    def test_view_url_creates_new_movimiento_by_url(self):
        """test absolute URL simple"""
        lista_movimientos = Movimiento.objects.all()
        self.assertEqual(len(lista_movimientos), 1)
        self.client.get('/borrar/movimiento/1/asientos/')
        lista_movimientos = Movimiento.objects.all()
        self.assertEqual(len(lista_movimientos), 0)

    def test_view_url_creates_new_movimiento_by_name(self):
        """test URL from domain configuration in urls.py simple"""
        lista_movimientos = Movimiento.objects.all()
        self.assertEqual(len(lista_movimientos), 1)
        self.client.get(reverse('main:borrar_movimiento', args=[1, 'asientos']))
        lista_movimientos = Movimiento.objects.all()
        self.assertEqual(len(lista_movimientos), 0)

    def test_view_redirect_simple(self):
        """test that view is redirected to the right page"""
        resp = self.client.get('/borrar/movimiento/1/asientos/', follow=True)
        self.assertEqual(len(resp.redirect_chain), 1)
        page_redirected = resp.redirect_chain[0][0]
        self.assertEqual(page_redirected, '/asientos/')

    def test_view_url_creates_new_movimiento_by_url_extra(self):
        """test absolute URL complex"""
        lista_movimientos = Movimiento.objects.all()
        self.assertEqual(len(lista_movimientos), 1)
        self.client.get('/borrar/movimiento/1/modificar_asiento/1/')
        lista_movimientos = Movimiento.objects.all()
        self.assertEqual(len(lista_movimientos), 0)

    def test_view_url_creates_new_movimiento_by_name_extra(self):
        """test URL from domain configuration in urls.py complex"""
        lista_movimientos = Movimiento.objects.all()
        self.assertEqual(len(lista_movimientos), 1)
        self.client.get(reverse('main:borrar_movimiento_complejo', args=[1, 'modificar_asiento', 1]))
        lista_movimientos = Movimiento.objects.all()
        self.assertEqual(len(lista_movimientos), 0)

    def test_view_redirect_complex(self):
        """test that view is redirected to the right page"""
        # adding a second movimiento to enable removal (otherwise it gives error)
        Movimiento.objects.create(
            num = 1,
            fecha = "2021-12-07",
            descripcion = "Movimiento de prueba",
            debe = 0,
            haber = 250,
            cuenta = Cuenta.objects.get(num=100)
        )
        resp = self.client.get('/borrar/movimiento/1/modificar_asiento/1/', follow=True)
        self.assertEqual(len(resp.redirect_chain), 1)
        page_redirected = resp.redirect_chain[0][0]
        self.assertEqual(page_redirected, '/modificar/asiento/1/')



class BorrarCuentaViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        cuenta = Cuenta.objects.create(num='100', nombre='Cuenta nómina')

    def test_view_url_creates_new_movimiento_by_url(self):
        """test absolute URL"""
        lista_cuentas = Cuenta.objects.all()
        self.assertEqual(len(lista_cuentas), 1)
        self.client.get('/borrar/cuenta/100/')
        lista_cuentas = Cuenta.objects.all()
        self.assertEqual(len(lista_cuentas), 0)

    def test_view_url_creates_new_movimiento_by_name(self):
        """test URL from domain configuration in urls.py"""
        lista_cuentas = Cuenta.objects.all()
        self.assertEqual(len(lista_cuentas), 1)
        self.client.get(reverse('main:borrar_cuenta', args=[100]))
        lista_cuentas = Cuenta.objects.all()
        self.assertEqual(len(lista_cuentas), 0)

    def test_view_redirect(self):
        """test that view is redirected to the right page"""
        resp = self.client.get('/borrar/cuenta/100/', follow=True)
        self.assertEqual(len(resp.redirect_chain), 1)
        page_redirected = resp.redirect_chain[0][0]
        self.assertEqual(page_redirected, '/cuentas/')
