import datetime

from pytest_django.asserts import assertTemplateUsed

from fixtures_views import *


class TestAsientosView():
    @pytest.fixture
    def form_crear_asiento(self, django_app):
        resp = django_app.get(reverse('main:asientos'), user='username')
        return resp.forms['crear_asiento']

    @pytest.fixture
    def populate_movimientos_for_pagination(self):
        results = 15  # number of entries per page
        total = 125   # number of entries to create

        cuenta = Cuenta.objects.create(num='100', nombre='Caja')
        for n in range(total):
            Movimiento.objects.create(
                num = n+1,
                fecha = datetime.date(2021, 10, 15),
                descripcion = f'Movimiento núm {n+1:03d}',
                debe = 10.52,
                haber = 0,
                cuenta = cuenta,
            )
        return results, total

    @pytest.mark.parametrize('page', ['/asientos/', reverse('main:asientos')])
    def test_redirect_if_not_logged_in(self, page, django_app):
        resp = django_app.get(page)
        assert resp.status_code == 302
        assert resp.url.startswith('/accounts/login/')

    @pytest.mark.parametrize('page', ['/asientos/', reverse('main:asientos')])
    def test_view_url_exists_at_desired_location(self, page, django_app):
        resp = django_app.get(page, user='username')
        assert resp.status_code == 200

    @pytest.mark.parametrize('page', ['/asientos/', reverse('main:asientos')])
    def test_view_uses_correct_template(self, page, django_app):
        resp = django_app.get(page, user='username')
        assertTemplateUsed(resp, 'main/asientos.html')

    def test_list_of_movimientos(self, populate_database, django_app):
        resp = django_app.get(reverse('main:asientos'), user='username')
        _, _, movimientos = populate_database
        for mov in movimientos:
            assert mov.descripcion in resp

    def test_add_simple_asiento_form_attributes(self, form_crear_asiento):
        form = form_crear_asiento

        assert form.id == 'crear_asiento'
        assert form.method == 'post'
        assert form.action == '/asientos/'
        assert form.action == reverse('main:asientos')

        fields = form.fields.keys()
        for f in ['fecha', 'descripcion', 'valor', 'debe', 'haber']:
            assert f in fields


    def test_add_simple_asiento(self, form_crear_asiento, populate_database_cuentas):
        cuentas = populate_database_cuentas
        form = form_crear_asiento

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


    @pytest.mark.parametrize('page', ['/asientos/pag/1/', reverse('main:asientos_pagina', args=[1])])
    def test_view_url_page_exists_at_desired_location(self, page, django_app):
        resp = django_app.get(page, user='username')
        assert resp.status_code == 200

    @pytest.mark.parametrize('page', [1, 2, 3, 4, 5, 6, 7, 8])
    def test_pagination_by_url(self, django_app, page, populate_movimientos_for_pagination):
        results, total = populate_movimientos_for_pagination

        # check pagination page
        resp = django_app.get(reverse('main:asientos_pagina', args=[page]), user='username')
        for n in range(total):
            if n in range((page-1)*results, page*results):
                assert f'Movimiento núm {n+1:03d}' in resp.text
            else:
                assert f'Movimiento núm {n+1:03d}' not in resp.text

    @pytest.mark.parametrize('page', [1, 2, 3, 4, 5, 6, 7, 8])
    def test_pagination_by_click(self, django_app, page, populate_movimientos_for_pagination):
        results, total = populate_movimientos_for_pagination

        # check pagination page
        initial = django_app.get(reverse('main:asientos'), user='username')
        resp = initial.click(href=reverse('main:asientos_pagina', args=[page]), index=0)
        for n in range(total):
            if n in range((page-1)*results, page*results):
                assert f'Movimiento núm {n+1:03d}' in resp.text
            else:
                assert f'Movimiento núm {n+1:03d}' not in resp.text
