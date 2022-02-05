from pytest_django.asserts import assertTemplateUsed

from fixtures_views import *


class TestInformesView:
    @pytest.fixture
    def form_parametros(self, django_app):
        resp = django_app.get(reverse('main:informes'), user='username')
        return resp.forms['parametros']

    @pytest.fixture
    def populate_db_informes(self, populate_database):
        _, cuentas, _ = populate_database
        adicionales = [
            [5, '2021-01-28', 'Compra del pan', 2.50, 0, cuentas[0]],
            [5, '2021-01-28', 'Compra del pan', 0, 2.50, cuentas[3]],
            [6, '2021-02-15', 'Compra de fruta', 10.75, 0, cuentas[0]],
            [6, '2021-02-15', 'Compra de fruta', 0, 10.75, cuentas[3]],
            [7, '2021-03-18', 'Calcetines y calzoncillos', 15.85, 0, cuentas[1]],
            [7, '2021-03-18', 'Calcetines y calzoncillos', 0, 15.85, cuentas[3]],
            [8, '2021-04-20', 'Abrigo de invierno', 54, 0, cuentas[1]],
            [8, '2021-04-20', 'Abrigo de invierno', 0, 54, cuentas[3]],
        ]
        for num, fecha, descripcion, debe, haber, cuenta in adicionales:
            Movimiento.objects.create(num=num, fecha=fecha,
                descripcion=descripcion, debe=debe, haber=haber, cuenta=cuenta)

    @pytest.mark.parametrize('page', ['/informes/', reverse('main:informes')])
    def test_redirect_if_not_logged_in(self, page, django_app):
        resp = django_app.get(page)
        assert resp.status_code == 302
        assert resp.url.startswith('/accounts/login/')

    @pytest.mark.parametrize('page', ['/informes/', reverse('main:informes')])
    def test_view_url_exists_at_desired_location(self, page, django_app):
        resp = django_app.get(page, user='username')
        assert resp.status_code == 200

    @pytest.mark.parametrize('page', ['/informes/', reverse('main:informes')])
    def test_view_uses_correct_template(self, page, django_app):
        resp = django_app.get(page, user='username')
        assertTemplateUsed(resp, 'main/informes.html')

    def test_parametros_form_attributes(self, form_parametros):
        form = form_parametros

        assert form.id == 'parametros'
        assert form.method == 'post'
        assert form.action == '/informes/'
        assert form.action == reverse('main:informes')

        fields = form.fields.keys()
        for f in ['f_fecha_inicial', 'f_fecha_final', 'f_tipo', 'f_cuenta', 'f_etiqueta']:
            assert f in fields

    @pytest.mark.parametrize('tipo, fecha_col', [
        ('diario', 'Fecha'), ('semanal', 'Semana'), ('mensual', 'Mes'),
        ('trimestral', 'Trimestre'), ('anual', 'Año')
    ])
    def test_parametros_form_attributes_tipo(self, form_parametros, populate_db_informes, tipo, fecha_col):
        populate_db_informes
        form = form_parametros
        form['f_tipo'].select(text=tipo)
        resp = form.submit()

        # check title and subtitle
        for text in ['Todas las cuentas', f'Informe {tipo}, todas las fechas']:
            assert text in resp.text

        # check columns of table
        for col in [fecha_col, 'Debe', 'Haber', 'Total']:
            assert col in resp.text

    @pytest.mark.parametrize('fecha_ini, fecha_fin, expected_subtitle', [
        ('', '2022-01-29', 'Informe diario, desde el principio hasta 2022-01-29'),
        ('2022-01-29', '', 'Informe diario, desde 2022-01-29 hasta el final'),
        ('2022-01-01', '2022-01-31', 'Informe diario, desde 2022-01-01 hasta 2022-01-31'),
    ], ids=['fecha-inicial', 'fecha-final', 'ambas-fechas'])
    def test_form_fechas(self, form_parametros, populate_db_informes, fecha_ini, fecha_fin, expected_subtitle):
        populate_db_informes
        form = form_parametros
        form['f_fecha_inicial'] = fecha_ini
        form['f_fecha_final'] = fecha_fin
        resp = form.submit()

        # check title and subtitle
        for text in ['Todas las cuentas', expected_subtitle]:
            assert text in resp.text

    @pytest.mark.parametrize('cuenta, etiqueta, expected_title', [
        ('100: Caja', '', 'Cuenta 100: Caja'),
        ('', 'gastos', 'Cuentas del tipo: Gastos corrientes'),
        ('100: Caja', 'gastos', 'Cuenta 100: Caja'),
    ], ids=['cuenta-solo', 'etiqueta-solo', 'cuenta-y-etiqueta'])
    def test_form_cuentas(self, form_parametros, populate_db_informes, cuenta, etiqueta, expected_title):
        populate_db_informes
        form = form_parametros
        form['f_cuenta'] = cuenta
        form['f_etiqueta'] = etiqueta
        resp = form.submit()

        # check title and subtitle
        for text in [expected_title, 'Informe diario, todas las fechas']:
            assert text in resp.text
