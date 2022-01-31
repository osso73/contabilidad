from fixtures_views import *


class TestBorrarCuentaView():
    @pytest.mark.parametrize('access', ['url', 'name'])
    def test_view_deletes_cuenta(self, django_app, access, populate_database_cuentas):
        _, cuentas = populate_database_cuentas
        assert len(cuentas) > 0

        for c in cuentas:
            if access == 'url':
                django_app.get(f'/cuentas/borrar/{c.pk}/')
            else:
                django_app.get(reverse('main:borrar_cuenta', args=[c.pk]))

        cuentas = Cuenta.objects.all()
        assert len(cuentas) == 0

    def test_view_redirect(self, client, populate_database_cuentas):
        _, cuentas = populate_database_cuentas
        url = reverse('main:borrar_cuenta', args=[cuentas[0].pk])
        resp = client.get(url, follow=True)
        assert len(resp.redirect_chain) == 1
        page_redirected = resp.redirect_chain[0][0]
        assert page_redirected == '/cuentas/'

    def test_dont_delete_if_account_has_movements(self, django_app, populate_database):
        _, _, movimientos = populate_database
        num_cuenta = movimientos[0].cuenta.num
        resp = django_app.get(reverse('main:borrar_cuenta', args=[num_cuenta]))

        # check cuenta still exists in the database
        cuenta = Cuenta.objects.filter(num=num_cuenta)
        assert len(cuenta) == 1

        # check error message displayed in the response
        error_msg = "Esta cuenta no se puede borrar, porque tiene movimientos asociados."
        assert error_msg in resp.text
