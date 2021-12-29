import datetime

from django.test import TestCase
from django.urls import reverse
from django_webtest import WebTest
from webtest import Upload
from unittest import skip

from main.models import Cuenta, Movimiento, FiltroCuentas, FiltroMovimientos


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


class CuentasViewTest(WebTest):
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

    def test_list_of_cuentas(self):
        cuentas = {
            '100': 'Caja',
            '101': 'Tickets restaurant',
            '1101': 'Cuenta nómina',
            '1110': 'Cuenta ahorro',
            '1200': 'Tarjeta Visa',
            '1201': 'Tarjeta Amex',
            '1210': 'Tarjeta prepago',
            '15': 'Hipoteca',
            '2001': 'Gas casa',
            '2000': 'Electricidad casa',
            '203': 'Impuestos casa',
            '300': 'Comida',
            '312': 'Cenas, pinchos…',
            '324': 'Gastos coche',
        }
        for num, nombre in cuentas.items():
            Cuenta.objects.create(num=num, nombre=nombre)

        resp = self.app.get('/cuentas/')
        for num, nombre in cuentas.items():
            self.assertIn(num, resp)
            self.assertIn(nombre, resp)

    def test_create_new_cuenta_form_attributes(self):
        resp = self.app.get('/cuentas/')
        form = resp.forms['crear_cuenta']

        self.assertEqual(form.id, 'crear_cuenta')
        self.assertEqual(form.method, 'post')
        self.assertEqual(form.action, '/cuentas/')
        self.assertEqual(form.action, reverse('main:cuentas'))

        fields = form.fields.keys()
        for f in ['num', 'nombre']:
            self.assertIn(f, fields)

    def test_create_new_cuenta(self):
        resp = self.app.get('/cuentas/')
        form = resp.forms['crear_cuenta']

        form['num'] = '100'
        form['nombre'] = 'Caja'
        form.submit()

        # check that account exists in the database
        cuentas = Cuenta.objects.all()
        self.assertEqual(len(cuentas), 1)
        self.assertEqual(cuentas[0].num, '100')
        self.assertEqual(cuentas[0].nombre, 'Caja')


class AsientosViewTest(WebTest):
    @classmethod
    def setUpTestData(cls):
        cls.lista_cuentas = []
        cuentas = {
            '100': 'Caja',
            '101': 'Tickets restaurant',
            '1101': 'Cuenta nómina',
            '1110': 'Cuenta ahorro',
            '1200': 'Tarjeta Visa',
            '1201': 'Tarjeta Amex',
            '1210': 'Tarjeta prepago',
            '15': 'Hipoteca',
            '2001': 'Gas casa',
            '2000': 'Electricidad casa',
            '203': 'Impuestos casa',
            '300': 'Comida',
            '312': 'Cenas, pinchos…',
            '324': 'Gastos coche',
        }
        for num, nombre in cuentas.items():
            c = Cuenta.objects.create(num=num, nombre=nombre)
            cls.lista_cuentas.append(c)

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


    def test_list_of_movimientos(self):
        lista_movimientos = list()
        m = Movimiento.objects.create(num=1, fecha="2021-12-28",
            descripcion="Pan", debe=2.50, haber=0, cuenta=self.lista_cuentas[0])
        lista_movimientos.append(m)
        m = Movimiento.objects.create(num=1, fecha="2021-12-28",
            descripcion="Pan", debe=0, haber=2.50, cuenta=self.lista_cuentas[3])
        lista_movimientos.append(m)
        m = Movimiento.objects.create(num=2, fecha="2021-12-15",
            descripcion="Fruta", debe=10.75, haber=0, cuenta=self.lista_cuentas[0])
        lista_movimientos.append(m)
        m = Movimiento.objects.create(num=2, fecha="2021-12-15",
            descripcion="Fruta", debe=0, haber=10.75, cuenta=self.lista_cuentas[3])
        lista_movimientos.append(m)
        m = Movimiento.objects.create(num=3, fecha="2021-12-18",
            descripcion="Calcetines", debe=15.85, haber=0, cuenta=self.lista_cuentas[1])
        lista_movimientos.append(m)
        m = Movimiento.objects.create(num=3, fecha="2021-12-18",
            descripcion="Calcetines", debe=0, haber=15.85, cuenta=self.lista_cuentas[3])
        lista_movimientos.append(m)
        m = Movimiento.objects.create(num=4, fecha="2021-12-20",
            descripcion="Abrigo", debe=54, haber=0, cuenta=self.lista_cuentas[1])
        lista_movimientos.append(m)
        m = Movimiento.objects.create(num=4, fecha="2021-12-20",
            descripcion="Abrigo", debe=0, haber=54, cuenta=self.lista_cuentas[3])
        lista_movimientos.append(m)

        resp = self.app.get('/asientos/')
        for mov in lista_movimientos:
            self.assertIn(str(mov.descripcion), resp)

    def test_add_simple_asiento_form_attributes(self):
        resp = self.app.get('/asientos/')
        form = resp.forms['crear_asiento']

        self.assertEqual(form.id, 'crear_asiento')
        self.assertEqual(form.method, 'post')
        self.assertEqual(form.action, '/asientos/')
        self.assertEqual(form.action, reverse('main:asientos'))

        fields = form.fields.keys()
        for f in ['fecha', 'descripcion', 'valor', 'debe', 'haber']:
            self.assertIn(f, fields)

    def test_add_simple_asiento(self):
        resp = self.app.get('/asientos/')
        form = resp.forms['crear_asiento']

        form['fecha'] = '2021-12-28'
        form['descripcion'] = 'Compras en el super'
        form['valor'] = '34'
        form['debe'] = '100'
        form['haber'] = '300'
        form.submit()

        # check movimientos are created in the database
        movimientos = Movimiento.objects.all()
        self.assertEqual(len(movimientos), 2)
        self.assertEqual(movimientos[0].num, 1)
        self.assertEqual(movimientos[0].fecha, datetime.date(2021, 12, 28))
        self.assertEqual(movimientos[0].descripcion, 'Compras en el super')
        self.assertEqual(movimientos[0].debe, 34)
        self.assertEqual(movimientos[0].haber, 0)
        self.assertEqual(movimientos[0].cuenta.num, '100')
        self.assertEqual(movimientos[0].cuenta.nombre, 'Caja')

        self.assertEqual(movimientos[1].num, 1)
        self.assertEqual(movimientos[1].fecha, datetime.date(2021, 12, 28))
        self.assertEqual(movimientos[1].descripcion, 'Compras en el super')
        self.assertEqual(movimientos[1].debe, 0)
        self.assertEqual(movimientos[1].haber, 34)
        self.assertEqual(movimientos[1].cuenta.num, '300')
        self.assertEqual(movimientos[1].cuenta.nombre, 'Comida')


class ModificarAsientoViewTest(WebTest):
    def setUp(self):
        # Set up non-modified objects used by all test methods
        cuenta = Cuenta.objects.create(num='100', nombre='Cuenta nómina')
        Movimiento.objects.create(num=1, fecha="2021-12-07",
            descripcion = "Prueba", debe=250, haber=0, cuenta=cuenta)

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

    def test_form_attributes(self):
        resp = self.app.get('/modificar/asiento/1/')
        form = resp.forms['formulario']

        self.assertEqual(form.id, 'formulario')
        self.assertEqual(form.method, 'post')
        self.assertEqual(form.action, '/modificar/asiento/1/')
        self.assertEqual(form.action, reverse('main:modificar_asiento', args=[1]))

        fields = form.fields.keys()
        for f in ['id0', 'num0', 'fecha0', 'descripcion0', 'debe0', 'haber0', 'cuenta0']:
            self.assertIn(f, fields)

    def test_modify_asiento(self):
        resp = self.app.get('/modificar/asiento/1/')
        form = resp.forms['formulario']
        form['num0'] = '2'
        form.submit()

        movimiento = Movimiento.objects.all()[0]
        self.assertEqual(movimiento.num, 2)

    def test_modify_fecha(self):
        resp = self.app.get('/modificar/asiento/1/')
        form = resp.forms['formulario']
        form['fecha0'] = '2021-12-31'
        form.submit()

        movimiento = Movimiento.objects.all()[0]
        self.assertEqual(movimiento.fecha, datetime.date(2021, 12, 31))

    def test_modify_descripcion(self):
        resp = self.app.get('/modificar/asiento/1/')
        form = resp.forms['formulario']
        form['descripcion0'] = 'Nueva descripcion'
        form.submit()

        movimiento = Movimiento.objects.all()[0]
        self.assertEqual(movimiento.descripcion, 'Nueva descripcion')

    def test_modify_debe(self):
        resp = self.app.get('/modificar/asiento/1/')
        form = resp.forms['formulario']
        form['debe0'] = '243.87'
        form.submit()

        movimiento = Movimiento.objects.all()[0]
        self.assertEqual(float(movimiento.debe), 243.87)

    def test_modify_haber(self):
        resp = self.app.get('/modificar/asiento/1/')
        form = resp.forms['formulario']
        form['haber0'] = '521.67'
        form.submit()

        movimiento = Movimiento.objects.all()[0]
        self.assertEqual(float(movimiento.haber), 521.67)

    def test_modify_cuenta(self):
        Cuenta.objects.create(num='150', nombre='Tarjeta visa')
        resp = self.app.get('/modificar/asiento/1/')
        form = resp.forms['formulario']
        form['cuenta0'] = '150'
        form.submit()

        movimiento = Movimiento.objects.all()[0]
        self.assertEqual(movimiento.cuenta.num, '150')
        self.assertEqual(movimiento.cuenta.nombre, 'Tarjeta visa')

    def test_add_movimiento(self):
        resp = self.app.get('/modificar/asiento/1/')
        resp.click(linkid='anadir_movimiento')

        mov = Movimiento.objects.all()
        self.assertEqual(len(mov), 2)
        self.assertEqual(mov[1].num, 1)
        self.assertEqual(mov[1].fecha, datetime.date(2021, 12, 7))
        self.assertEqual(mov[1].descripcion, '')
        self.assertEqual(float(mov[1].debe), 0.0)
        self.assertEqual(float(mov[1].haber), 0.0)
        self.assertEqual(mov[1].cuenta.num, '100')



class ModificarCuentaViewTest(WebTest):
    def setUp(self):
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

    def test_form_attributes(self):
        resp = self.app.get('/modificar/cuenta/100/')
        form = resp.forms['formulario']

        self.assertEqual(form.id, 'formulario')
        self.assertEqual(form.method, 'post')
        self.assertEqual(form.action, '/modificar/cuenta/100/')
        self.assertEqual(form.action, reverse('main:modificar_cuenta', args=[100]))

        fields = form.fields.keys()
        for f in ['num', 'nombre']:
            self.assertIn(f, fields)

    def test_modify_nombre(self):
        resp = self.app.get('/modificar/cuenta/100/')
        form = resp.forms['formulario']
        form['nombre'] = 'Tarjeta visa'
        form.submit()

        cuenta = Cuenta.objects.all()[0]
        self.assertEqual(cuenta.nombre, 'Tarjeta visa')


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


class AnadirMovimientoViewTest(WebTest):
    def setUp(self):
        # Set up non-modified objects used by all test methods
        cuenta = Cuenta.objects.create(num='100', nombre='Cuenta nómina')
        Movimiento.objects.create(num=1, fecha="2021-12-07",
            descripcion = "Prueba", debe=250, haber=0, cuenta=cuenta)

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

    def test_add_movimiento(self):
        resp = self.client.get('/anadir/movimiento/1/2021-08-07/')

        mov = Movimiento.objects.all()
        self.assertEqual(len(mov), 2)
        self.assertEqual(mov[1].num, 1)
        self.assertEqual(mov[1].fecha, datetime.date(2021, 8, 7))
        self.assertEqual(mov[1].descripcion, '')
        self.assertEqual(float(mov[1].debe), 0.0)
        self.assertEqual(float(mov[1].haber), 0.0)
        self.assertEqual(mov[1].cuenta.num, '100')



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


class CargarCuentasTest(WebTest):
    def test_redirect_get_requests_by_url(self):
        resp = self.client.get('/cargar/cuentas/', follow=True)
        self.assertEqual(len(resp.redirect_chain), 1)
        page_redirected = resp.redirect_chain[0][0]
        self.assertEqual(page_redirected, '/cuentas/')

    def test_redirect_get_requests_by_name(self):
        resp = self.client.get(reverse('main:cargar_cuentas'), follow=True)
        self.assertEqual(len(resp.redirect_chain), 1)
        page_redirected = resp.redirect_chain[0][0]
        self.assertEqual(page_redirected, '/cuentas/')

    def test_load_file_form_attributes(self):
        resp = self.app.get('/cuentas/')
        form = resp.forms['cargar_fichero']

        self.assertEqual(form.id, 'cargar_fichero')
        self.assertEqual(form.method, 'post')
        self.assertEqual(form.action, '/cargar/cuentas/')
        self.assertEqual(form.action, reverse('main:cargar_cuentas'))

        fields = form.fields.keys()
        self.assertIn('sobreescribir', fields)
        self.assertIn('file', fields)


    def test_load_file(self):
        # before loading, we have 0 cuentas
        cuentas = Cuenta.objects.all()
        self.assertEqual(len(cuentas), 0)
        resp = self.app.get('/cuentas/')
        form = resp.forms['cargar_fichero']

        form['file'] = Upload('main/tests/data/cuentas.xlsx')
        resp = form.submit()

        cuentas = [ c.num for c in Cuenta.objects.all() ]
        self.assertNotEqual(len(cuentas), 0)
        cuentas_check = {
            '100': 'Caja',
            '101': 'Tickets restaurant',
            '1101': 'Cuenta nómina',
            '1110': 'Cuenta ahorro',
            '1200': 'Tarjeta Visa',
            '1201': 'Tarjeta Amex',
            '1210': 'Tarjeta prepago',
            '300': 'Comida',
            '312': 'Cenas, pinchos…',
            '324': 'Gastos coche',
            '15': 'Hipoteca',
            '2001': 'Gas casa',
            '2000': 'Electricidad casa',
        }
        for c in cuentas_check:
            self.assertIn(c, cuentas)
            self.assertIn(c, resp)

    def test_load_file_sobreescribir(self):
        resp = self.app.get('/cuentas/')
        form = resp.forms['cargar_fichero']
        Cuenta.objects.create(num='100', nombre='Dinero')

        form['file'] = Upload('main/tests/data/cuentas.xlsx')
        form['sobreescribir'] = False
        resp = form.submit()

        cuentas = [ c.nombre for c in Cuenta.objects.all() ]
        self.assertNotIn('Caja', cuentas)
        self.assertIn('Dinero', cuentas)

        form['file'] = Upload('main/tests/data/cuentas.xlsx')
        form['sobreescribir'] = True
        resp = form.submit()

        cuentas = [ c.nombre for c in Cuenta.objects.all() ]
        self.assertNotIn('Dinero', cuentas)
        self.assertIn('Caja', cuentas)

    def test_load_file_error(self):
        """Load an incorrect file, it should show no cuentas loaded"""
        resp = self.app.get('/cuentas/')
        form = resp.forms['cargar_fichero']

        form['file'] = Upload('main/tests/data/empty_file.xlsx')
        resp = form.submit()

        cuentas = Cuenta.objects.all()
        self.assertEqual (len(cuentas), 0)


class CargarAsientosTest(WebTest):
    @classmethod
    def setUpTestData(cls):
        cls.lista_cuentas = []
        cuentas = {
            '100': 'Caja',
            '101': 'Tickets restaurant',
            '1101': 'Cuenta nómina',
            '1110': 'Cuenta ahorro',
            '1200': 'Tarjeta Visa',
            '1201': 'Tarjeta Amex',
            '1210': 'Tarjeta prepago',
            '15': 'Hipoteca',
            '2001': 'Gas casa',
            '2000': 'Electricidad casa',
            '203': 'Impuestos casa',
            '300': 'Comida',
            '312': 'Cenas, pinchos…',
            '324': 'Gastos coche',
        }
        for num, nombre in cuentas.items():
            c = Cuenta.objects.create(num=num, nombre=nombre)
            cls.lista_cuentas.append(c)

    def test_redirect_get_requests_by_url(self):
        resp = self.client.get('/cargar/asientos/', follow=True)
        self.assertEqual(len(resp.redirect_chain), 1)
        page_redirected = resp.redirect_chain[0][0]
        self.assertEqual(page_redirected, '/asientos/')

    def test_redirect_get_requests_by_name(self):
        resp = self.client.get(reverse('main:cargar_asientos'), follow=True)
        self.assertEqual(len(resp.redirect_chain), 1)
        page_redirected = resp.redirect_chain[0][0]
        self.assertEqual(page_redirected, '/asientos/')

    def test_load_file_form_attributes(self):
        resp = self.app.get('/asientos/')
        form = resp.forms['cargar_fichero']

        self.assertEqual(form.id, 'cargar_fichero')
        self.assertEqual(form.method, 'post')
        self.assertEqual(form.action, '/cargar/asientos/')
        self.assertEqual(form.action, reverse('main:cargar_asientos'))

        fields = form.fields.keys()
        self.assertIn('file', fields)

    def test_load_file(self):
        # before loading, we have 0 movimientos
        movimientos = Movimiento.objects.all()
        self.assertEqual(len(movimientos), 0)

        resp = self.app.get('/asientos/')
        form = resp.forms['cargar_fichero']
        form['file'] = Upload('main/tests/data/plantilla.xlsx')
        resp = form.submit()

        movimientos = [ c.descripcion for c in Movimiento.objects.all() ]
        self.assertNotEqual(len(movimientos), 0)
        movimientos_check = [
            'Cena en el restaurante',
            'Cena en el restaurante propina',
            'Factura EDP - gas y electricidad',
            'Factura EDP - gas',
            'Factura EDP - electricidad',
            'Pan',
            'Pizzas Telepizza',
            'Gasolina coche',
            'Hipoteca',
        ]
        for m in movimientos_check:
            self.assertIn(m, movimientos)
            self.assertIn(m, resp)

    def test_load_file_error(self):
        resp = self.app.get('/asientos/')
        form = resp.forms['cargar_fichero']
        form['file'] = Upload('main/tests/data/plantilla_errores.xlsx')
        resp = form.submit()

        movimientos = [ c.descripcion for c in Movimiento.objects.all() ]
        movimientos_ok = [
            'Compra pan',
            'Hipoteca',
            'Cena en el restaurante',
            'Cena en el restaurante propina',
            'Factura EDP - gas',
            ]
        movimientos_error = [
            'Pizzas Telepizza',
            'Gasolina coche',
            'Pago IBI',
            'Factura EDP - gas y electricidad',
            'Factura EDP - electricidad',
            ]

        messages = [
            'Ha habido 5 errores.',
            'Se han cargado 8 movimientos.',
            'Fecha incorrecta',
            'Cuenta no existe',
            'Valor es incorrecto',
            'Haber es incorrecto',
            'Debe es incorrecto',
        ]

        for m in movimientos_ok:
            self.assertIn(m, movimientos)
            self.assertIn(m, resp)

        for m in movimientos_error:
            self.assertNotIn(m, movimientos)
            self.assertIn(m, resp)

        for m in messages:
            self.assertIn(m, resp)


class FiltroCuentasViewTest(WebTest):
    @classmethod
    def setUpTestData(cls):
        cls.lista_cuentas = []
        # create some contents, that can be filtered for all tests
        c = Cuenta.objects.create(num='100', nombre='Caja')
        cls.lista_cuentas.append(c)
        c = Cuenta.objects.create(num='110', nombre='Tarjeta visa')
        cls.lista_cuentas.append(c)
        c = Cuenta.objects.create(num='111', nombre='Tarjeta Amex')
        cls.lista_cuentas.append(c)
        c = Cuenta.objects.create(num='300', nombre='Comida')
        cls.lista_cuentas.append(c)
        c = Cuenta.objects.create(num='301', nombre='Ropa')
        cls.lista_cuentas.append(c)


    def setUp(self):
        # Create filter with default values (all blanks)
        self.filtro = FiltroCuentas.objects.create()

    def test_redirect_get_requests_by_url(self):
        resp = self.client.get('/filtro/cuentas/', follow=True)
        self.assertEqual(len(resp.redirect_chain), 1)
        page_redirected = resp.redirect_chain[0][0]
        self.assertEqual(page_redirected, '/cuentas/')

    def test_redirect_get_requests_by_name(self):
        resp = self.client.get(reverse('main:filtro_cuentas'), follow=True)
        self.assertEqual(len(resp.redirect_chain), 1)
        page_redirected = resp.redirect_chain[0][0]
        self.assertEqual(page_redirected, '/cuentas/')

    def test_filter_form_attributes(self):
        resp = self.app.get('/cuentas/')
        form = resp.forms['filtro']

        self.assertEqual(form.id, 'filtro')
        self.assertEqual(form.method, 'post')
        self.assertEqual(form.action, '/filtro/cuentas/')
        self.assertEqual(form.action, reverse('main:filtro_cuentas'))

        fields = form.fields.keys()
        self.assertIn('f_num', fields)
        self.assertIn('f_nombre', fields)

    def test_filter_form_fill(self):
        resp = self.app.get('/cuentas/')
        form = resp.forms['filtro']
        form['f_num'] = '100'
        form['f_nombre'] = 'Pago'
        resp = form.submit()
        filtro = FiltroCuentas.objects.all()[0]
        self.assertEqual(filtro.num, '100')
        self.assertEqual(filtro.nombre, 'Pago')

    def test_apply_filter_num(self):
        # set the filter
        self.filtro.num = '300'
        self.filtro.save()

        lista_cuentas = [ c.nombre for c in self.lista_cuentas ]

        # check only account filtered appears
        resp = self.app.get('/cuentas/')
        self.assertIn('Comida', resp.text)
        for name in lista_cuentas:
            if name == 'Comida':
                continue
            self.assertNotIn(name, resp.text)

    def test_apply_filter_name(self):
        # set the filter
        self.filtro.nombre = 'Tarjeta'
        self.filtro.save()

        lista_cuentas = [ c.nombre for c in self.lista_cuentas ]

        # check only account filtered appears
        resp = self.app.get('/cuentas/')
        for name in lista_cuentas:
            if 'Tarjeta' in name:
                self.assertIn(name, resp.text)
            else:
                self.assertNotIn(name, resp.text)


class FiltroAsientosViewTest(WebTest):
    @classmethod
    def setUpTestData(cls):
        cls.lista_cuentas = []
        # create some contents, that can be filtered for all tests
        c = Cuenta.objects.create(num='100', nombre='Caja')
        cls.lista_cuentas.append(c)
        c = Cuenta.objects.create(num='110', nombre='Tarjeta visa')
        cls.lista_cuentas.append(c)
        c = Cuenta.objects.create(num='111', nombre='Tarjeta Amex')
        cls.lista_cuentas.append(c)
        c = Cuenta.objects.create(num='300', nombre='Comida')
        cls.lista_cuentas.append(c)
        c = Cuenta.objects.create(num='301', nombre='Ropa')
        cls.lista_cuentas.append(c)

        cls.lista_movimientos = []
        m = Movimiento.objects.create(num=1, fecha="2021-12-28",
            descripcion="Pan", debe=2.50, haber=0, cuenta=cls.lista_cuentas[0])
        cls.lista_movimientos.append(m)
        m = Movimiento.objects.create(num=1, fecha="2021-12-28",
            descripcion="Pan", debe=0, haber=2.50, cuenta=cls.lista_cuentas[3])
        cls.lista_movimientos.append(m)
        m = Movimiento.objects.create(num=2, fecha="2021-12-15",
            descripcion="Fruta", debe=10.75, haber=0, cuenta=cls.lista_cuentas[0])
        cls.lista_movimientos.append(m)
        m = Movimiento.objects.create(num=2, fecha="2021-12-15",
            descripcion="Fruta", debe=0, haber=10.75, cuenta=cls.lista_cuentas[3])
        cls.lista_movimientos.append(m)
        m = Movimiento.objects.create(num=3, fecha="2021-12-18",
            descripcion="Calcetines", debe=15.85, haber=0, cuenta=cls.lista_cuentas[1])
        cls.lista_movimientos.append(m)
        m = Movimiento.objects.create(num=3, fecha="2021-12-18",
            descripcion="Calcetines", debe=0, haber=15.85, cuenta=cls.lista_cuentas[3])
        cls.lista_movimientos.append(m)
        m = Movimiento.objects.create(num=4, fecha="2021-12-20",
            descripcion="Abrigo", debe=54, haber=0, cuenta=cls.lista_cuentas[1])
        cls.lista_movimientos.append(m)
        m = Movimiento.objects.create(num=4, fecha="2021-12-20",
            descripcion="Abrigo", debe=0, haber=54, cuenta=cls.lista_cuentas[3])
        cls.lista_movimientos.append(m)

    def setUp(self):
        # Create filter with default values (all blanks)
        self.filtro = FiltroMovimientos.objects.create()

    def test_redirect_get_requests_by_url(self):
        resp = self.client.get('/filtro/asientos/', follow=True)
        self.assertEqual(len(resp.redirect_chain), 1)
        page_redirected = resp.redirect_chain[0][0]
        self.assertEqual(page_redirected, '/asientos/')

    def test_redirect_get_requests_by_name(self):
        resp = self.client.get(reverse('main:filtro_asientos'), follow=True)
        self.assertEqual(len(resp.redirect_chain), 1)
        page_redirected = resp.redirect_chain[0][0]
        self.assertEqual(page_redirected, '/asientos/')

    def test_filter_form_attributes(self):
        resp = self.app.get('/asientos/')
        form = resp.forms['filtro']

        self.assertEqual(form.id, 'filtro')
        self.assertEqual(form.method, 'post')
        self.assertEqual(form.action, '/filtro/asientos/')
        self.assertEqual(form.action, reverse('main:filtro_asientos'))

        fields = form.fields.keys()
        for f in ['f_fecha_inicial', 'f_fecha_final', 'f_descripcion',
            'f_cuenta', 'f_asiento']:
            self.assertIn(f, fields)

    def test_filter_form_fill(self):
        resp = self.app.get('/asientos/')
        form = resp.forms['filtro']
        form['f_fecha_inicial'] = '2021-12-01'
        form['f_fecha_final'] = '2021-12-15'
        form['f_descripcion'] = 'descripcion palabras'
        form['f_cuenta'] = '100'
        form['f_asiento'] = '2'
        resp = form.submit()

        filtro = FiltroMovimientos.objects.all()[0]
        self.assertEqual(filtro.fecha_inicial, '2021-12-01')
        self.assertEqual(filtro.fecha_final, '2021-12-15')
        self.assertEqual(filtro.descripcion, 'descripcion palabras')
        self.assertEqual(filtro.cuenta, '100')
        self.assertEqual(filtro.asiento, '2')

    def test_apply_filter_fecha_inicial(self):
        # set the filter
        fecha = '2021-12-19'
        self.filtro.fecha_inicial = fecha
        self.filtro.save()

        movimientos_in = [ m.descripcion for m in self.lista_movimientos if m.fecha > fecha]
        movimientos_out = [ m.descripcion for m in self.lista_movimientos if m.fecha < fecha]

        # check only account filtered appears
        resp = self.app.get('/asientos/')
        for name in movimientos_in:
            self.assertIn(name, resp.text)
        for name in movimientos_out:
            self.assertNotIn(name, resp.text)

    def test_apply_filter_fecha_final(self):
        # set the filter
        fecha = '2021-12-19'
        self.filtro.fecha_final = fecha
        self.filtro.save()

        movimientos_in = [ m.descripcion for m in self.lista_movimientos if m.fecha < fecha]
        movimientos_out = [ m.descripcion for m in self.lista_movimientos if m.fecha > fecha]

        # check only account filtered appears
        resp = self.app.get('/asientos/')
        for name in movimientos_in:
            self.assertIn(name, resp.text)
        for name in movimientos_out:
            self.assertNotIn(name, resp.text)

    def test_apply_filter_descripcion(self):
        # set the filter
        descripcion = 'Calcetines'
        self.filtro.descripcion = descripcion
        self.filtro.save()

        movimientos_in = [ m.descripcion for m in self.lista_movimientos if descripcion in m.descripcion]
        movimientos_out = [ m.descripcion for m in self.lista_movimientos if descripcion not in m.descripcion]

        # check only account filtered appears
        resp = self.app.get('/asientos/')
        for name in movimientos_in:
            self.assertIn(name, resp.text)
        for name in movimientos_out:
            self.assertNotIn(name, resp.text)

    def test_apply_filter_cuenta(self):
        # set the filter
        cuenta = '110'  # Tarjeta visa
        self.filtro.cuenta = cuenta
        self.filtro.save()

        movimientos_in = [ m.descripcion for m in self.lista_movimientos if m.cuenta == cuenta]
        movimientos_out = [ m.descripcion for m in self.lista_movimientos if m.cuenta == cuenta]

        # check only account filtered appears
        resp = self.app.get('/asientos/')
        for name in movimientos_in:
            self.assertIn(name, resp.text)
        for name in movimientos_out:
            self.assertNotIn(name, resp.text)

    def test_apply_filter_asiento(self):
        # set the filter
        asiento = '2'  # Tarjeta visa
        self.filtro.cuenta = asiento
        self.filtro.save()

        movimientos_in = [ m.descripcion for m in self.lista_movimientos if m.num == asiento]
        movimientos_out = [ m.descripcion for m in self.lista_movimientos if m.num == asiento]

        # check only account filtered appears
        resp = self.app.get('/asientos/')
        for name in movimientos_in:
            self.assertIn(name, resp.text)
        for name in movimientos_out:
            self.assertNotIn(name, resp.text)


class BorrarFiltroCuentasTest(WebTest):
    def setUp(self):
        # Create filter with default values (all blanks)
        self.filtro = FiltroCuentas.objects.create(num='100', nombre='Caja')

    def test_borrar_filtro_by_url(self):
        resp = self.client.get('/cuentas/borrar/filtro/', follow=True)
        self.assertEqual(len(resp.redirect_chain), 1)
        page_redirected = resp.redirect_chain[0][0]
        self.assertEqual(page_redirected, '/cuentas/')

        filtro = FiltroCuentas.objects.all()[0]
        self.assertEqual(filtro.num, '')
        self.assertEqual(filtro.nombre, '')

    def test_borrar_filtro_by_name(self):
        resp = self.client.get(reverse('main:borrar_filtro_cuentas'), follow=True)
        self.assertEqual(len(resp.redirect_chain), 1)
        page_redirected = resp.redirect_chain[0][0]
        self.assertEqual(page_redirected, '/cuentas/')

        filtro = FiltroCuentas.objects.all()[0]
        self.assertEqual(filtro.num, '')
        self.assertEqual(filtro.nombre, '')

    def test_borrar_filtro_by_button(self):
        resp = self.app.get('/cuentas/')
        resp.click(linkid='button_clear')

        filtro = FiltroCuentas.objects.all()[0]
        self.assertEqual(filtro.num, '')
        self.assertEqual(filtro.nombre, '')


class BorrarFiltroAsientosTest(WebTest):
    def setUp(self):
        self.filtro = FiltroMovimientos.objects.create(
            fecha_inicial = '2021-12-01',
            fecha_final = '2021-12-15',
            descripcion = 'descripcion palabras',
            cuenta = '100',
            asiento = '2',
            )

    def test_borrar_filtro_by_url(self):
        resp = self.client.get('/asientos/borrar/filtro/', follow=True)
        self.assertEqual(len(resp.redirect_chain), 1)
        page_redirected = resp.redirect_chain[0][0]
        self.assertEqual(page_redirected, '/asientos/')
        self.validate_filtro()

    def test_borrar_filtro_by_name(self):
        resp = self.client.get(reverse('main:borrar_filtro_asientos'), follow=True)
        self.assertEqual(len(resp.redirect_chain), 1)
        page_redirected = resp.redirect_chain[0][0]
        self.assertEqual(page_redirected, '/asientos/')
        self.validate_filtro()

    def test_borrar_filtro_by_button(self):
        resp = self.app.get('/asientos/')
        resp.click(linkid='button_clear')
        self.validate_filtro()

    def validate_filtro(self):
        """Validate that saved filter is blank"""
        filtro = FiltroMovimientos.objects.all()[0]
        self.assertEqual(filtro.fecha_inicial, '')
        self.assertEqual(filtro.fecha_final, '')
        self.assertEqual(filtro.descripcion, '')
        self.assertEqual(filtro.cuenta, '')
        self.assertEqual(filtro.asiento, '')
