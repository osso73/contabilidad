import pandas as pd
import numpy as np
import datetime
from django.core.files import File
from django.core.exceptions import ObjectDoesNotExist

from fixtures_functions import *
from main.functions import max_num_asiento, crea_asiento_simple, extraer_asientos, crear_asientos, valida_simple, valida_compleja


class TestMaxNumAsiento:
    def test_get_max_num_asiento(self, populate_database):
        _, _, movimientos = populate_database
        nums = [ m.num for m in movimientos ]
        assert max(nums) == max_num_asiento()

    def test_get_max_num_asiento_empty_db(self):
        assert max_num_asiento() == 0


class TestCreaAsientoSimple:
    def test_crea_asiento_values(self, populate_database):
        _, cuentas, _ = populate_database
        simple = {
            'num': 500,
            'fecha': datetime.date(2022, 1, 26),
            'descripcion': 'Descripción del movimiento',
            'valor': 352.55,
            'debe': cuentas[0],
            'haber': cuentas[1],
        }
        crea_asiento_simple(simple)
        asiento = Movimiento.objects.filter(num=500)
        for movimiento in asiento:
            assert movimiento.num == simple['num']
            assert movimiento.fecha == simple['fecha']
            assert movimiento.descripcion == simple['descripcion']
            assert float(movimiento.debe) in [simple['valor'], 0.0]
            assert float(movimiento.haber) in [simple['valor'], 0.0]
            assert movimiento.cuenta == cuentas[0] or cuentas[1]

    def test_crea_asiento_as_strings(self, populate_database):
        _, cuentas, _ = populate_database
        # providing the values as strings, as provided by form
        simple = {
            'num': 500,
            'fecha': '2022-01-26',
            'descripcion': 'Descripción del movimiento',
            'valor': '352.55',
            'debe': cuentas[0],
            'haber': cuentas[1],
        }
        crea_asiento_simple(simple)
        asiento = Movimiento.objects.filter(num=500)
        for movimiento in asiento:
            assert movimiento.num == simple['num']
            assert movimiento.fecha ==  datetime.date.fromisoformat(simple['fecha'])
            assert movimiento.descripcion == simple['descripcion']
            assert float(movimiento.debe) in [float(simple['valor']), 0.0]
            assert float(movimiento.haber) in [float(simple['valor']), 0.0]
            assert movimiento.cuenta == cuentas[0] or cuentas[1]


class TestExtraerAsientos:
    def test_loading_good_file_plantilla_simple(self):
        f = open('main/tests/data/plantilla.xlsx', 'rb')
        simple, _ = extraer_asientos(File(f))

        assert isinstance(simple, pd.DataFrame)
        for col in  ['Fecha', 'Descripción', 'Valor', 'Debe', 'Haber']:
            assert col in simple.columns
        assert len(simple) == 4
        for descr in ['Pan', 'Pizzas Telepizza', 'Gasolina coche', 'Hipoteca']:
            assert descr in list(simple['Descripción'])


    def test_loading_good_file_plantilla_compleja(self):
        f = open('main/tests/data/plantilla.xlsx', 'rb')
        _, compleja = extraer_asientos(File(f))

        assert isinstance(compleja, pd.DataFrame)
        for col in  ['id', 'Fecha', 'Descripción', 'Debe', 'Haber', 'Cuenta']:
            assert col in compleja.columns
        assert len(compleja) == 6
        for descr in ['Cena en el restaurante', 'Cena en el restaurante propina', 'Factura EDP - gas y electricidad', 'Factura EDP - gas', 'Factura EDP - electricidad']:
            assert descr in list(compleja['Descripción'])

    # test on an excel with wrong format, and a non-excel file
    @pytest.mark.parametrize('filename', ['empty_file.xlsx', 'logo.svg'])
    def test_loading_bad_file_plantilla_simple(self, filename):
        f = open('main/tests/data/'+filename, 'rb')
        simple, _ = extraer_asientos(File(f))

        assert isinstance(simple, pd.DataFrame)
        for col in ['Fecha', 'Descripción', 'Valor', 'Debe', 'Haber']:
            assert col in simple.columns
        assert len(simple) == 0

    # test on an excel with wrong format, and a non-excel file
    @pytest.mark.parametrize('filename', ['empty_file.xlsx', 'logo.svg'])
    def test_loading_bad_file_plantilla_compleja(self, filename):
        f = open('main/tests/data/'+filename, 'rb')
        _, compleja = extraer_asientos(File(f))

        assert isinstance(compleja, pd.DataFrame)
        for col in ['id', 'Fecha', 'Descripción', 'Debe', 'Haber', 'Cuenta']:
            assert col in compleja.columns
        assert len(compleja) == 0


class TestCrearAsientos:
    @pytest.fixture
    def create_asiento_simple_dataframe(self, populate_database_cuentas):
        _, cuentas = populate_database_cuentas
        asiento_dict = {
            'Fecha': ['2022-01-10', '2022-01-11', '2022-01-12', '2022-01-13'],
            'Descripción': [ f'Movimiento {n+1}' for n in range(4) ],
            'Valor': [10.10, 11.11, 12.12, 13.13],
            'Debe': [cuentas[0].num]*4,
            'Haber': [cuentas[1].num]*4,
        }
        simple_df = pd.DataFrame(asiento_dict)
        simple_df.Fecha = pd.to_datetime(simple_df.Fecha)

        return simple_df

    @pytest.fixture
    def create_asiento_complejo_dataframe(self, populate_database_cuentas):
        _, cuentas = populate_database_cuentas
        asiento_dict = {
            'id': [1] * 3 + [2] * 3,
            'Fecha': ['2021-01-06'] * 3 + ['2021-01-16'] * 3,
            'Descripción': [ f'Movimiento {n+1}' for n in range(6) ],
            'Debe': [10.5, 0, 0, 25.25, 0, 0],
            'Haber': [0, 5, 5.5, 0, 14, 11.25],
            'Cuenta': [cuentas[1].num]*6,
        }

        compleja_df = pd.DataFrame(asiento_dict)
        compleja_df.Fecha = pd.to_datetime(compleja_df.Fecha)

        return compleja_df

    @pytest.fixture
    def empty_simple_df(self):
        return pd.DataFrame(columns= ['Fecha', 'Descripción', 'Valor', 'Debe', 'Haber'])

    @pytest.fixture
    def empty_compleja_df(self):
        return pd.DataFrame(columns=['id', 'Fecha', 'Descripción', 'Debe', 'Haber', 'Cuenta'])

    def test_crear_asientos_plantilla_simple_ok(self, create_asiento_simple_dataframe, empty_compleja_df):
        simple_df = create_asiento_simple_dataframe
        ok, errores_simple, errores_compleja = crear_asientos(simple_df, empty_compleja_df)

        assert len(ok) == 8
        assert len(errores_simple) == 0
        assert len(errores_compleja) == 0

        # check moviemientos exist in returned list
        descripciones = [ mov.descripcion for mov in ok ]
        for name in simple_df['Descripción']:
            assert name in descripciones

        # check movimientos exist in database
        descripciones_db = [ mov.descripcion for mov in Movimiento.objects.all() ]
        for name in simple_df['Descripción']:
            assert name in descripciones_db

    def test_crear_asientos_plantilla_compleja_ok(self, create_asiento_complejo_dataframe, empty_simple_df):
        compleja_df = create_asiento_complejo_dataframe
        ok, errores_simple, errores_compleja = crear_asientos(empty_simple_df, compleja_df)

        assert len(ok) == 6
        assert len(errores_simple) == 0
        assert len(errores_compleja) == 0

        # check moviemientos exist in returned list
        descripciones = [ mov.descripcion for mov in ok ]
        for name in compleja_df['Descripción']:
            assert name in descripciones

        # check movimientos exist in database
        descripciones_db = [ mov.descripcion for mov in Movimiento.objects.all() ]
        for name in compleja_df['Descripción']:
            assert name in descripciones_db

    @pytest.mark.parametrize('campo, valor, mensaje', [
        ('Fecha', 'wrong date', 'Fecha incorrecta'),
        ('Fecha', None, 'Fecha incorrecta'),
        ('Valor', '2021', 'Valor es incorrecto'),
        ('Valor', None, 'Valor es incorrecto'),
        ('Debe', '999', 'Cuenta no existe'),
        ('Debe', None, 'Cuenta no existe'),
        ('Haber', '999', 'Cuenta no existe'),
        ('Haber', None, 'Cuenta no existe'),
    ])
    def test_crear_asientos_simple_errors(self, create_asiento_simple_dataframe, empty_compleja_df, campo, valor, mensaje):
        simple_df = create_asiento_simple_dataframe
        simple_df.loc[0, campo] = valor
        ok, errores_simple, errores_compleja = crear_asientos(simple_df, empty_compleja_df)

        assert len(ok) == 6
        assert len(errores_simple) == 1
        assert len(errores_compleja) == 0

        assert errores_simple[0]['error'] == mensaje


    @pytest.mark.parametrize('campo, valor, mensaje', [
        ('id', '10.54', "El número de asiento es incorrecto (<class 'str'>)"),
        ('id', None, "El número de asiento es incorrecto (<class 'numpy.float64'>)"),
        ('Fecha', 'wrong date', 'Fecha incorrecta'),
        ('Fecha', None, 'Fecha incorrecta'),
        ('Debe', '2021', 'Debe es incorrecto'),
        ('Debe', None, 'Debe es incorrecto'),
        ('Haber', '2021', 'Haber es incorrecto'),
        ('Haber', None, 'Haber es incorrecto'),
        ('Cuenta', '999', 'Cuenta no existe'),
        ('Cuenta', None, 'Cuenta no existe'),
    ])
    def test_crear_asientos_compleja_errors(self, create_asiento_complejo_dataframe, empty_simple_df, campo, valor, mensaje):
        compleja_df = create_asiento_complejo_dataframe
        compleja_df.loc[0, campo] = valor
        ok, errores_simple, errores_compleja = crear_asientos(empty_simple_df, compleja_df)

        assert len(ok) == 5
        assert len(errores_simple) == 0
        assert len(errores_compleja) == 1

        assert errores_compleja[0]['error'] == mensaje


class TestValidaSimple:
    @pytest.fixture
    def create_movimiento_simple(self, populate_database_cuentas):
        populate_database_cuentas
        cuentas = Cuenta.objects.all()
        movimiento_simple = {
            'fecha': datetime.date(2021, 4, 28),
            'descripcion': 'Movimiento de test',
            'valor': 10.54,
            'debe': cuentas[0].num,
            'haber': cuentas[1].num,
        }
        return movimiento_simple, cuentas

    def test_todo_ok(self, create_movimiento_simple):
        movimiento_simple, cuentas = create_movimiento_simple
        check = valida_simple(movimiento_simple, cuentas)
        assert check == 'ok'

    @pytest.mark.parametrize('campo, valor, mensaje', [
        ('fecha', '2021-12-15', 'Fecha incorrecta'),
        ('fecha', None, 'Fecha incorrecta'),
        ('valor', '2021', 'Valor es incorrecto'),
        ('valor', None, 'Valor es incorrecto'),
        ('debe', '999', 'Cuenta no existe'),
        ('debe', None, 'Cuenta no existe'),
        ('haber', '999', 'Cuenta no existe'),
        ('haber', None, 'Cuenta no existe'),
    ])
    def test_errors(self, create_movimiento_simple, campo, valor, mensaje):
        movimiento_simple, cuentas = create_movimiento_simple
        movimiento_simple[campo] = valor
        check = valida_simple(movimiento_simple, cuentas)
        assert check == mensaje


class TestValidaCompleja:
    @pytest.fixture
    def create_movimiento_complejo(self, populate_database_cuentas):
        populate_database_cuentas
        cuentas = Cuenta.objects.all()
        movimiento_complejo = {
            'num': 5000,
            'fecha': datetime.date(2021, 4, 28),
            'descripcion': 'Movimiento de test',
            'debe': 0,
            'haber': 25.32,
            'cuenta': cuentas[0].num,
        }
        return movimiento_complejo, cuentas

    def test_todo_ok(self, create_movimiento_complejo):
        movimiento_complejo, cuentas = create_movimiento_complejo
        check = valida_compleja(movimiento_complejo, cuentas)
        assert check == 'ok'

    @pytest.mark.parametrize('campo, valor, mensaje', [
        ('num', '10.54', "El número de asiento es incorrecto (<class 'str'>)"),
        ('num', None, "El número de asiento es incorrecto (<class 'NoneType'>)"),
        ('fecha', '2021-12-15', 'Fecha incorrecta'),
        ('fecha', None, 'Fecha incorrecta'),
        ('debe', '2021', 'Debe es incorrecto'),
        ('debe', None, 'Debe es incorrecto'),
        ('haber', '2021', 'Haber es incorrecto'),
        ('haber', None, 'Haber es incorrecto'),
        ('cuenta', '999', 'Cuenta no existe'),
        ('cuenta', None, 'Cuenta no existe'),
    ])
    def test_errors(self, create_movimiento_complejo, campo, valor, mensaje):
        movimiento_complejo, cuentas = create_movimiento_complejo
        movimiento_complejo[campo] = valor
        check = valida_compleja(movimiento_complejo, cuentas)
        assert check == mensaje
