from fixtures_views import *


class TestBorrarMovimientoView():
    @pytest.mark.parametrize('page', ['/asientos/modificar/1/', reverse('main:modificar_asiento', args=[1])])
    def test_redirect_if_not_logged_in(self, page, django_app, populate_database):
        populate_database
        movimientos = Movimiento.objects.all()
        inital_length = len(movimientos)
        assert inital_length > 0

        for mov in movimientos:
            resp = django_app.get(f'/movimiento/borrar/{mov.pk}/asientos/')
            assert resp.status_code == 302
            assert resp.url.startswith('/accounts/login/')

        movimientos = Movimiento.objects.all()
        assert len(movimientos) == inital_length
        
    def test_view_deletes_movimiento_redirect_to_asientos_by_url(self, django_app, populate_database):
        populate_database
        movimientos = Movimiento.objects.all()
        assert len(movimientos) > 0

        for mov in movimientos:
            django_app.get(f'/movimiento/borrar/{mov.pk}/asientos/', user='username')

        movimientos = Movimiento.objects.all()
        assert len(movimientos) == 0

    def test_view_deletes_movimiento_redirect_to_asientos_by_name(self, django_app, populate_database):
        populate_database
        movimientos = Movimiento.objects.all()
        assert len(movimientos) > 0

        for mov in movimientos:
            django_app.get(reverse('main:borrar_movimiento', args=[mov.pk, 'asientos']), user='username')

        movimientos = Movimiento.objects.all()
        assert len(movimientos) == 0

    def test_view_redirect_simple(self, django_app, populate_database):
        _, _, movimientos = populate_database
        pk = movimientos[0].pk
        resp = django_app.get(reverse('main:borrar_movimiento',
            args=[pk, 'asientos']), user='username')
        assert resp.status_code == 302
        assert resp.url.startswith('/asientos/')

    def test_view_deletes_movimiento_redirect_to_modificar_asientos_by_url(self, django_app, populate_database):
        populate_database
        movimientos = Movimiento.objects.all()
        num_inicial = len(movimientos)
        assert num_inicial > 0

        # delete one movimiento from the asiento 1
        url = f'/movimiento/borrar/{movimientos[0].pk}/modificar_asiento/{movimientos[0].num}/'
        django_app.get(url, user='username')

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
        django_app.get(url, user='username')

        movimientos = Movimiento.objects.all()
        num_final = len(movimientos)
        assert num_final == num_inicial - 1

    def test_view_redirect_complex(self, django_app, populate_database):
        _, _, movimientos = populate_database
        url = reverse('main:borrar_movimiento_complejo', args=[movimientos[0].pk, 'modificar_asiento', movimientos[0].num])
        resp = django_app.get(url, user='username')
        assert resp.status_code == 302
        assert resp.url.startswith('/asientos/modificar/')
