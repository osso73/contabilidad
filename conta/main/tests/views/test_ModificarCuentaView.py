from pytest_django.asserts import assertTemplateUsed

from fixtures_views import *


class TestModificarCuentaView():
    @pytest.fixture
    def form_modificar_cuenta(self, django_app):
        resp = django_app.get(reverse('main:modificar_cuenta', args=[100]), user='username')
        return resp.forms['formulario']

    @pytest.mark.parametrize('page', ['/cuentas/modificar/100/', reverse('main:modificar_cuenta', args=[100])])
    def test_redirect_if_not_logged_in(self, page, django_app):
        resp = django_app.get(page)
        assert resp.status_code == 302
        assert resp.url.startswith('/accounts/login/')

    @pytest.mark.parametrize('page', ['/cuentas/modificar/100/', reverse('main:modificar_cuenta', args=[100])])
    def test_view_url_exists_at_desired_location(self, page, django_app, populate_database_cuentas):
        populate_database_cuentas
        resp = django_app.get(page, user='username')
        assert resp.status_code == 200

    @pytest.mark.parametrize('page', ['/cuentas/modificar/100/', reverse('main:modificar_cuenta', args=[100])])
    def test_view_uses_correct_template(self, page, django_app, populate_database_cuentas):
        populate_database_cuentas
        resp = django_app.get(page, user='username')
        assertTemplateUsed(resp, 'main/modificar_cuenta.html')

    def test_form_attributes(self, populate_database_cuentas, form_modificar_cuenta):
        populate_database_cuentas
        form = form_modificar_cuenta

        assert form.id == 'formulario'
        assert form.method == 'post'
        assert form.action == '/cuentas/modificar/100/'
        assert form.action == reverse('main:modificar_cuenta', args=[100])

        fields = form.fields.keys()
        for f in ['num', 'nombre']:
            assert f in fields

    def test_modify_nombre(self, populate_database_cuentas, form_modificar_cuenta):
        populate_database_cuentas
        form = form_modificar_cuenta
        form['nombre'] = 'Tarjeta visa'
        form.submit()

        cuenta = Cuenta.objects.get(pk=100)
        assert cuenta.nombre == 'Tarjeta visa'

    def test_modify_etiqueta_no_error(self, populate_database_cuentas, form_modificar_cuenta):
        populate_database_cuentas
        form = form_modificar_cuenta
        form['etiqueta'] = 'gastos'
        form.submit()

        cuenta = Cuenta.objects.get(pk=100)
        etiqueta_db = cuenta.etiqueta.all()
        assert len(etiqueta_db) == 1
        assert etiqueta_db[0].id == 'gastos'

    def test_modify_several_etiquetas_with_error(self, populate_database_cuentas, form_modificar_cuenta):
        populate_database_cuentas
        form = form_modificar_cuenta
        form['etiqueta'] = 'gastos, casa, etiqueta incorrecta'
        form.submit()

        cuenta = Cuenta.objects.get(pk=100)
        etiqueta_db = cuenta.etiqueta.all()
        etiqueta_names = [ e.id for e in etiqueta_db ]
        assert len(etiqueta_db) == 2
        assert 'gastos' in etiqueta_names
        assert 'casa' in etiqueta_names
        assert 'etiqueta incorrecta' not in etiqueta_names
