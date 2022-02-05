from fixtures_views import *


class TestBorrarCuentaView():
    @pytest.mark.parametrize('access', ['url', 'name'])
    def test_redirect_if_not_logged_in(self, access, django_app, populate_database):
        populate_database_cuentas
        cuentas = Cuenta.objects.all()
        inital_length = len(cuentas)
        assert inital_length > 0

        for c in cuentas:
            if access == 'url':
                resp = django_app.get(f'/cuentas/borrar/{c.pk}/')
            else:
                resp = django_app.get(reverse('main:borrar_cuenta', args=[c.pk]))
            assert resp.status_code == 302
            assert resp.url.startswith('/accounts/login/')

        cuentas = Cuenta.objects.all()
        assert len(cuentas) == inital_length


    @pytest.mark.parametrize('access', ['url', 'name'])
    def test_view_deletes_cuenta(self, django_app, access, populate_database_cuentas):
        _, cuentas = populate_database_cuentas
        assert len(cuentas) > 0

        for c in cuentas:
            if access == 'url':
                django_app.get(f'/cuentas/borrar/{c.pk}/', user='username')
            else:
                django_app.get(reverse('main:borrar_cuenta', args=[c.pk]), user='username')

        cuentas = Cuenta.objects.all()
        assert len(cuentas) == 0

    def test_view_redirect(self, django_app, populate_database_cuentas):
        _, cuentas = populate_database_cuentas
        url = reverse('main:borrar_cuenta', args=[cuentas[0].pk])
        resp = django_app.get(url, user='username')
        assert resp.status_code == 302
        assert resp.url.startswith('/cuentas/')

    def test_dont_delete_if_account_has_movements(self, django_app, populate_database):
        _, _, movimientos = populate_database
        num_cuenta = movimientos[0].cuenta.num
        resp = django_app.get(reverse('main:borrar_cuenta', args=[num_cuenta]), user='username')

        # check cuenta still exists in the database
        cuenta = Cuenta.objects.filter(num=num_cuenta)
        assert len(cuenta) == 1

        # check error message displayed in the response
        error_msg = "Esta cuenta no se puede borrar, porque tiene movimientos asociados."
        assert error_msg in resp.text
