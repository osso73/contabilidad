from main.models import FiltroCuentas, FiltroMovimientos
import datetime

from fixtures_views import *


class TestCambiarOrden():
    @pytest.fixture
    def create_filter_cuentas(self):
        # Create filter with default values (all blanks)
        return FiltroCuentas.objects.create()

    @pytest.fixture
    def create_filter_asientos(self):
        # Create filter with default values (all blanks)
        return FiltroMovimientos.objects.create()

    @pytest.mark.parametrize('page', ['/cambiar/orden/cuentas/num/',
        reverse('main:cambiar_orden', args=['cuentas', 'num'])])
    def test_redirect_if_not_logged_in(self, page, django_app):
        resp = django_app.get(page)
        assert resp.status_code == 302  # redirect
        assert resp.url.startswith('/accounts/login/')

    @pytest.mark.parametrize('page', ['/cambiar/orden/cuentas/num/',
        reverse('main:cambiar_orden', args=['cuentas', 'num'])])
    def test_redirect_page_cuentas(self, page, django_app, create_filter_cuentas):
        create_filter_cuentas
        resp = django_app.get(page, user='username')
        assert resp.status_code == 302  # redirect
        assert resp.url.startswith('/cuentas/')

    @pytest.mark.parametrize('access_type', ['url', 'click'])
    @pytest.mark.parametrize('campo', ['num', 'nombre', 'etiqueta'])
    def test_cambiar_orden_cuentas(self, campo, access_type, create_filter_cuentas, django_app, populate_database_cuentas):
        # create data in the database
        populate_database_cuentas
        filtro = create_filter_cuentas
        assert filtro.campo == 'num'
        assert filtro.ascendiente == True

        # access url to change order
        if access_type == 'click':
            resp = django_app.get(reverse('main:cuentas'), user='username')
            resp.click(linkid=campo+"_titulo", verbose=True)
        else:
            django_app.get(reverse('main:cambiar_orden', args=['cuentas', campo]), user='username')

        # validate order is changed in filter
        filtro = FiltroCuentas.objects.all()[0]
        assert filtro.campo == campo
        if campo.lower() == 'num':
            assert filtro.ascendiente == False
        else:
            assert filtro.ascendiente == True

        # access url again to reverse order
        if access_type == 'click':
            resp.click(linkid=campo+"_titulo", verbose=True)
        else:
            django_app.get(reverse('main:cambiar_orden', args=['cuentas', campo]), user='username')

        # check order is reversed in filter
        filtro = FiltroCuentas.objects.all()[0]
        assert filtro.campo == campo
        if campo.lower() == 'num':
            assert filtro.ascendiente == True
        else:
            assert filtro.ascendiente == False

    @pytest.mark.parametrize('access_type', ['url', 'click'])
    @pytest.mark.parametrize('campo', ['num', 'nombre', 'etiqueta'])
    def test_validate_order_cuentas(self, campo, access_type, create_filter_cuentas, django_app, populate_database_etiquetas):
        # create data in the database
        etiquetas = populate_database_etiquetas
        self.populate_cuentas_by_order(campo, 100, etiquetas)
        filtro = create_filter_cuentas

        # access url to change order
        if access_type == 'click':
            page = django_app.get(reverse('main:cuentas'), user='username')
            page.click(linkid=campo+"_titulo", verbose=True)
        else:
            django_app.get(reverse('main:cambiar_orden', args=['cuentas', campo]), user='username')
        resp = django_app.get(reverse('main:cuentas'), user='username')

        # validate order is changed in page
        filtro = FiltroCuentas.objects.all()[0]
        if campo.lower() == 'num':
            assert 'id001' not in resp.text
            assert 'id100' in resp.text
        else:
            assert 'id001' in resp.text
            assert 'id100' not in resp.text

        # access url again to reverse order
        if access_type == 'click':
            page.click(linkid=campo+"_titulo", verbose=True)
        else:
            django_app.get(reverse('main:cambiar_orden', args=['cuentas', campo]), user='username')
        resp = django_app.get(reverse('main:cuentas'), user='username')

        # check order is reversed in page
        if campo.lower() == 'num':
            assert 'id001' in resp.text
            assert 'id100' not in resp.text
        else:
            assert 'id001' not in resp.text
            assert 'id100' in resp.text

    def populate_cuentas_by_order(self, field, total, etiquetas):
        cuenta = dict()
        for n in range(total):
            cuenta['num'] = f'id{n+1:03d}'
            cuenta['nombre'] = f'Cuenta núm {n+1:03d}' if field == 'nombre' else 'Cuenta genérica'
            cuenta['etiqueta'] = 'gastos'
            if field == 'etiqueta':
                if n < 10:
                    cuenta['etiqueta'] = 'balance'
                elif n > total - 10:
                    cuenta['etiqueta'] = 'ingresos'

            c = Cuenta.objects.create(num = cuenta['num'], nombre=cuenta['nombre'])
            c.etiqueta.set([cuenta['etiqueta']])

    @pytest.mark.parametrize('page', ['/cambiar/orden/asientos/num/',
        reverse('main:cambiar_orden', args=['asientos', 'num'])])
    def test_redirect_page_asientos(self, page, django_app, create_filter_asientos):
        create_filter_asientos
        resp = django_app.get(page, user='username')
        assert resp.status_code == 302  # redirect
        assert resp.url.startswith('/asientos/')

    @pytest.mark.parametrize('access_type', ['url', 'click'])
    @pytest.mark.parametrize('campo', ['num', 'fecha', 'descripcion', 'debe', 'haber', 'cuenta'])
    def test_cambiar_orden_asientos(self, campo, access_type, create_filter_asientos, django_app, populate_database):
        # creata data in the database
        populate_database
        filtro = create_filter_asientos
        assert filtro.campo == 'num'
        assert filtro.ascendiente == True

        # access the page
        if access_type == 'click':
            resp = django_app.get(reverse('main:asientos'), user='username')
            resp.click(linkid=campo+"_titulo", verbose=True)
        else:
            django_app.get(reverse('main:cambiar_orden', args=['asientos', campo]), user='username')

        # validate order has changed in the filter
        filtro = FiltroMovimientos.objects.all()[0]
        assert filtro.campo == campo
        if campo.lower() == 'num':
            assert filtro.ascendiente == False
        else:
            assert filtro.ascendiente == True

        # access the page again, to check the order is reversed
        if access_type == 'click':
            resp.click(linkid=campo+"_titulo", verbose=True)
        else:
            django_app.get(reverse('main:cambiar_orden', args=['asientos', campo]), user='username')

        # validate order is reversed in the filter
        filtro = FiltroMovimientos.objects.all()[0]
        assert filtro.campo == campo
        if campo.lower() == 'num':
            assert filtro.ascendiente == True
        else:
            assert filtro.ascendiente == False

    @pytest.mark.parametrize('page', ['/cambiar/orden/wrong/num/',
        reverse('main:cambiar_orden', args=['wrong', 'num'])])
    def test_redirect_page_wrong(self, page, django_app, create_filter_cuentas, create_filter_asientos):
        create_filter_cuentas
        create_filter_asientos
        resp = django_app.get(page, user='username')
        assert resp.status_code == 302  # redirect
        assert resp.url.startswith('/')

    @pytest.mark.parametrize('access_type', ['url', 'click'])
    @pytest.mark.parametrize('campo', ['num', 'fecha', 'descripcion', 'debe', 'haber', 'cuenta'])
    def test_validate_order_asientos(self, create_filter_asientos, django_app, populate_database_cuentas, access_type, campo):
        # create data in the database
        _, cuentas = populate_database_cuentas
        self.populate_database_by_order(campo, 100, cuentas)
        filtro = create_filter_asientos

        # access the url to change order
        if access_type == 'click':
            page = django_app.get(reverse('main:asientos'), user='username')
            page.click(linkid=campo+"_titulo", verbose=True)
        else:
            django_app.get(reverse('main:cambiar_orden', args=['asientos', campo]), user='username')
        resp = django_app.get(reverse('main:asientos'), user='username')

        # validate order is changed
        if campo.lower() == 'num':
            assert 'Movimiento núm 001' not in resp.text
            assert 'Movimiento núm 100' in resp.text
        else:
            assert 'Movimiento núm 001' in resp.text
            assert 'Movimiento núm 100' not in resp.text

        # access the url again to reverse order
        if access_type == 'click':
            page.click(linkid=campo+"_titulo", verbose=True)
        else:
            django_app.get(reverse('main:cambiar_orden', args=['asientos', campo]), user='username')
        resp = django_app.get(reverse('main:asientos'), user='username')

        # validate order is reversed
        if campo.lower() == 'num':
            assert 'Movimiento núm 001' in resp.text
            assert 'Movimiento núm 100' not in resp.text
        else:
            assert 'Movimiento núm 001' not in resp.text
            assert 'Movimiento núm 100' in resp.text

    def populate_database_by_order(self, field, total, cuentas):
        mov = dict()
        for n in range(total):
            mov['num'] = n + 1 if field == 'num' else 1
            mov['fecha'] = datetime.date(2022, 2, 9) + datetime.timedelta(days=n) if field == 'fecha' else datetime.date(2022, 2, 9)
            mov['descripcion'] = f'Movimiento núm {n+1:03d}'
            mov['debe'] = n + 1 if field == 'debe' else 1
            mov['haber'] = n + 1 if field == 'haber' else 1
            mov['cuenta'] = cuentas[1]
            if field == 'cuenta':
                if n < 10:
                    mov['cuenta'] = cuentas[0]
                elif n > total - 10:
                    mov['cuenta'] = cuentas[2]

            Movimiento.objects.create(num = mov['num'], fecha = mov['fecha'],
                descripcion = mov['descripcion'], debe = mov['debe'],
                haber = mov['haber'], cuenta = mov['cuenta']
            )
