import datetime

from fixtures_views import *


class TestAnadirMovimientoView():
    @pytest.mark.parametrize('page', ['/movimiento/anadir/1/2021-12-28/',
        reverse('main:anadir_movimiento', args=[1, '2021-12-28'])])
    def test_view_url_exists_at_desired_location(self, page, django_app, populate_database):
        populate_database
        resp = django_app.get(page)
        assert resp.status_code == 302  # expect a redirect

    def test_view_url_creates_new_movimiento(self, django_app, populate_database):
        _, _, movimientos = populate_database
        num_inicial = len(movimientos)
        resp = django_app.get(reverse('main:anadir_movimiento', args=[1, '2021-12-28']))
        movimientos = Movimiento.objects.all()
        num_final = len(movimientos)
        assert num_final == num_inicial + 1
        last = movimientos[num_final-1]
        assert last.fecha == datetime.date(2021, 12, 28)

    def test_view_redirect(self, client, populate_database):
        """test that view is redirected to the right page"""
        populate_database
        url = reverse('main:anadir_movimiento', args=[1, '2021-12-28'])
        resp = client.get(url, follow=True)
        assert len(resp.redirect_chain) == 1
        page_redirected = resp.redirect_chain[0][0]
        assert page_redirected == '/asientos/modificar/1/'

    def test_add_movimiento(self, django_app, populate_database):
        _, _, movimientos = populate_database
        num_inicial = len(movimientos)
        resp = django_app.get(reverse('main:anadir_movimiento', args=[1, '2021-12-28']))

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
