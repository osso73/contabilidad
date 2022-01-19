from django.db.models.deletion import ProtectedError

from fixtures_models import *


class TestCuentaModel():
    def test_object_name_is_num_colon_nombre(self, create_cuenta):
        _, cuenta = create_cuenta
        expected_name = f'{cuenta.num}: {cuenta.nombre}'
        assert str(cuenta) == expected_name

    def test_nombre_max_length(self, create_cuenta):
        _, cuenta = create_cuenta
        max_length = cuenta._meta.get_field('nombre').max_length
        assert max_length == 50

    def test_delete_protected_account(self, create_movimiento):
        _, cuenta, _ = create_movimiento

        with pytest.raises(ProtectedError):
            cuenta.delete()
