from webtest import Upload

from fixtures_views import *


class TestCargarCuentas():
    @pytest.fixture
    def form_cargar_cuentas(self, django_app):
        resp = django_app.get(reverse('main:cuentas'))
        return resp.forms['cargar_fichero']

    @pytest.mark.parametrize('page', ['/cuentas/cargar/', reverse('main:cargar_cuentas')])
    def test_redirect_get_requests(self, page, client):
        resp = client.get(page, follow=True)
        assert len(resp.redirect_chain) == 1
        page_redirected = resp.redirect_chain[0][0]
        assert page_redirected == '/cuentas/'

    def test_load_file_form_attributes(self, form_cargar_cuentas):
        form = form_cargar_cuentas

        assert form.id == 'cargar_fichero'
        assert form.method == 'post'
        assert form.action == '/cuentas/cargar/'
        assert form.action == reverse('main:cargar_cuentas')

        fields = form.fields.keys()
        for f in ['sobreescribir', 'file']:
            assert f in fields

    def test_load_file_not_sobreescribir(self, form_cargar_cuentas, populate_database_etiquetas):
        populate_database_etiquetas
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

    def test_load_file_sobreescribir(self, form_cargar_cuentas, populate_database_etiquetas):
        populate_database_etiquetas
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
