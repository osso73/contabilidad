from django.core.exceptions import ValidationError
from main.models import FiltroMovimientos

from fixtures_models import *


class TestFiltroMovimientos():
    @pytest.fixture
    def create_filtro_movimientos(self):
        # Set up non-modified objects used by all test methods
        return FiltroMovimientos.objects.create()

    @pytest.mark.parametrize('field, length', [
        ('fecha_inicial', 10),
        ('fecha_final', 10),
        ('descripcion', 200),
        ('cuenta', 10),
        ('asiento', 10),
        ('campo', 15),
        ('etiqueta', 15),
    ])
    def test_fields_max_length(self, create_filtro_movimientos, field, length):
        filtro = create_filtro_movimientos
        max_length = filtro._meta.get_field(field).max_length
        assert max_length == length

    @pytest.mark.parametrize('field, default', [
        ('fecha_inicial', ''),
        ('fecha_final', ''),
        ('descripcion', ''),
        ('cuenta', ''),
        ('asiento', ''),
        ('campo', 'num'),
        ('etiqueta', ''),
    ])
    def test_fields_default(self, create_filtro_movimientos, field, default):
        filtro = create_filtro_movimientos
        assert getattr(filtro, field) == default

    def test_campo_choices(self, create_filtro_movimientos):
        filtro = create_filtro_movimientos
        filtro.fecha_inicial = '2021-10-31'
        filtro.fecha_final = '2021-12-31'
        filtro.descripcion = 'Probando'
        filtro.cuenta = '100'
        filtro.asiento = '1'
        filtro.etiqueta = 'label'
        for c in ['num', 'fecha', 'descripcion', 'debe', 'haber', 'cuenta']:
            filtro.campo = c
            filtro.save()
            filtro.full_clean()

        filtro.campo = 'wrong'
        filtro.save()
        with pytest.raises(ValidationError):
            filtro.full_clean()
