from pytest_django.asserts import assertTemplateUsed

from fixtures_views import *


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
    def test_view_uses_correct_template(self, page, django_app):
        resp = django_app.get(page)
        assertTemplateUsed(resp, 'main/cuentas.html')


    def test_list_of_cuentas(self, django_app, populate_database_cuentas):
        _, lista_cuentas = populate_database_cuentas
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

    @pytest.mark.parametrize('page', ['/cuentas/pag/4/', reverse('main:cuentas_pagina', args=[4])])
    def test_view_url_page_exists_at_desired_location(self, page, django_app):
        resp = django_app.get(page)
        assert resp.status_code == 200

    @pytest.mark.parametrize('page', [1, 2, 3, 4, 5, 6, 7, 8])
    def test_pagination_by_url(self, django_app, page):
        results = 25
        for n in range(200):
            Cuenta.objects.create(num=f'{n+1:03d}', nombre=f'Cuenta núm {n+1:03d}')
        resp = django_app.get(reverse('main:cuentas_pagina', args=[page]))

        for n in range(200):
            if n in range((page-1)*results, page*results):
                assert f'Cuenta núm {n+1:03d}' in resp.text
            else:
                assert f'Cuenta núm {n+1:03d}' not in resp.text

    @pytest.mark.parametrize('page', [1, 2, 3, 4, 5, 6, 7, 8])
    def test_pagination_by_click(self, django_app, page):
        results = 25
        for n in range(200):
            Cuenta.objects.create(num=f'{n+1:03d}', nombre=f'Cuenta núm {n+1:03d}')
        initial = django_app.get(reverse('main:cuentas'))
        resp = initial.click(href=reverse('main:cuentas_pagina', args=[page]), index=0)

        for n in range(200):
            if n in range((page-1)*results, page*results):
                assert f'Cuenta núm {n+1:03d}' in resp.text
            else:
                assert f'Cuenta núm {n+1:03d}' not in resp.text
