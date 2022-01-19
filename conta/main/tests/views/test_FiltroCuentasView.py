from main.models import FiltroCuentas

from fixtures_views import *


class TestFiltroCuentasView():
    @pytest.fixture
    def create_filter(self):
        # Create filter with default values (all blanks)
        return FiltroCuentas.objects.create()

    @pytest.fixture
    def create_and_populate_filter(self):
        return FiltroCuentas.objects.create(num='100', nombre='Tarjeta', etiqueta='gastos')

    @pytest.fixture
    def form_filtro_cuentas(self, django_app):
        resp = django_app.get(reverse('main:cuentas'))
        return resp.forms['filtro']

    @pytest.mark.parametrize('page', ['/cuentas/filtro/', reverse('main:filtro_cuentas')])
    def test_redirect_get_requests(self, page, client):
        resp = client.get(page, follow=True)
        assert len(resp.redirect_chain) == 1
        page_redirected = resp.redirect_chain[0][0]
        assert page_redirected == '/cuentas/'

    def test_load_file_form_attributes(self, form_filtro_cuentas):
        form = form_filtro_cuentas

        assert form.id == 'filtro'
        assert form.method == 'post'
        assert form.action == '/cuentas/filtro/'
        assert form.action == reverse('main:filtro_cuentas')

        fields = form.fields.keys()
        for f in ['f_num', 'f_nombre']:
            assert f in fields

    def test_filter_form_fill(self, form_filtro_cuentas):
        form = form_filtro_cuentas
        form['f_num'] = '100'
        form['f_nombre'] = 'Pago'
        resp = form.submit('accion_filtro', value='aplicar')
        filtro = FiltroCuentas.objects.all()[0]
        assert filtro.num == '100'
        assert filtro.nombre == 'Pago'

    def test_apply_filter_num(self, populate_database_cuentas, create_filter, django_app):
        filtro = create_filter
        _, cuentas = populate_database_cuentas

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
        _, cuentas = populate_database_cuentas

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

    def test_borrar_filtro_by_button(self, create_and_populate_filter, form_filtro_cuentas):
        create_and_populate_filter
        form = form_filtro_cuentas
        resp = form.submit('accion_filtro', value='borrar')

        filtro = FiltroCuentas.objects.all()[0]
        assert filtro.num == ''
        assert filtro.nombre == ''
        assert filtro.etiqueta == ''
