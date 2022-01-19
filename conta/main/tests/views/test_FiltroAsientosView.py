from main.models import FiltroMovimientos

from fixtures_views import *


class TestFiltroAsientosView():
    @pytest.fixture
    def create_filter(self):
        # Create filter with default values (all blanks)
        return FiltroMovimientos.objects.create()

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

    @pytest.fixture
    def form_filtro_movimientos(self, django_app):
        resp = django_app.get(reverse('main:asientos'))
        return resp.forms['filtro']

    @pytest.mark.parametrize('page', ['/asientos/filtro/', reverse('main:filtro_asientos')])
    def test_redirect_get_requests(self, page, client):
        resp = client.get(page, follow=True)
        assert len(resp.redirect_chain) == 1
        page_redirected = resp.redirect_chain[0][0]
        assert page_redirected == '/asientos/'

    def test_load_file_form_attributes(self, form_filtro_movimientos):
        form = form_filtro_movimientos

        assert form.id == 'filtro'
        assert form.method == 'post'
        assert form.action == '/asientos/filtro/'
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
        resp = form.submit('accion_filtro', value="aplicar")

        filtro = FiltroMovimientos.objects.all()[0]
        assert filtro.fecha_inicial == '2021-12-01'
        assert filtro.fecha_final == '2021-12-15'
        assert filtro.descripcion == 'descripcion palabras'
        assert filtro.cuenta == '100'
        assert filtro.asiento == '2'

    def test_apply_filter_fecha_inicial(self, populate_database, create_filter, django_app):
        filtro = create_filter
        _, _, movimientos = populate_database

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
        _, _, movimientos = populate_database

        # set the filter
        fecha = '2021-12-19'
        filtro.fecha_final = fecha
        filtro.save()

        movimientos_in = [ m.descripcion for m in movimientos if m.fecha <= fecha]
        movimientos_out = [ m.descripcion for m in movimientos if m.fecha > fecha]

        # check only account filtered appears
        resp = django_app.get(reverse('main:asientos'))
        for name in movimientos_in:
            assert name in resp.text
        for name in movimientos_out:
            assert name not in resp.text

    def test_apply_filter_descripcion(self, populate_database, create_filter, django_app):
        filtro = create_filter
        _, _, movimientos = populate_database

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
        _, cuentas, movimientos = populate_database

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
        _, cuentas, movimientos = populate_database

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

    def test_borrar_filtro_by_button(self, create_and_populate_filter, form_filtro_movimientos):
        create_and_populate_filter
        form = form_filtro_movimientos
        resp = form.submit('accion_filtro', value="borrar")

        # Validate that saved filter is blank
        filtro = FiltroMovimientos.objects.all()[0]
        assert filtro.fecha_inicial == ''
        assert filtro.fecha_final == ''
        assert filtro.descripcion == ''
        assert filtro.cuenta == ''
        assert filtro.asiento == ''
