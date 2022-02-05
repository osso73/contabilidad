import datetime

from fixtures_views import *


class TestAnadirMovimientoView():
    @pytest.mark.parametrize('page', ['/movimiento/anadir/1/2021-12-28/',
        reverse('main:anadir_movimiento', args=[1, '2021-12-28'])])
    def test_redirect_if_not_logged_in(self, page, django_app):
        resp = django_app.get(page)
        assert resp.status_code == 302
        assert resp.url.startswith('/accounts/login/')

    @pytest.mark.parametrize('page', ['/movimiento/anadir/1/2021-12-28/',
        reverse('main:anadir_movimiento', args=[1, '2021-12-28'])])
    def test_view_redirect(self, page, django_app, populate_database):
        """test that view is redirected to the right page"""
        populate_database
        resp = django_app.get(page, user='username')
        assert resp.status_code == 302  # expect a redirect
        assert resp.url.startswith('/asientos/modificar/1/')

    def test_view_url_creates_new_movimiento(self, django_app, populate_database):
        _, _, movimientos = populate_database
        num_inicial = len(movimientos)
        resp = django_app.get(
            reverse('main:anadir_movimiento', args=[1, '2021-12-28']),
            user='username'
            )
        movimientos = Movimiento.objects.all()
        num_final = len(movimientos)
        assert num_final == num_inicial + 1
        last = movimientos[num_final-1]
        assert last.fecha == datetime.date(2021, 12, 28)

    def test_add_movimiento(self, django_app, populate_database):
        _, _, movimientos = populate_database
        num_inicial = len(movimientos)
        resp = django_app.get(
            reverse('main:anadir_movimiento', args=[1, '2021-12-28']), 
            user='username'
            )

        movimientos = Movimiento.objects.all()
        num_final = len(movimientos)
        assert num_final == num_inicial + 1

        mov = movimientos[num_final-1]  # get the last movimiento that has been just added

        assert mov.num == 1
        assert mov.fecha == datetime.date(2021, 12, 28)
        assert mov.descripcion ==''
        assert float(mov.debe) == 0.0
        assert float(mov.haber) == 0.0
        assert mov.cuenta.num == '100'
