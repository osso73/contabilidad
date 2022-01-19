from webtest import Upload

from fixtures_views import *


class TestCargarAsientos():
    @pytest.fixture
    def form_cargar_movimientos(self, django_app):
        resp = django_app.get(reverse('main:asientos'))
        return resp.forms['cargar_fichero']

    @pytest.mark.parametrize('page', ['/asientos/cargar/', reverse('main:cargar_asientos')])
    def test_redirect_get_requests(self, page, client):
        resp = client.get(page, follow=True)
        assert len(resp.redirect_chain) == 1
        page_redirected = resp.redirect_chain[0][0]
        assert page_redirected == '/asientos/'

    def test_load_file_form_attributes(self, form_cargar_movimientos):
        form = form_cargar_movimientos

        assert form.id == 'cargar_fichero'
        assert form.method == 'post'
        assert form.action == '/asientos/cargar/'
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
