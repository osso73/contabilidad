from pytest_django.asserts import assertTemplateUsed
import random

from fixtures_views import *


class TestBorrarMultiplesMovimientos:
    @pytest.fixture
    def form_multiple_movimientos_delete(self, django_app):
        resp = django_app.get(reverse('main:asientos'), user='username')
        return resp.forms['borrar']

    @pytest.mark.parametrize('page', ['/movimiento/borrar/', reverse('main:borrar_movimiento_multiple')])
    def test_redirect_if_not_logged_in(self, page, django_app):
        resp = django_app.get(page)
        assert resp.status_code == 302
        assert resp.url.startswith('/accounts/login/')

    @pytest.mark.parametrize('page', ['/movimiento/borrar/', reverse('main:borrar_movimiento_multiple')])
    def test_redirect_get_requests(self, page, django_app):
        resp = django_app.get(page, user='username')
        assert resp.status_code == 302
        assert resp.url == reverse('main:asientos')

    def test_form_attributes(self, populate_database, form_multiple_movimientos_delete):
        populate_database
        form = form_multiple_movimientos_delete

        assert form.id == 'borrar'
        assert form.method == 'post'
        assert form.action == '/movimiento/borrar/'
        assert form.action == reverse('main:borrar_movimiento_multiple')

        fields = form.fields.keys()
        for n  in range(8):
            f = f'check_{n+1}'
            assert f in fields


    @pytest.mark.parametrize('num', range(1,9))
    def test_select_some_transactions(self, populate_database, form_multiple_movimientos_delete, num):
        populate_database
        num_movimientos_ini = len(Movimiento.objects.all())

        form = form_multiple_movimientos_delete
        # select num accounts, and delete them
        for n in random.sample(range(8), num):
            f = f'check_{n+1}'
            form[f] = True
        resp = form.submit()

        num_movimientos_end = len(Movimiento.objects.all())
        assert num_movimientos_ini == num_movimientos_end + num
