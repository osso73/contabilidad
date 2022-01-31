from main.models import FiltroCuentas

from fixtures_views import *


class TestFiltroCuentas():
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
        assert page_redirected == reverse('main:cuentas')

    def test_load_file_form_attributes(self, form_filtro_cuentas):
        form = form_filtro_cuentas

        assert form.id == 'filtro'
        assert form.method == 'post'
        assert form.action == '/cuentas/filtro/'
        assert form.action == reverse('main:filtro_cuentas')

        fields = form.fields.keys()
        for f in ['f_num', 'f_nombre', 'f_etiqueta']:
            assert f in fields

    @pytest.mark.parametrize('test_num, test_nombre, test_etiqueta', [
        ('100', 'Caja', 'balance'),
        ('101', 'Tickets restaurant', 'balance'),
        ('1101', 'Cuenta nómina', 'balance'),
        ('1110', 'Cuenta ahorro', 'balance'),
        ('1200', 'Tarjeta Visa', 'balance'),
        ('1201', 'Tarjeta Amex', 'balance'),
        ('1210', 'Tarjeta prepago', 'balance'),
        ('15', 'Hipoteca', 'gastos, casa, balance'),
        ('2001', 'Gas casa', 'gastos, casa'),
        ('2000', 'Electricidad casa', 'gastos, casa'),
        ('203', 'Impuestos casa', 'gastos, casa'),
        ('300', 'Comida', 'gastos'),
        ('312', 'Cenas, pinchos…', 'gastos'),
        ('324', 'Gastos coche', 'gastos')])
    def test_filter_form_fill(self, test_num, test_nombre, test_etiqueta, form_filtro_cuentas):
        form = form_filtro_cuentas
        form['f_num'] = test_num
        form['f_nombre'] = test_nombre
        form['f_etiqueta'] = test_etiqueta
        form.submit('accion_filtro', value='aplicar')
        filtro = FiltroCuentas.objects.all()[0]
        assert filtro.num == test_num
        assert filtro.nombre == test_nombre
        assert filtro.etiqueta == test_etiqueta

    @pytest.mark.parametrize('test_num, test_nombre', [('100', 'Caja'),
        ('101', 'Tickets restaurant'), ('1101', 'Cuenta nómina'),
        ('1110', 'Cuenta ahorro'), ('1200', 'Tarjeta Visa'),
        ('1201', 'Tarjeta Amex'), ('1210', 'Tarjeta prepago'),
        ('15', 'Hipoteca'), ('2001', 'Gas casa'), ('2000', 'Electricidad casa'),
        ('203', 'Impuestos casa'), ('300', 'Comida'),
        ('312', 'Cenas, pinchos…'), ('324', 'Gastos coche')])
    def test_apply_filter_num(self, test_num, test_nombre, populate_database_cuentas, create_filter, django_app):
        filtro = create_filter
        _, cuentas = populate_database_cuentas

        # set the filter
        filtro.num = test_num
        filtro.save()

        lista_cuentas = [ c.nombre for c in cuentas ]

        # check only account filtered appears
        resp = django_app.get(reverse('main:cuentas'))
        for name in lista_cuentas:
            if name == test_nombre:
                assert name in resp.text
            else:
                assert name not in resp.text

    @pytest.mark.parametrize('test_name', ['Tarjeta', 'Cuenta', 'casa', 'coche', 'Impuestos'])
    def test_apply_filter_name(self, test_name, populate_database_cuentas, create_filter, django_app):
        filtro = create_filter
        _, cuentas = populate_database_cuentas

        # set the filter
        filtro.nombre = test_name
        filtro.save()

        lista_cuentas = [ c.nombre for c in cuentas ]

        # check only account filtered appears
        resp = django_app.get(reverse('main:cuentas'))
        for name in lista_cuentas:
            if test_name in name:
                assert name in resp.text
            else:
                assert name not in resp.text

    @pytest.mark.parametrize('test_etiqueta', ['gastos', 'ingresos', 'balance', 'casa'])
    def test_apply_filter_etiqueta(self, test_etiqueta, populate_database_cuentas, create_filter, django_app):
        filtro = create_filter
        _, cuentas = populate_database_cuentas

        # set the filter
        filtro.etiqueta = test_etiqueta
        filtro.save()

        lista_cuentas = [ c.nombre for c in cuentas ]

        # check only account filtered appears
        resp = django_app.get(reverse('main:cuentas'))
        for cuenta in cuentas:
            etiquetas_cuenta = [ e.id for e in cuenta.etiqueta.all() ]
            if test_etiqueta in etiquetas_cuenta:
                assert cuenta.nombre in resp.text
            else:
                assert cuenta.nombre not in resp.text

    def test_borrar_filtro_by_button(self, create_and_populate_filter, form_filtro_cuentas):
        create_and_populate_filter
        form = form_filtro_cuentas
        resp = form.submit('accion_filtro', value='borrar')

        filtro = FiltroCuentas.objects.all()[0]
        assert filtro.num == ''
        assert filtro.nombre == ''
        assert filtro.etiqueta == ''

    def test_filter_url_with_wrong_action(self, create_and_populate_filter, csrf_exempt_django_app):
        original_filtro = create_and_populate_filter
        form = {
            'f_num': '204',
            'f_nombre': 'Wrong name',
            'f_etiqueta': 'Wrong etiqueta',
            'accion_filtro': 'wrong_action',
        }
        resp = csrf_exempt_django_app.post(reverse('main:filtro_cuentas'), form)

        # check that nothing is changed
        current_filtro = FiltroCuentas.objects.all()[0]
        assert current_filtro.num == original_filtro.num
        assert current_filtro.nombre == original_filtro.nombre
        assert current_filtro.etiqueta == original_filtro.etiqueta

        # check redirect to the correct page
        assert resp.headers['Location'] == reverse('main:cuentas')
