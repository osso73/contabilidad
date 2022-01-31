from main.models import FiltroCuentas, FiltroMovimientos

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
    def test_redirect_page_cuentas(self, page, client, create_filter_cuentas):
        create_filter_cuentas
        resp = client.get(page, follow=True)
        assert len(resp.redirect_chain) == 1
        page_redirected = resp.redirect_chain[0][0]
        assert page_redirected == '/cuentas/'

    @pytest.mark.parametrize('access_type', ['url', 'click'])
    @pytest.mark.parametrize('campo', ['num', 'nombre'])
    def test_cambiar_orden_cuentas(self, campo, access_type, create_filter_cuentas, django_app, populate_database_cuentas):
        populate_database_cuentas
        filtro = create_filter_cuentas
        assert filtro.campo == 'num'
        assert filtro.ascendiente == True
        if access_type == 'click':
            resp = django_app.get(reverse('main:cuentas'))
            resp.click(linkid=campo+"_titulo", verbose=True)
        else:
            django_app.get(reverse('main:cambiar_orden', args=['cuentas', campo]))
        filtro = FiltroCuentas.objects.all()[0]
        assert filtro.campo == campo
        if campo.lower() == 'num':
            assert filtro.ascendiente == False
        else:
            assert filtro.ascendiente == True

        if access_type == 'click':
            resp.click(linkid=campo+"_titulo", verbose=True)
        else:
            django_app.get(reverse('main:cambiar_orden', args=['cuentas', campo]))
        filtro = FiltroCuentas.objects.all()[0]
        assert filtro.campo == campo
        if campo.lower() == 'num':
            assert filtro.ascendiente == True
        else:
            assert filtro.ascendiente == False

    @pytest.mark.parametrize('page', ['/cambiar/orden/asientos/num/',
        reverse('main:cambiar_orden', args=['asientos', 'num'])])
    def test_redirect_page_asientos(self, page, client, create_filter_asientos):
        create_filter_asientos
        resp = client.get(page, follow=True)
        assert len(resp.redirect_chain) == 1
        page_redirected = resp.redirect_chain[0][0]
        assert page_redirected == '/asientos/'

    @pytest.mark.parametrize('access_type', ['url', 'click'])
    @pytest.mark.parametrize('campo', ['num', 'fecha', 'descripcion', 'debe', 'haber', 'cuenta'])
    def test_cambiar_orden_asientos(self, campo, access_type, create_filter_asientos, django_app, populate_database):
        populate_database
        filtro = create_filter_asientos
        assert filtro.campo == 'num'
        assert filtro.ascendiente == True
        if access_type == 'click':
            resp = django_app.get(reverse('main:asientos'))
            resp.click(linkid=campo+"_titulo", verbose=True)
        else:
            django_app.get(reverse('main:cambiar_orden', args=['asientos', campo]))
        filtro = FiltroMovimientos.objects.all()[0]
        assert filtro.campo == campo
        if campo.lower() == 'num':
            assert filtro.ascendiente == False
        else:
            assert filtro.ascendiente == True

        if access_type == 'click':
            resp.click(linkid=campo+"_titulo", verbose=True)
        else:
            django_app.get(reverse('main:cambiar_orden', args=['asientos', campo]))
        filtro = FiltroMovimientos.objects.all()[0]
        assert filtro.campo == campo
        if campo.lower() == 'num':
            assert filtro.ascendiente == True
        else:
            assert filtro.ascendiente == False

    @pytest.mark.parametrize('page', ['/cambiar/orden/wrong/num/',
        reverse('main:cambiar_orden', args=['wrong', 'num'])])
    def test_redirect_page_wrong(self, page, client, create_filter_cuentas, create_filter_asientos):
        create_filter_cuentas
        create_filter_asientos
        resp = client.get(page, follow=True)
        assert len(resp.redirect_chain) == 1
        page_redirected = resp.redirect_chain[0][0]
        assert page_redirected == '/'

    def test_validate_order(self):
        pass
