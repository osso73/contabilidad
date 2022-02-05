from fixtures_views import *


class TestGestionarEtiqueta():
    @pytest.fixture
    def form_filtro_etiquetas(self, django_app):
        resp = django_app.get(reverse('main:cuentas'), user='username')
        return resp.forms['etiquetas']

    @pytest.mark.parametrize('page', ['/cuentas/etiqueta/gestionar/', reverse('main:gestionar_etiqueta')])
    def test_redirect_if_not_logged_in(self, page, django_app):
        resp = django_app.get(page)
        assert resp.status_code == 302
        assert resp.url.startswith('/accounts/login/')

    @pytest.mark.parametrize('page', ['/cuentas/etiqueta/gestionar/', reverse('main:gestionar_etiqueta')])
    def test_redirect_get_requests(self, page, django_app):
        resp = django_app.get(page, user='username')
        assert resp.status_code == 302
        assert resp.url == reverse('main:cuentas')

    def test_load_file_form_attributes(self, form_filtro_etiquetas):
        form = form_filtro_etiquetas

        assert form.id == 'etiquetas'
        assert form.method == 'post'
        assert form.action == '/cuentas/etiqueta/gestionar/'
        assert form.action == reverse('main:gestionar_etiqueta')

        fields = form.fields.keys()
        for f in ['e_id', 'e_nombre']:
            assert f in fields

    @pytest.mark.parametrize('test_id, test_nombre', [
        ('gastos', 'Gastos corrientes'), ('ingresos', 'Ingresos'),
        ('balance', 'Cuentas balance'), ('casa', 'Gastos de la casa')])
    def test_create_etiqueta(self, test_id, test_nombre, form_filtro_etiquetas):
        form = form_filtro_etiquetas
        form['e_id'] = test_id
        form['e_nombre'] = test_nombre
        resp = form.submit('accion_etiqueta', value='anadir')
        etiqueta_db = Etiqueta.objects.get(id=test_id)
        assert etiqueta_db.id == test_id
        assert etiqueta_db.nombre == test_nombre

    @pytest.mark.parametrize('test_id', ['gastos', 'ingresos', 'balance', 'casa'])
    def test_borrar_etiqueta_existing(self, test_id, populate_database_etiquetas, form_filtro_etiquetas):
        etiquetas = populate_database_etiquetas
        form = form_filtro_etiquetas
        form['e_id'] = test_id
        resp = form.submit('accion_etiqueta', value='borrar')

        assert len(etiquetas) == len(Etiqueta.objects.all()) + 1, "One less etiqueta in the database than before erasing"

        for etiqueta in etiquetas:
            if etiqueta.id == test_id:
                assert len(Etiqueta.objects.filter(id=etiqueta.id)) == 0, "The erased etiqueta does not exist"
            else:
                assert len(Etiqueta.objects.filter(id=etiqueta.id)) == 1, "Other etiquetas still exist"

    def test_borrar_etiqueta_non_existing(self, populate_database_etiquetas, form_filtro_etiquetas):
        etiquetas = populate_database_etiquetas
        form = form_filtro_etiquetas
        form['e_id'] = 'wrong'
        resp = form.submit('accion_etiqueta', value='borrar')

        assert len(etiquetas) == len(Etiqueta.objects.all()), "Same number of etiquetas in the database than before erasing"

    def test_gestionar_etiquetas_with_wrong_action(self, populate_database_etiquetas, csrf_exempt_django_app):
        original_etiquetas = populate_database_etiquetas
        form = {
            'e_id': 'wrong id',
            'e_nombre': 'Wrong name',
            'accion_etiqueta': 'wrong_action',
        }
        resp = csrf_exempt_django_app.post(reverse('main:gestionar_etiqueta'), form, user='username')

        current_etiquetas = Etiqueta.objects.all()
        assert original_etiquetas == list(current_etiquetas), "The list of etiquetas should be unchanged"
        assert resp.headers['Location'] == reverse('main:cuentas'), "The view should be redirected to main:cuentas"
