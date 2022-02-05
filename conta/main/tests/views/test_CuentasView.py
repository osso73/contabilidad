from pytest_django.asserts import assertTemplateUsed

from fixtures_views import *


class TestCuentasView():
    @pytest.fixture
    def form_crear_cuenta(self, django_app):
        resp = django_app.get(reverse('main:cuentas'), user='username')
        return resp.forms['crear_cuenta']

    @pytest.fixture
    def populate_cuentas_for_pagination(self):
        results = 15  # number of entries per page
        total = 125   # number of accounts to create

        # create 125 accounts, to check pagination
        for n in range(125):
            Cuenta.objects.create(num=f'{n+1:03d}', nombre=f'Cuenta núm {n+1:03d}')

        return results, total

    @pytest.mark.parametrize('page', ['/cuentas/', reverse('main:cuentas')])
    def test_redirect_if_not_logged_in(self, page, django_app):
        resp = django_app.get(page)
        assert resp.status_code == 302
        assert resp.url.startswith('/accounts/login/')

    @pytest.mark.parametrize('page', ['/cuentas/', reverse('main:cuentas')])
    def test_view_url_exists_at_desired_location(self, page, django_app):
        resp = django_app.get(page, user='username')
        assert resp.status_code == 200

    def test_view_uses_correct_template(self, django_app):
        resp = django_app.get(reverse('main:cuentas'), user='username')
        assertTemplateUsed(resp, 'main/cuentas.html')

    def test_list_of_cuentas(self, django_app, populate_database_cuentas):
        _, lista_cuentas = populate_database_cuentas
        resp = django_app.get(reverse('main:cuentas'), user='username')
        for cuenta in lista_cuentas:
            assert cuenta.num in resp.text
            assert cuenta.nombre in resp.text

    def test_create_new_cuenta_form_attributes(self, form_crear_cuenta):
        form = form_crear_cuenta

        assert form.id == 'crear_cuenta'
        assert form.method == 'post'
        assert form.action == '/cuentas/'
        assert form.action == reverse('main:cuentas')

        fields = form.fields.keys()
        for f in ['num', 'nombre', 'etiqueta']:
            assert f in fields

    @pytest.mark.parametrize('cuenta',[
        {'num': '100', 'nombre': 'Caja', 'etiqueta': 'balance'},
        {'num': '200', 'nombre': 'Hipoteca', 'etiqueta': None},
    ])
    def test_create_new_cuenta(self, cuenta, form_crear_cuenta, populate_database_etiquetas):
        populate_database_etiquetas

        form = form_crear_cuenta
        form['num'] = cuenta['num']
        form['nombre'] = cuenta['nombre']
        form['etiqueta'] = cuenta['etiqueta']
        form.submit()

        # check that account exists in the database
        cuentas = Cuenta.objects.all()
        assert len(cuentas) == 1
        assert cuentas[0].num == cuenta['num']
        assert cuentas[0].nombre == cuenta['nombre']
        if cuenta['etiqueta']:
            assert cuentas[0].etiqueta.all()[0] == Etiqueta.objects.get(id=cuenta['etiqueta'])
        else:
            assert not cuentas[0].etiqueta.all()

    @pytest.mark.parametrize('page', ['/cuentas/pag/4/', reverse('main:cuentas_pagina', args=[4])])
    def test_view_url_page_exists_at_desired_location(self, page, django_app):
        resp = django_app.get(page, user='username')
        assert resp.status_code == 200

    @pytest.mark.parametrize('page', [1, 2, 3, 4, 5, 6, 7, 8])
    def test_pagination_by_url(self, django_app, page, populate_cuentas_for_pagination):
        results, total = populate_cuentas_for_pagination

        # check pagination page
        resp = django_app.get(reverse('main:cuentas_pagina', args=[page]), user='username')
        for n in range(total):
            if n in range((page-1)*results, page*results):
                assert f'Cuenta núm {n+1:03d}' in resp.text
            else:
                assert f'Cuenta núm {n+1:03d}' not in resp.text

    @pytest.mark.parametrize('page', [1, 2, 3, 4, 5, 6, 7, 8])
    def test_pagination_by_click(self, django_app, page, populate_cuentas_for_pagination):
        results, total = populate_cuentas_for_pagination

        # check pagination page
        initial = django_app.get(reverse('main:cuentas'), user='username')
        resp = initial.click(href=reverse('main:cuentas_pagina', args=[page]), index=0)
        for n in range(total):
            if n in range((page-1)*results, page*results):
                assert f'Cuenta núm {n+1:03d}' in resp.text
            else:
                assert f'Cuenta núm {n+1:03d}' not in resp.text
