from decimal import InvalidOperation

from fixtures_models import *


class TestAsientoModel():
    def test_object_name_is_num(self, create_movimiento):
        _, _, movimiento = create_movimiento
        expected_name = str(movimiento.num)
        assert str(movimiento) == expected_name

    def test_descripcion_max_length(self, create_movimiento):
        _, _, movimiento = create_movimiento
        max_length = movimiento._meta.get_field('descripcion').max_length
        assert max_length == 200

    def test_debe_has_two_decimals(self, create_movimiento):
        _, _, movimiento = create_movimiento
        movimiento.debe = 10 / 3
        movimiento.save()
        movimiento = Movimiento.objects.get(pk=1)
        assert str(movimiento.debe) == '3.33'
        movimiento.debe = 5
        movimiento.save()
        movimiento = Movimiento.objects.get(pk=1)
        assert str(movimiento.debe) == '5.00'

    def test_haber_has_two_decimals(self, create_movimiento):
        _, _, movimiento = create_movimiento
        movimiento.haber = 10 / 3
        movimiento.save()
        movimiento = Movimiento.objects.get(pk=1)
        assert str(movimiento.haber) == '3.33'
        movimiento.haber = 5
        movimiento.save()
        movimiento = Movimiento.objects.get(pk=1)
        assert str(movimiento.haber) == '5.00'

    def test_debe_has_eight_digits_max(self, create_movimiento):
        _, _, movimiento = create_movimiento
        movimiento.debe = 1234567890
        with pytest.raises(InvalidOperation):
            movimiento.save()

    def test_debe_ok_if_less_than_eight_digits(self, create_movimiento):
        _, _, movimiento = create_movimiento
        movimiento.debe = 123456
        movimiento.save()
        movimiento = Movimiento.objects.get(pk=1)
        assert movimiento.debe == 123456

    def test_haber_has_eight_digits_max(self, create_movimiento):
        _, _, movimiento = create_movimiento
        movimiento.haber = 1234567890
        with pytest.raises(InvalidOperation):
            movimiento.save()

    def test_haber_ok_if_less_than_eight_digits(self, create_movimiento):
        _, _, movimiento = create_movimiento
        movimiento.haber = 123456
        movimiento.save()
        movimiento = Movimiento.objects.get(pk=1)
        assert movimiento.haber == 123456.00
