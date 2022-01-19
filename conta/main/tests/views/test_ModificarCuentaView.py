from pytest_django.asserts import assertTemplateUsed

from fixtures_views import *


class TestModificarCuentaView():
    @pytest.mark.parametrize('page', ['/cuentas/modificar/100/', reverse('main:modificar_cuenta', args=[100])])
    def test_view_url_exists_at_desired_location(self, page, django_app, populate_database_cuentas):
        populate_database_cuentas
        resp = django_app.get(page)
        assert resp.status_code == 200

    @pytest.mark.parametrize('page', ['/cuentas/modificar/100/', reverse('main:modificar_cuenta', args=[100])])
    def test_view_uses_correct_template(self, page, django_app, populate_database_cuentas):
        populate_database_cuentas
        resp = django_app.get(page)
        assertTemplateUsed(resp, 'main/modificar_cuenta.html')

    def test_form_attributes(self, django_app, populate_database_cuentas):
        populate_database_cuentas
        resp = django_app.get(reverse('main:modificar_cuenta', args=[100]))
        form = resp.forms['formulario']

        assert form.id == 'formulario'
        assert form.method == 'post'
        assert form.action == '/cuentas/modificar/100/'
        assert form.action == reverse('main:modificar_cuenta', args=[100])

        fields = form.fields.keys()
        for f in ['num', 'nombre']:
            assert f in fields

    def test_modify_nombre(self, django_app, populate_database_cuentas):
        populate_database_cuentas
        resp = django_app.get(reverse('main:modificar_cuenta', args=[100]))
        form = resp.forms['formulario']
        form['nombre'] = 'Tarjeta visa'
        form.submit()

        cuenta = Cuenta.objects.get(pk=100)
        assert cuenta.nombre == 'Tarjeta visa'
