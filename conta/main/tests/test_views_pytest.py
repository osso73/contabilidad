import datetime

from django.urls import reverse
from django_webtest import WebTest
from webtest import Upload
import pytest
from pytest_django.asserts import assertTemplateUsed

from main.models import Cuenta, Movimiento, FiltroCuentas, FiltroMovimientos


# give access to the database
pytestmark = pytest.mark.django_db

# common fixtures, used by several tests
@pytest.fixture
def populate_database_cuentas():
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
    lista_cuentas = list()
    for num, nombre in cuentas.items():
        c = Cuenta.objects.create(num=num, nombre=nombre)
        lista_cuentas.append(c)
    return lista_cuentas


@pytest.fixture
def populate_database(populate_database_cuentas):
    cuentas = populate_database_cuentas
    movimientos = list()
    m = Movimiento.objects.create(num=1, fecha="2021-12-28",
        descripcion="Compra del pan", debe=2.50, haber=0, cuenta=cuentas[0])
    movimientos.append(m)
    m = Movimiento.objects.create(num=1, fecha="2021-12-28",
        descripcion="Compra del pan", debe=0, haber=2.50, cuenta=cuentas[3])
    movimientos.append(m)
    m = Movimiento.objects.create(num=2, fecha="2021-12-15",
        descripcion="Compra de fruta", debe=10.75, haber=0, cuenta=cuentas[0])
    movimientos.append(m)
    m = Movimiento.objects.create(num=2, fecha="2021-12-15",
        descripcion="Compra de fruta", debe=0, haber=10.75, cuenta=cuentas[3])
    movimientos.append(m)
    m = Movimiento.objects.create(num=3, fecha="2021-12-18",
        descripcion="Calcetines y calzoncillos", debe=15.85, haber=0, cuenta=cuentas[1])
    movimientos.append(m)
    m = Movimiento.objects.create(num=3, fecha="2021-12-18",
        descripcion="Calcetines y calzoncillos", debe=0, haber=15.85, cuenta=cuentas[3])
    movimientos.append(m)
    m = Movimiento.objects.create(num=4, fecha="2021-12-20",
        descripcion="Abrigo de invierno", debe=54, haber=0, cuenta=cuentas[1])
    movimientos.append(m)
    m = Movimiento.objects.create(num=4, fecha="2021-12-20",
        descripcion="Abrigo de invierno", debe=0, haber=54, cuenta=cuentas[3])
    movimientos.append(m)

    return cuentas, movimientos


class TestIndexView():
    @pytest.mark.parametrize('page', ['/', reverse('main:index')])
    def test_view_url_exists_at_desired_location(self, page, django_app):
        resp = django_app.get(page)
        assert resp.status_code == 200

    @pytest.mark.parametrize('page', ['/', reverse('main:index')])
    def test_view_uses_correct_template(self, page, django_app):
        resp = django_app.get(page)
        assertTemplateUsed(resp, 'main/index.html')


class TestCuentasView():
    @pytest.fixture
    def form_crear_cuenta(self, django_app):
        resp = django_app.get(reverse('main:cuentas'))
        return resp.forms['crear_cuenta']

    @pytest.mark.parametrize('page', ['/cuentas/', reverse('main:cuentas')])
    def test_view_url_exists_at_desired_location(self, page, django_app):
        resp = django_app.get(page)
        assert resp.status_code == 200

    @pytest.mark.parametrize('page', ['/cuentas/', reverse('main:cuentas')])
    def test_view_uses_correct_template_oriol(self, page, django_app):
        resp = django_app.get(page)
        assertTemplateUsed(resp, 'main/cuentas.html')


    def test_list_of_cuentas_oriol(self, django_app, populate_database_cuentas):
        lista_cuentas = populate_database_cuentas
        resp = django_app.get(reverse('main:cuentas'))
        for cuenta in lista_cuentas:
            assert cuenta.num in resp
            assert cuenta.nombre in resp

    def test_create_new_cuenta_form_attributes(self, form_crear_cuenta):
        form = form_crear_cuenta

        assert form.id == 'crear_cuenta'
        assert form.method == 'post'
        assert form.action == '/cuentas/'
        assert form.action == reverse('main:cuentas')

        fields = form.fields.keys()
        for f in ['num', 'nombre']:
            assert f in fields

    def test_create_new_cuenta(self, form_crear_cuenta):
        form = form_crear_cuenta

        form['num'] = '100'
        form['nombre'] = 'Caja'
        form.submit()

        # check that account exists in the database
        cuentas = Cuenta.objects.all()
        assert len(cuentas) == 1
        assert cuentas[0].num == '100'
        assert cuentas[0].nombre == 'Caja'


class TestAsientosView():
    @pytest.mark.parametrize('page', ['/asientos/', reverse('main:asientos')])
    def test_view_url_exists_at_desired_location(self, page, django_app):
        resp = django_app.get(page)
        assert resp.status_code == 200

    @pytest.mark.parametrize('page', ['/asientos/', reverse('main:asientos')])
    def test_view_uses_correct_template_oriol(self, page, django_app):
        resp = django_app.get(page)
        assertTemplateUsed(resp, 'main/asientos.html')

    def test_list_of_movimientos(self, populate_database, django_app):
        resp = django_app.get(reverse('main:asientos'))
        cuentas, movimientos = populate_database
        for mov in movimientos:
            assert mov.descripcion in resp

    def test_add_simple_asiento_form_attributes(self, django_app):
        resp = django_app.get(reverse('main:asientos'))
        form = resp.forms['crear_asiento']

        assert form.id == 'crear_asiento'
        assert form.method == 'post'
        assert form.action == '/asientos/'
        assert form.action == reverse('main:asientos')

        fields = form.fields.keys()
        for f in ['fecha', 'descripcion', 'valor', 'debe', 'haber']:
            assert f in fields


    def test_add_simple_asiento(self, django_app, populate_database_cuentas):
        cuentas = populate_database_cuentas
        resp = django_app.get(reverse('main:asientos'))
        form = resp.forms['crear_asiento']

        # fill the form
        form['fecha'] = '2021-12-28'
        form['descripcion'] = 'Compras en el super'
        form['valor'] = '34'
        form['debe'] = '100'
        form['haber'] = '300'
        form.submit()

        # check movimientos are created in the database
        movimientos = Movimiento.objects.all()
        assert len(movimientos) == 2
        assert movimientos[0].num == 1
        assert movimientos[0].fecha == datetime.date(2021, 12, 28)
        assert movimientos[0].descripcion == 'Compras en el super'
        assert movimientos[0].debe == 34
        assert movimientos[0].haber == 0
        assert movimientos[0].cuenta.num == '100'
        assert movimientos[0].cuenta.nombre == 'Caja'

        assert movimientos[1].num == 1
        assert movimientos[1].fecha == datetime.date(2021, 12, 28)
        assert movimientos[1].descripcion == 'Compras en el super'
        assert movimientos[1].debe == 0
        assert movimientos[1].haber == 34
        assert movimientos[1].cuenta.num == '300'
        assert movimientos[1].cuenta.nombre == 'Comida'


class TestModificarAsientoView():
    @pytest.fixture
    def form_modificar_asiento(self, django_app):
        resp = django_app.get(reverse('main:modificar_asiento', args=[1]))
        return resp.forms['formulario']

    @pytest.mark.parametrize('page', ['/modificar/asiento/1/', reverse('main:modificar_asiento', args=[1])])
    def test_view_url_exists_at_desired_location(self, page, django_app, populate_database):
        populate_database
        resp = django_app.get(page)
        assert resp.status_code == 200

    @pytest.mark.parametrize('page', ['/modificar/asiento/1/', reverse('main:modificar_asiento', args=[1])])
    def test_view_uses_correct_template_oriol(self, page, django_app, populate_database):
        populate_database
        resp = django_app.get(page)
        assertTemplateUsed(resp, 'main/modificar_asiento.html')

    def test_form_attributes(self, populate_database, form_modificar_asiento):
        populate_database
        form = form_modificar_asiento

        assert form.id == 'formulario'
        assert form.method == 'post'
        assert form.action == '/modificar/asiento/1/'
        assert form.action == reverse('main:modificar_asiento', args=[1])

        fields = form.fields.keys()
        for f in ['id0', 'num0', 'fecha0', 'descripcion0', 'debe0', 'haber0', 'cuenta0']:
            assert f in fields

    def test_modify_asiento(self, populate_database, form_modificar_asiento):
        populate_database
        form = form_modificar_asiento
        form['num0'] = '115'
        form.submit()

        movimiento = Movimiento.objects.all()[0]
        assert movimiento.num == 115


    def test_modify_fecha(self, populate_database, form_modificar_asiento):
        populate_database
        form = form_modificar_asiento
        form['fecha0'] = '2021-12-31'
        form.submit()

        movimiento = Movimiento.objects.all()[0]
        assert movimiento.fecha == datetime.date(2021, 12, 31)

    def test_modify_descripcion(self, populate_database, form_modificar_asiento):
        populate_database
        form = form_modificar_asiento
        form['descripcion0'] = 'Nueva descripcion'
        form.submit()

        movimiento = Movimiento.objects.all()[0]
        assert movimiento.descripcion == 'Nueva descripcion'

    def test_modify_debe(self, populate_database, form_modificar_asiento):
        populate_database
        form = form_modificar_asiento
        form['debe0'] = '243.87'
        form.submit()

        movimiento = Movimiento.objects.all()[0]
        assert float(movimiento.debe) == 243.87

    def test_modify_haber(self, populate_database, form_modificar_asiento):
        populate_database
        form = form_modificar_asiento
        form['haber0'] = '521.67'
        form.submit()

        movimiento = Movimiento.objects.all()[0]
        assert float(movimiento.haber) == 521.67

    def test_modify_cuenta(self, populate_database, form_modificar_asiento):
        Cuenta.objects.create(num='999', nombre='Tarjeta visa probando')
        populate_database
        form = form_modificar_asiento
        form['cuenta0'] = '999'
        form.submit()

        movimiento = Movimiento.objects.all()[0]
        assert movimiento.cuenta.num == '999'
        assert movimiento.cuenta.nombre == 'Tarjeta visa probando'

    def test_add_movimiento(self, django_app, populate_database, form_modificar_asiento):
        resp = django_app.get(reverse('main:modificar_asiento', args=[1]))
        resp.click(linkid='anadir_movimiento')

        mov = Movimiento.objects.filter(num=1)
        assert len(mov) == 3
        assert mov[2].num == 1
        assert mov[2].fecha == datetime.date(2021, 12, 28)
        assert mov[2].descripcion == ''
        assert float(mov[2].debe) == 0.0
        assert float(mov[2].haber) == 0.0
        assert mov[2].cuenta.num == '100'


class TestModificarCuentaView():
    @pytest.mark.parametrize('page', ['/modificar/cuenta/100/', reverse('main:modificar_cuenta', args=[100])])
    def test_view_url_exists_at_desired_location(self, page, django_app, populate_database_cuentas):
        populate_database_cuentas
        resp = django_app.get(page)
        assert resp.status_code == 200

    @pytest.mark.parametrize('page', ['/modificar/cuenta/100/', reverse('main:modificar_cuenta', args=[100])])
    def test_view_uses_correct_template(self, page, django_app, populate_database_cuentas):
        populate_database_cuentas
        resp = django_app.get(page)
        assertTemplateUsed(resp, 'main/modificar_cuenta.html')

    def test_form_attributes(self, django_app, populate_database_cuentas):
        populate_database_cuentas
        resp = django_app.get(reverse('main:modificar_cuenta', args=[100]))
        form = resp.forms['formulario']

        assert form.id == 'formulario'
        assert form.method == 'post'
        assert form.action == '/modificar/cuenta/100/'
        assert form.action == reverse('main:modificar_cuenta', args=[100])

        fields = form.fields.keys()
        for f in ['num', 'nombre']:
            assert f in fields

    def test_modify_nombre(self, django_app, populate_database_cuentas):
        populate_database_cuentas
        resp = django_app.get(reverse('main:modificar_cuenta', args=[100]))
        form = resp.forms['formulario']
        form['nombre'] = 'Tarjeta visa'
        form.submit()

        cuenta = Cuenta.objects.get(pk=100)
        assert cuenta.nombre == 'Tarjeta visa'


class TestBorrarMovimientoView():
    def test_view_deletes_movimiento_redirect_to_asientos_by_url(self, django_app, populate_database):
        populate_database
        movimientos = Movimiento.objects.all()
        assert len(movimientos) > 0

        for mov in movimientos:
            django_app.get(f'/borrar/movimiento/{mov.pk}/asientos/')

        movimientos = Movimiento.objects.all()
        assert len(movimientos) == 0

    def test_view_deletes_movimiento_redirect_to_asientos_by_name(self, django_app, populate_database):
        populate_database
        movimientos = Movimiento.objects.all()
        assert len(movimientos) > 0

        for mov in movimientos:
            django_app.get(reverse('main:borrar_movimiento', args=[mov.pk, 'asientos']))

        movimientos = Movimiento.objects.all()
        assert len(movimientos) == 0

    def test_view_redirect_simple(self, client, populate_database):
        cuentas, movimientos = populate_database
        pk = movimientos[0].pk
        resp = client.get(reverse('main:borrar_movimiento',
            args=[pk, 'asientos']), follow=True)

        assert len(resp.redirect_chain) == 1
        page_redirected = resp.redirect_chain[0][0]
        assert page_redirected == '/asientos/'

    def test_view_deletes_movimiento_redirect_to_modificar_asientos_by_url(self, django_app, populate_database):
        populate_database
        movimientos = Movimiento.objects.all()
        num_inicial = len(movimientos)
        assert num_inicial > 0

        # delete one movimiento from the asiento 1
        url = f'/borrar/movimiento/{movimientos[0].pk}/modificar_asiento/{movimientos[0].num}/'
        django_app.get(url)

        movimientos = Movimiento.objects.all()
        num_final = len(movimientos)
        assert num_final == num_inicial - 1

    def test_view_deletes_movimiento_redirect_to_modificar_asientos_by_name(self, django_app, populate_database):
        populate_database
        movimientos = Movimiento.objects.all()
        num_inicial = len(movimientos)
        assert num_inicial > 0

        # delete one movimiento from the asiento 1
        url = reverse('main:borrar_movimiento_complejo', args=[movimientos[0].pk, 'modificar_asiento', movimientos[0].num])
        django_app.get(url)

        movimientos = Movimiento.objects.all()
        num_final = len(movimientos)
        assert num_final == num_inicial - 1

    def test_view_redirect_complex(self, client, populate_database):
        cuentas, movimientos = populate_database
        url = reverse('main:borrar_movimiento_complejo', args=[movimientos[0].pk, 'modificar_asiento', movimientos[0].num])
        resp = client.get(url, follow=True)
        assert len(resp.redirect_chain) == 1
        page_redirected = resp.redirect_chain[0][0]
        assert page_redirected == '/modificar/asiento/1/'


class TestAnadirMovimientoView():
    @pytest.mark.parametrize('page', ['/anadir/movimiento/1/2021-12-28/',
        reverse('main:anadir_movimiento', args=[1, '2021-12-28'])])
    def test_view_url_exists_at_desired_location(self, page, django_app, populate_database):
        populate_database
        resp = django_app.get(page)
        assert resp.status_code == 302  # expect a redirect

    def test_view_url_creates_new_movimiento(self, django_app, populate_database):
        cuentas, movimientos = populate_database
        num_inicial = len(movimientos)
        resp = django_app.get(reverse('main:anadir_movimiento', args=[1, '2021-12-28']))
        movimientos = Movimiento.objects.all()
        num_final = len(movimientos)
        assert num_final == num_inicial + 1
        last = movimientos[num_final-1]
        assert last.fecha == datetime.date(2021, 12, 28)

    def test_view_redirect(self, client, populate_database):
        """test that view is redirected to the right page"""
        populate_database
        url = reverse('main:anadir_movimiento', args=[1, '2021-12-28'])
        resp = client.get(url, follow=True)
        assert len(resp.redirect_chain) == 1
        page_redirected = resp.redirect_chain[0][0]
        assert page_redirected == '/modificar/asiento/1/'

    def test_add_movimiento(self, django_app, populate_database):
        cuentas, movimientos = populate_database
        num_inicial = len(movimientos)
        resp = django_app.get(reverse('main:anadir_movimiento', args=[1, '2021-12-28']))

        movimientos = Movimiento.objects.all()
        num_final = len(movimientos)
        assert num_final == num_inicial + 1

        mov = movimientos[num_final-1]  # get the last movimiento that has been just added

        assert mov.num == 1
        assert mov.fecha == datetime.date(2021, 12, 28)
        assert mov.descripcion ==''
        assert float(mov.debe) == 0.0
        assert float(mov.haber) == 0.0
        assert mov.cuenta.num == '100'


class TestBorrarCuentaView():
    def test_view_deletes_movimiento_redirect_to_asientos_by_url(self, django_app, populate_database_cuentas):
        cuentas = populate_database_cuentas
        assert len(cuentas) > 0

        for c in cuentas:
            django_app.get(f'/borrar/cuenta/{c.pk}/')

        cuentas = Cuenta.objects.all()
        assert len(cuentas) == 0

    def test_view_deletes_movimiento_redirect_to_asientos_by_name(self, django_app, populate_database_cuentas):
        cuentas = populate_database_cuentas
        assert len(cuentas) > 0

        for c in cuentas:
            django_app.get(reverse('main:borrar_cuenta', args=[c.pk]))

        cuentas = Cuenta.objects.all()
        assert len(cuentas) == 0

    def test_view_redirect(self, client, populate_database_cuentas):
        cuentas = populate_database_cuentas
        url = reverse('main:borrar_cuenta', args=[cuentas[0].pk])
        resp = client.get(url, follow=True)
        assert len(resp.redirect_chain) == 1
        page_redirected = resp.redirect_chain[0][0]
        assert page_redirected == '/cuentas/'

    def test_dont_delete_if_account_has_movements(self, django_app, populate_database):
        cuentas, movimientos = populate_database
        num_cuenta = movimientos[0].cuenta.num
        django_app.get(reverse('main:borrar_cuenta', args=[num_cuenta]))
        cuenta = Cuenta.objects.filter(num=num_cuenta)
        assert len(cuenta) == 1


class TestCargarCuentas():
    @pytest.fixture
    def form_cargar_cuentas(self, django_app):
        resp = django_app.get(reverse('main:cuentas'))
        return resp.forms['cargar_fichero']

    @pytest.mark.parametrize('page', ['/cargar/cuentas/', reverse('main:cargar_cuentas')])
    def test_redirect_get_requests(self, page, client):
        resp = client.get(page, follow=True)
        assert len(resp.redirect_chain) == 1
        page_redirected = resp.redirect_chain[0][0]
        assert page_redirected == '/cuentas/'

    def test_load_file_form_attributes(self, form_cargar_cuentas):
        form = form_cargar_cuentas

        assert form.id == 'cargar_fichero'
        assert form.method == 'post'
        assert form.action == '/cargar/cuentas/'
        assert form.action == reverse('main:cargar_cuentas')

        fields = form.fields.keys()
        for f in ['sobreescribir', 'file']:
            assert f in fields

    def test_load_file(self, form_cargar_cuentas):
        # before loading, we have 0 cuentas
        cuentas = Cuenta.objects.all()
        assert len(cuentas) == 0

        form = form_cargar_cuentas
        form['file'] = Upload('main/tests/data/cuentas.xlsx')
        resp = form.submit()

        cuentas = [ c.num for c in Cuenta.objects.all() ]
        assert len(cuentas) > 0
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
            assert c in cuentas
            assert c in resp

    def test_load_file_sobreescribir(self, form_cargar_cuentas):
        Cuenta.objects.create(num='100', nombre='Dinero')
        form = form_cargar_cuentas
        form['file'] = Upload('main/tests/data/cuentas.xlsx')
        form['sobreescribir'] = False
        resp = form.submit()

        cuentas = [ c.nombre for c in Cuenta.objects.all() ]
        assert 'Caja' not in cuentas
        assert 'Dinero' in cuentas

        form['file'] = Upload('main/tests/data/cuentas.xlsx')
        form['sobreescribir'] = True
        resp = form.submit()

        cuentas = [ c.nombre for c in Cuenta.objects.all() ]
        assert 'Caja' in cuentas
        assert 'Dinero' not in cuentas

    def test_load_file_error(self, form_cargar_cuentas):
        """Load an incorrect file, it should show no cuentas loaded"""
        form = form_cargar_cuentas
        form['file'] = Upload('main/tests/data/empty_file.xlsx')
        resp = form.submit()

        cuentas = Cuenta.objects.all()
        assert len(cuentas) == 0


class TestCargarAsientos():
    @pytest.fixture
    def form_cargar_movimientos(self, django_app):
        resp = django_app.get(reverse('main:asientos'))
        return resp.forms['cargar_fichero']

    @pytest.mark.parametrize('page', ['/cargar/asientos/', reverse('main:cargar_asientos')])
    def test_redirect_get_requests(self, page, client):
        resp = client.get(page, follow=True)
        assert len(resp.redirect_chain) == 1
        page_redirected = resp.redirect_chain[0][0]
        assert page_redirected == '/asientos/'

    def test_load_file_form_attributes(self, form_cargar_movimientos):
        form = form_cargar_movimientos

        assert form.id == 'cargar_fichero'
        assert form.method == 'post'
        assert form.action == '/cargar/asientos/'
        assert form.action == reverse('main:cargar_asientos')

        fields = form.fields.keys()
        assert 'file' in fields

    def test_load_file(self, form_cargar_movimientos, populate_database_cuentas):
        populate_database_cuentas
        # before loading, we have 0 movimientos
        movimientos = Movimiento.objects.all()
        assert len(movimientos) == 0

        form = form_cargar_movimientos
        form['file'] = Upload('main/tests/data/plantilla.xlsx')
        resp = form.submit()

        movimientos = [ c.descripcion for c in Movimiento.objects.all() ]
        assert len(movimientos) > 0
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
            assert m in movimientos
            assert m in resp

    def test_load_file_error(self, form_cargar_movimientos, populate_database_cuentas):
        populate_database_cuentas
        form = form_cargar_movimientos
        form['file'] = Upload('main/tests/data/plantilla_errores.xlsx')
        resp = form.submit()

        movimientos = [ c.descripcion for c in Movimiento.objects.all() ]
        movimientos_ok = [
            'Compra pan',
            'Hipoteca',
            'Cena en el restaurante',
            'Factura EDP - gas',
            'Comida - total',
            ]
        movimientos_error = [
            'Pizzas Telepizza',
            'Gasolina coche',
            'Pago IBI',
            'Factura EDP - gas y electricidad',
            'Factura EDP - electricidad',
            'Cena en el restaurante propina',
            'Comida',
            'Comida - propina',
            ]
        messages = [
            'Ha habido 8 errores.',
            'Se han cargado 8 movimientos.',
            'Fecha incorrecta',
            'Cuenta no existe',
            'Valor es incorrecto',
            'Haber es incorrecto',
            'Debe es incorrecto',
            'El número de asiento es incorrecto',
        ]

        for m in movimientos_ok:
            assert m in movimientos
            assert m in resp

        for m in movimientos_error:
            assert m not in movimientos
            assert m in resp

        for m in messages:
            assert m in resp

    def test_load_file_blank(self, form_cargar_movimientos, populate_database_cuentas):
        """Test that when uploaded file with wrong format, nothing breaks"""
        populate_database_cuentas
        form = form_cargar_movimientos
        form['file'] = Upload('main/tests/data/empty_file.xlsx')
        resp = form.submit()
        self.validate_error_file(resp)

    def test_load_file_empty(self, form_cargar_movimientos, populate_database_cuentas):
        """Test that when uploaded file with no movements, nothing breaks"""
        populate_database_cuentas
        form = form_cargar_movimientos
        form['file'] = Upload('main/tests/data/plantilla_vacia.xlsx')
        resp = form.submit()
        self.validate_error_file(resp)

    def test_load_file_non_excel(self, form_cargar_movimientos, populate_database_cuentas):
        """Test that when uploaded file with no movements, nothing breaks"""
        populate_database_cuentas
        form = form_cargar_movimientos
        form['file'] = Upload('main/tests/data/logo.svg')
        resp = form.submit()
        self.validate_error_file(resp)

    def validate_error_file(self, resp):
        movimientos = Movimiento.objects.all()
        assert len(movimientos) == 0

        msg = ['Se han cargado 0 movimientos.', 'Ha habido 0 errores.']
        for m in msg:
            assert m in resp.text


class TestFiltroCuentasView():
    @pytest.fixture
    def create_filter(self):
        # Create filter with default values (all blanks)
        return FiltroCuentas.objects.create()

    @pytest.fixture
    def form_filtro_cuentas(self, django_app):
        resp = django_app.get(reverse('main:cuentas'))
        return resp.forms['filtro']

    @pytest.mark.parametrize('page', ['/filtro/cuentas/', reverse('main:filtro_cuentas')])
    def test_redirect_get_requests(self, page, client):
        resp = client.get(page, follow=True)
        assert len(resp.redirect_chain) == 1
        page_redirected = resp.redirect_chain[0][0]
        assert page_redirected == '/cuentas/'

    def test_load_file_form_attributes(self, form_filtro_cuentas):
        form = form_filtro_cuentas

        assert form.id == 'filtro'
        assert form.method == 'post'
        assert form.action == '/filtro/cuentas/'
        assert form.action == reverse('main:filtro_cuentas')

        fields = form.fields.keys()
        for f in ['f_num', 'f_nombre']:
            assert f in fields

    def test_filter_form_fill(self, form_filtro_cuentas):
        form = form_filtro_cuentas
        form['f_num'] = '100'
        form['f_nombre'] = 'Pago'
        resp = form.submit()
        filtro = FiltroCuentas.objects.all()[0]
        assert filtro.num == '100'
        assert filtro.nombre == 'Pago'

    def test_apply_filter_num(self, populate_database_cuentas, create_filter, django_app):
        filtro = create_filter
        cuentas = populate_database_cuentas

        # set the filter
        filtro.num = '300'
        filtro.save()

        lista_cuentas = [ c.nombre for c in cuentas ]

        # check only account filtered appears
        resp = django_app.get(reverse('main:cuentas'))
        for name in lista_cuentas:
            if name == 'Comida':
                assert name in resp.text
            else:
                assert name not in resp.text

    def test_apply_filter_name(self, populate_database_cuentas, create_filter, django_app):
        filtro = create_filter
        cuentas = populate_database_cuentas

        # set the filter
        filtro.nombre = 'Tarjeta'
        filtro.save()

        lista_cuentas = [ c.nombre for c in cuentas ]

        # check only account filtered appears
        resp = django_app.get(reverse('main:cuentas'))
        for name in lista_cuentas:
            if 'Tarjeta' in name:
                assert name in resp.text
            else:
                assert name not in resp.text


class TestFiltroAsientosView():
    @pytest.fixture
    def create_filter(self):
        # Create filter with default values (all blanks)
        return FiltroMovimientos.objects.create()

    @pytest.fixture
    def form_filtro_movimientos(self, django_app):
        resp = django_app.get(reverse('main:asientos'))
        return resp.forms['filtro']

    @pytest.mark.parametrize('page', ['/filtro/asientos/', reverse('main:filtro_asientos')])
    def test_redirect_get_requests(self, page, client):
        resp = client.get(page, follow=True)
        assert len(resp.redirect_chain) == 1
        page_redirected = resp.redirect_chain[0][0]
        assert page_redirected == '/asientos/'

    def test_load_file_form_attributes(self, form_filtro_movimientos):
        form = form_filtro_movimientos

        assert form.id == 'filtro'
        assert form.method == 'post'
        assert form.action == '/filtro/asientos/'
        assert form.action == reverse('main:filtro_asientos')

        fields = form.fields.keys()
        for f in ['f_fecha_inicial', 'f_fecha_final', 'f_descripcion',
            'f_cuenta', 'f_asiento']:
            assert f in fields

    def test_filter_form_fill(self, form_filtro_movimientos):
        form = form_filtro_movimientos
        form['f_fecha_inicial'] = '2021-12-01'
        form['f_fecha_final'] = '2021-12-15'
        form['f_descripcion'] = 'descripcion palabras'
        form['f_cuenta'] = '100'
        form['f_asiento'] = '2'
        resp = form.submit()

        filtro = FiltroMovimientos.objects.all()[0]
        assert filtro.fecha_inicial == '2021-12-01'
        assert filtro.fecha_final == '2021-12-15'
        assert filtro.descripcion == 'descripcion palabras'
        assert filtro.cuenta == '100'
        assert filtro.asiento == '2'

    def test_apply_filter_fecha_inicial(self, populate_database, create_filter, django_app):
        filtro = create_filter
        _, movimientos = populate_database

        # set the filter
        fecha = '2021-12-19'
        filtro.fecha_inicial = fecha
        filtro.save()

        movimientos_in = [ m.descripcion for m in movimientos if m.fecha >= fecha]
        movimientos_out = [ m.descripcion for m in movimientos if m.fecha <= fecha]

        # check only account filtered appears
        resp = django_app.get(reverse('main:asientos'))
        for name in movimientos_in:
            assert name in resp.text
        for name in movimientos_out:
            assert name not in resp.text

    def test_apply_filter_fecha_final(self, populate_database, create_filter, django_app):
        filtro = create_filter
        _, movimientos = populate_database

        # set the filter
        fecha = '2021-12-19'
        filtro.fecha_final = fecha
        filtro.save()

        movimientos_in = [ m.descripcion for m in movimientos if m.fecha <= fecha]
        movimientos_out = [ m.descripcion for m in movimientos if m.fecha >= fecha]

        # check only account filtered appears
        resp = django_app.get(reverse('main:asientos'))
        for name in movimientos_in:
            assert name in resp.text
        for name in movimientos_out:
            assert name not in resp.text

    def test_apply_filter_descripcion(self, populate_database, create_filter, django_app):
        filtro = create_filter
        _, movimientos = populate_database

        # set the filter
        descripcion = 'Calcetines'
        filtro.descripcion = descripcion
        filtro.save()

        movimientos_in = [ m.descripcion for m in movimientos if descripcion in m.descripcion]
        movimientos_out = [ m.descripcion for m in movimientos if descripcion not in m.descripcion]

        # check only account filtered appears
        resp = django_app.get(reverse('main:asientos'))
        for name in movimientos_in:
            assert name in resp.text
        for name in movimientos_out:
            assert name not in resp.text

    def test_apply_filter_cuenta(self, populate_database, create_filter, django_app):
        filtro = create_filter
        cuentas, movimientos = populate_database

        # set the filter
        cuenta = '100'  # Caja
        filtro.cuenta = cuenta
        filtro.save()

        movimientos_in = [ m.descripcion for m in movimientos if m.cuenta.num == cuenta]
        movimientos_out = [ m.descripcion for m in movimientos if m.cuenta.num != cuenta]

        # check only account filtered appears
        resp = django_app.get(reverse('main:asientos'))
        for name in movimientos_in:
            assert name in resp.text

    def test_apply_filter_asiento(self, populate_database, create_filter, django_app):
        filtro = create_filter
        cuentas, movimientos = populate_database

        # set the filter
        asiento = '2'
        filtro.asiento = asiento
        filtro.save()

        movimientos_in = [ m.descripcion for m in movimientos if m.num == int(asiento)]
        movimientos_out = [ m.descripcion for m in movimientos if m.num != int(asiento)]

        # check only account filtered appears
        resp = django_app.get(reverse('main:asientos'))
        for name in movimientos_in:
            assert name in resp.text
        for name in movimientos_out:
            assert name not in resp.text


class TestBorrarFiltroCuentas():
    @pytest.fixture
    def create_and_populate_filter(self):
        return FiltroCuentas.objects.create(num='100', nombre='Tarjeta')

    @pytest.mark.parametrize('page', ['/cuentas/borrar/filtro/',
        reverse('main:borrar_filtro_cuentas')])
    def test_redirect_page_(self, page, client, create_and_populate_filter):
        create_and_populate_filter
        resp = client.get(page, follow=True)
        assert len(resp.redirect_chain) == 1
        page_redirected = resp.redirect_chain[0][0]
        assert page_redirected == '/cuentas/'


    @pytest.mark.parametrize('page', ['/cuentas/borrar/filtro/',
        reverse('main:borrar_filtro_cuentas')])
    def test_borrar_filtro_by_url(self, page, django_app, create_and_populate_filter):
        create_and_populate_filter
        django_app.get(page)

        filtro = FiltroCuentas.objects.all()[0]
        assert filtro.num == ''
        assert filtro.nombre == ''

    def test_borrar_filtro_by_button(self, django_app, create_and_populate_filter):
        create_and_populate_filter
        resp = django_app.get(reverse('main:cuentas'))
        resp.click(linkid='button_clear')

        filtro = FiltroCuentas.objects.all()[0]
        assert filtro.num == ''
        assert filtro.nombre == ''


class TestBorrarFiltroAsientos():
    @pytest.fixture
    def create_and_populate_filter(self):
        f = FiltroMovimientos.objects.create(
            fecha_inicial = '2021-12-01',
            fecha_final = '2021-12-15',
            descripcion = 'descripcion palabras',
            cuenta = '100',
            asiento = '2',
            )
        return f

    @pytest.mark.parametrize('page', ['/asientos/borrar/filtro/',
        reverse('main:borrar_filtro_asientos')])
    def test_redirect_page(self, page, client, create_and_populate_filter):
        create_and_populate_filter
        resp = client.get(page, follow=True)
        assert len(resp.redirect_chain) == 1
        page_redirected = resp.redirect_chain[0][0]
        assert page_redirected == '/asientos/'

    @pytest.mark.parametrize('page', ['/asientos/borrar/filtro/',
        reverse('main:borrar_filtro_asientos')])
    def test_borrar_filtro_by_url(self, page, django_app, create_and_populate_filter):
        create_and_populate_filter
        django_app.get(page)
        self.validate_filtro()

    def test_borrar_filtro_by_button(self, django_app, create_and_populate_filter):
        create_and_populate_filter
        resp = django_app.get(reverse('main:asientos'))
        resp.click(linkid='button_clear')
        self.validate_filtro()

    def validate_filtro(self):
        """Validate that saved filter is blank"""
        filtro = FiltroMovimientos.objects.all()[0]
        assert filtro.fecha_inicial == ''
        assert filtro.fecha_final == ''
        assert filtro.descripcion == ''
        assert filtro.cuenta == ''
        assert filtro.asiento == ''

class TestCambiarOrden():
    @pytest.fixture
    def create_filter_cuentas(self):
        # Create filter with default values (all blanks)
        return FiltroCuentas.objects.create()

    @pytest.fixture
    def create_filter_asientos(self):
        # Create filter with default values (all blanks)
        return FiltroMovimientos.objects.create()

    @pytest.mark.parametrize('page', ['/cambiar/orden/cuentas/num/',
        reverse('main:cambiar_orden', args=['cuentas', 'num'])])
    def test_redirect_page_cuentas(self, page, client, create_filter_cuentas):
        create_filter_cuentas
        resp = client.get(page, follow=True)
        assert len(resp.redirect_chain) == 1
        page_redirected = resp.redirect_chain[0][0]
        assert page_redirected == '/cuentas/'

    @pytest.mark.parametrize('access_type', ['url', 'click'])
    @pytest.mark.parametrize('campo', ['num', 'nombre'])
    def test_cambiar_orden_cuentas(self, campo, access_type, create_filter_cuentas, django_app, populate_database_cuentas):
        populate_database_cuentas
        filtro = create_filter_cuentas
        assert filtro.campo == 'num'
        assert filtro.ascendiente == True
        if access_type == 'click':
            resp = django_app.get(reverse('main:cuentas'))
            resp.click(linkid=campo+"_titulo", verbose=True)
        else:
            django_app.get(reverse('main:cambiar_orden', args=['cuentas', campo]))
        filtro = FiltroCuentas.objects.all()[0]
        assert filtro.campo == campo
        if campo.lower() == 'num':
            assert filtro.ascendiente == False
        else:
            assert filtro.ascendiente == True

        if access_type == 'click':
            resp.click(linkid=campo+"_titulo", verbose=True)
        else:
            django_app.get(reverse('main:cambiar_orden', args=['cuentas', campo]))
        filtro = FiltroCuentas.objects.all()[0]
        assert filtro.campo == campo
        if campo.lower() == 'num':
            assert filtro.ascendiente == True
        else:
            assert filtro.ascendiente == False

    @pytest.mark.parametrize('page', ['/cambiar/orden/asientos/num/',
        reverse('main:cambiar_orden', args=['asientos', 'num'])])
    def test_redirect_page_asientos(self, page, client, create_filter_asientos):
        create_filter_asientos
        resp = client.get(page, follow=True)
        assert len(resp.redirect_chain) == 1
        page_redirected = resp.redirect_chain[0][0]
        assert page_redirected == '/asientos/'

    @pytest.mark.parametrize('access_type', ['url', 'click'])
    @pytest.mark.parametrize('campo', ['num', 'fecha', 'descripcion', 'debe', 'haber', 'cuenta'])
    def test_cambiar_orden_asientos(self, campo, access_type, create_filter_asientos, django_app, populate_database):
        populate_database
        filtro = create_filter_asientos
        assert filtro.campo == 'num'
        assert filtro.ascendiente == True
        if access_type == 'click':
            resp = django_app.get(reverse('main:asientos'))
            resp.click(linkid=campo+"_titulo", verbose=True)
        else:
            django_app.get(reverse('main:cambiar_orden', args=['asientos', campo]))
        filtro = FiltroMovimientos.objects.all()[0]
        assert filtro.campo == campo
        if campo.lower() == 'num':
            assert filtro.ascendiente == False
        else:
            assert filtro.ascendiente == True

        if access_type == 'click':
            resp.click(linkid=campo+"_titulo", verbose=True)
        else:
            django_app.get(reverse('main:cambiar_orden', args=['asientos', campo]))
        filtro = FiltroMovimientos.objects.all()[0]
        assert filtro.campo == campo
        if campo.lower() == 'num':
            assert filtro.ascendiente == True
        else:
            assert filtro.ascendiente == False

    @pytest.mark.parametrize('page', ['/cambiar/orden/wrong/num/',
        reverse('main:cambiar_orden', args=['wrong', 'num'])])
    def test_redirect_page_wrong(self, page, client, create_filter_cuentas, create_filter_asientos):
        create_filter_cuentas
        create_filter_asientos
        resp = client.get(page, follow=True)
        assert len(resp.redirect_chain) == 1
        page_redirected = resp.redirect_chain[0][0]
        assert page_redirected == '/'

    def test_validate_order(self):
        pass
