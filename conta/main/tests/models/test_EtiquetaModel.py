from django.db.models.deletion import ProtectedError

from fixtures_models import *


class TestEtiquetaModel():
    def test_object_name_is_id(self, create_etiqueta):
        etiqueta = create_etiqueta
        expected_name = etiqueta.id
        assert str(etiqueta) == expected_name

    def test_nombre_max_length(self, create_etiqueta):
        etiqueta = create_etiqueta
        max_length = etiqueta._meta.get_field('nombre').max_length
        assert max_length == 50
