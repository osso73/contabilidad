from fixtures_views import *


class TestBorrarMovimientoView():
    def test_view_deletes_movimiento_redirect_to_asientos_by_url(self, django_app, populate_database):
        populate_database
        movimientos = Movimiento.objects.all()
        assert len(movimientos) > 0

        for mov in movimientos:
            django_app.get(f'/movimiento/borrar/{mov.pk}/asientos/')

        movimientos = Movimiento.objects.all()
        assert len(movimientos) == 0

    def test_view_deletes_movimiento_redirect_to_asientos_by_name(self, django_app, populate_database):
        populate_database
        movimientos = Movimiento.objects.all()
        assert len(movimientos) > 0

        for mov in movimientos:
            django_app.get(reverse('main:borrar_movimiento', args=[mov.pk, 'asientos']))

        movimientos = Movimiento.objects.all()
        assert len(movimientos) == 0

    def test_view_redirect_simple(self, client, populate_database):
        _, _, movimientos = populate_database
        pk = movimientos[0].pk
        resp = client.get(reverse('main:borrar_movimiento',
            args=[pk, 'asientos']), follow=True)

        assert len(resp.redirect_chain) == 1
        page_redirected = resp.redirect_chain[0][0]
        assert page_redirected == '/asientos/'

    def test_view_deletes_movimiento_redirect_to_modificar_asientos_by_url(self, django_app, populate_database):
        populate_database
        movimientos = Movimiento.objects.all()
        num_inicial = len(movimientos)
        assert num_inicial > 0

        # delete one movimiento from the asiento 1
        url = f'/movimiento/borrar/{movimientos[0].pk}/modificar_asiento/{movimientos[0].num}/'
        django_app.get(url)

        movimientos = Movimiento.objects.all()
        num_final = len(movimientos)
        assert num_final == num_inicial - 1

    def test_view_deletes_movimiento_redirect_to_modificar_asientos_by_name(self, django_app, populate_database):
        populate_database
        movimientos = Movimiento.objects.all()
        num_inicial = len(movimientos)
        assert num_inicial > 0

        # delete one movimiento from the asiento 1
        url = reverse('main:borrar_movimiento_complejo', args=[movimientos[0].pk, 'modificar_asiento', movimientos[0].num])
        django_app.get(url)

        movimientos = Movimiento.objects.all()
        num_final = len(movimientos)
        assert num_final == num_inicial - 1

    def test_view_redirect_complex(self, client, populate_database):
        _, _, movimientos = populate_database
        url = reverse('main:borrar_movimiento_complejo', args=[movimientos[0].pk, 'modificar_asiento', movimientos[0].num])
        resp = client.get(url, follow=True)
        assert len(resp.redirect_chain) == 1
        page_redirected = resp.redirect_chain[0][0]
        assert page_redirected == '/asientos/modificar/1/'
