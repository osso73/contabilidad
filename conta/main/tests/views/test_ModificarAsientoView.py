import datetime

from pytest_django.asserts import assertTemplateUsed

from fixtures_views import *


class TestModificarAsientoView():
    @pytest.fixture
    def form_modificar_asiento(self, django_app):
        resp = django_app.get(reverse('main:modificar_asiento', args=[1]))
        return resp.forms['formulario']

    @pytest.mark.parametrize('page', ['/asientos/modificar/1/', reverse('main:modificar_asiento', args=[1])])
    def test_view_url_exists_at_desired_location(self, page, django_app, populate_database):
        populate_database
        resp = django_app.get(page)
        assert resp.status_code == 200

    @pytest.mark.parametrize('page', ['/asientos/modificar/1/', reverse('main:modificar_asiento', args=[1])])
    def test_view_uses_correct_template_oriol(self, page, django_app, populate_database):
        populate_database
        resp = django_app.get(page)
        assertTemplateUsed(resp, 'main/modificar_asiento.html')

    def test_form_attributes(self, populate_database, form_modificar_asiento):
        populate_database
        form = form_modificar_asiento

        assert form.id == 'formulario'
        assert form.method == 'post'
        assert form.action == '/asientos/modificar/1/'
        assert form.action == reverse('main:modificar_asiento', args=[1])

        fields = form.fields.keys()
        for f in ['id0', 'num0', 'fecha0', 'descripcion0', 'debe0', 'haber0', 'cuenta0']:
            assert f in fields

    def test_modify_asiento(self, populate_database, form_modificar_asiento):
        populate_database
        form = form_modificar_asiento
        form['num0'] = '115'
        form.submit()

        movimiento = Movimiento.objects.all()[0]
        assert movimiento.num == 115


    def test_modify_fecha(self, populate_database, form_modificar_asiento):
        populate_database
        form = form_modificar_asiento
        form['fecha0'] = '2021-12-31'
        form.submit()

        movimiento = Movimiento.objects.all()[0]
        assert movimiento.fecha == datetime.date(2021, 12, 31)

    def test_modify_descripcion(self, populate_database, form_modificar_asiento):
        populate_database
        form = form_modificar_asiento
        form['descripcion0'] = 'Nueva descripcion'
        form.submit()

        movimiento = Movimiento.objects.all()[0]
        assert movimiento.descripcion == 'Nueva descripcion'

    def test_modify_debe(self, populate_database, form_modificar_asiento):
        populate_database
        form = form_modificar_asiento
        form['debe0'] = '243.87'
        form.submit()

        movimiento = Movimiento.objects.all()[0]
        assert float(movimiento.debe) == 243.87

    def test_modify_haber(self, populate_database, form_modificar_asiento):
        populate_database
        form = form_modificar_asiento
        form['haber0'] = '521.67'
        form.submit()

        movimiento = Movimiento.objects.all()[0]
        assert float(movimiento.haber) == 521.67

    def test_modify_cuenta(self, populate_database, form_modificar_asiento):
        Cuenta.objects.create(num='999', nombre='Tarjeta visa probando')
        populate_database
        form = form_modificar_asiento
        form['cuenta0'] = '999'
        form.submit()

        movimiento = Movimiento.objects.all()[0]
        assert movimiento.cuenta.num == '999'
        assert movimiento.cuenta.nombre == 'Tarjeta visa probando'

    def test_add_movimiento(self, django_app, populate_database, form_modificar_asiento):
        resp = django_app.get(reverse('main:modificar_asiento', args=[1]))
        resp.click(linkid='anadir_movimiento')

        mov = Movimiento.objects.filter(num=1)
        assert len(mov) == 3
        assert mov[2].num == 1
        assert mov[2].fecha == datetime.date(2021, 12, 28)
        assert mov[2].descripcion == ''
        assert float(mov[2].debe) == 0.0
        assert float(mov[2].haber) == 0.0
        assert mov[2].cuenta.num == '100'
