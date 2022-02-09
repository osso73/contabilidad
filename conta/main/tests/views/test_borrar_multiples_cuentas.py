from pytest_django.asserts import assertTemplateUsed
import random

from fixtures_views import *


class TestBorrarMultiplesCuentas:
    @pytest.fixture
    def form_multiple_cuentas_delete(self, django_app):
        resp = django_app.get(reverse('main:cuentas'), user='username')
        return resp.forms['borrar']

    @pytest.mark.parametrize('page', ['/cuentas/borrar/', reverse('main:borrar_cuenta_multiple')])
    def test_redirect_if_not_logged_in(self, page, django_app):
        resp = django_app.get(page)
        assert resp.status_code == 302
        assert resp.url.startswith('/accounts/login/')

    @pytest.mark.parametrize('page', ['/cuentas/borrar/', reverse('main:borrar_cuenta_multiple')])
    def test_redirect_get_requests(self, page, django_app):
        resp = django_app.get(page, user='username')
        assert resp.status_code == 302
        assert resp.url == reverse('main:cuentas')

    def test_form_attributes(self, populate_database_cuentas, form_multiple_cuentas_delete):
        populate_database_cuentas
        form = form_multiple_cuentas_delete

        assert form.id == 'borrar'
        assert form.method == 'post'
        assert form.action == '/cuentas/borrar/'
        assert form.action == reverse('main:borrar_cuenta_multiple')

        fields = form.fields.keys()
        for n  in range(14):
            f = f'check_{n+1}'
            assert f in fields

    @pytest.mark.parametrize('num', range(1,15))
    def test_select_some_accounts(self, populate_database_cuentas, form_multiple_cuentas_delete, num):
        _, cuentas = populate_database_cuentas
        num_cuentas_ini = len(Cuenta.objects.all())

        form = form_multiple_cuentas_delete
        erased = list()
        # select num accounts, and delete them
        for n in random.sample(range(14), num):
            f = f'check_{n+1}'
            form[f] = True
            erased.append(n)
        resp = form.submit()

        num_cuentas_end = len(Cuenta.objects.all())
        assert num_cuentas_ini == num_cuentas_end + num
        for n in erased:
            assert cuentas[n].nombre not in resp.text


    def test_delete_accounts_with_movimientos(self, populate_database, form_multiple_cuentas_delete):
        _, cuentas, _ = populate_database

        form = form_multiple_cuentas_delete
        # select num accounts, and delete them
        cant_erase = [0, 1]  # accounts with movimientos - can't be erased
        erase = [12, 13]     # accounts without movimientos
        for n in erase + cant_erase:
            f = f'check_{n+1}'
            form[f] = True
        resp = form.submit()

        names = [ c.nombre for c in Cuenta.objects.all() ]

        assert "La(s) siguiente(s) cuentas no se pueden borrar" in resp.text

        # accounts have been erased
        for n in erase:
            assert cuentas[n].nombre not in names
            assert cuentas[n].nombre not in resp.text

        # accounts not erased
        for n in cant_erase:
            assert cuentas[n].nombre in names
            assert cuentas[n].nombre in resp.text
