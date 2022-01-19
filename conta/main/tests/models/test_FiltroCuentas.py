from django.core.exceptions import ValidationError
from main.models import FiltroCuentas

from fixtures_models import *


class TestFiltroCuentas():
    @pytest.fixture
    def create_filtro_cuentas(self):
        # Set up non-modified objects used by all test methods
        return  FiltroCuentas.objects.create()

    def test_num_max_length(self, create_filtro_cuentas):
        filtro = create_filtro_cuentas
        max_length = filtro._meta.get_field('num').max_length
        assert max_length == 10

    def test_nombre_max_length(self, create_filtro_cuentas):
        filtro = create_filtro_cuentas
        max_length = filtro._meta.get_field('nombre').max_length
        assert max_length == 50

    def test_campo_max_length(self, create_filtro_cuentas):
        filtro = create_filtro_cuentas
        max_length = filtro._meta.get_field('campo').max_length
        assert max_length == 10

    def test_etiqueta_max_length(self, create_filtro_cuentas):
        filtro = create_filtro_cuentas
        max_length = filtro._meta.get_field('etiqueta').max_length
        assert max_length == 15

    def test_num_default(self, create_filtro_cuentas):
        filtro = create_filtro_cuentas
        assert filtro.num == ''

    def test_nombre_default(self, create_filtro_cuentas):
        filtro = create_filtro_cuentas
        assert filtro.nombre == ''

    def test_campo_default(self, create_filtro_cuentas):
        filtro = create_filtro_cuentas
        assert filtro.campo == 'num'

    def test_ascendiente_default(self, create_filtro_cuentas):
        filtro = create_filtro_cuentas
        assert filtro.ascendiente is True

    def test_etiqueta_default(self, create_filtro_cuentas):
        filtro = create_filtro_cuentas
        assert filtro.etiqueta == ''


    def test_campo_choices(self, create_filtro_cuentas):
        filtro = create_filtro_cuentas
        filtro.num = '100'
        filtro.nombre = 'Caja'
        filtro.etiqueta = 'label'
        for c in ['num', 'nombre']:
            filtro.campo = c
            filtro.save()
            filtro.full_clean()

        filtro.campo = 'wrong'
        filtro.save()
        with pytest.raises(ValidationError):
            filtro.full_clean()
