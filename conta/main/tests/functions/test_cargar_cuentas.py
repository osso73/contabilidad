import pandas as pd
from django.core.files import File

from fixtures_functions import *
from main.functions import extraer_cuentas, crear_cuentas, valida_cuenta

class TestExtraerCuenta:
    def test_loading_good_file(self):
        f = open('main/tests/data/cuentas.xlsx', 'rb')
        df = extraer_cuentas(File(f))

        assert isinstance(df, pd.DataFrame)
        for col in ['num', 'nombre', 'etiqueta']:
            assert col in df.columns
        assert len(df) == 13
        for num in ['100', '101', '1101', '1110', '1200', '1201', '1210', '300', '312', '324', '15', '2001', '2000']:
            assert num in list(df.num)

    # test on an excel with wrong format, and a non-excel file
    @pytest.mark.parametrize('filename', ['empty_file.xlsx', 'logo.svg'])
    def test_loading_bad_file(self, filename):
        f = open('main/tests/data/'+filename, 'rb')
        df = extraer_cuentas(File(f))

        assert isinstance(df, pd.DataFrame)
        for col in ['num', 'nombre', 'etiqueta']:
            assert col in df.columns
        assert len(df) == 0

    def test_file_with_errors(self):
        f = open('main/tests/data/cuentas_with_errors.xlsx', 'rb')
        df = extraer_cuentas(File(f))
        for col in ['num', 'nombre', 'etiqueta']:
            assert col in df.columns
        assert len(df) == 13


class TestCrearCuentas:
    @pytest.mark.parametrize('sobreescribir', [False, True])
    def test_crear_cuentas_good_data(self, populate_database_cuentas, sobreescribir):
        populate_database_cuentas

        # first two accounts exist alread, so they should not be created
        cuentas_dict = {
            'num': [ f'10{n}' for n in range(6) ],
            'nombre': [ f'Cuenta{n+1}' for n in range(6) ],
            'etiqueta': ['balance']*6
        }
        cuentas_df = pd.DataFrame(cuentas_dict)
        creadas, errors = crear_cuentas(cuentas_df, sobreescribir)
        creadas_nombres = [ c.nombre for c in creadas ]
        creadas_errors = [ c.nombre for c in errors ]

        # check cuentas exist in returned list
        for nombre in ['Cuenta1', 'Cuenta2']:
            if sobreescribir:
                assert nombre in creadas_nombres
                assert nombre not in creadas_errors
            else:
                assert nombre not in creadas_nombres
                assert nombre in creadas_errors
                assert errors[0].error == 'Cuenta ya existente'
                assert errors[1].error == 'Cuenta ya existente'

        for nombre in ['Cuenta3', 'Cuenta4', 'Cuenta5', 'Cuenta6']:
            assert nombre in creadas_nombres

        # check cuentas exist in database
        cuentas_db = Cuenta.objects.all()
        for cuenta in creadas:
            assert cuenta in cuentas_db

    def test_crear_cuentas_wrong_etiqueta(self, populate_database_etiquetas):
        populate_database_etiquetas
        cuentas_dict = {
            'num': ['100', '101', '102', '103', '104', '105'],
            'nombre': ['Caja1', 'Caja2', 'Caja3', 'Caja4', 'Caja5', 'Caja6'],
            'etiqueta': ['balance']*3 + ['wrong']*3
        }
        cuentas_df = pd.DataFrame(cuentas_dict)
        creadas, _ = crear_cuentas(cuentas_df, False)
        lista_etiquetas = list()
        for cuenta in creadas:
            etiquetas = cuenta.etiqueta.all()
            for et in etiquetas:
                lista_etiquetas.append(et.id)
        assert 'balance' in lista_etiquetas
        assert 'wrong' not in lista_etiquetas

    def test_crear_cuentas_with_errors(self, populate_database_etiquetas):
        populate_database_etiquetas
        cuentas_dict = {
            'num': ['100', '100', '102', '103', '104', '105'],
            'nombre': ['Caja1', 'Caja2', '', 'Caja4', 'Caja5', 'Caja6'],
            'etiqueta': ['balance']*5 + ['']
        }
        cuentas_df = pd.DataFrame(cuentas_dict)
        creadas, error = crear_cuentas(cuentas_df, False)
        assert len(creadas) == 5
        assert len(error) == 1
        assert error[0].num == '102'
        cuentas_db = Cuenta.objects.filter(num='102')
        assert len(cuentas_db) == 0


class TestValidaCuenta:
    @pytest.mark.parametrize('num, nombre, msg', [
        ('100', 'Caja1', 'ok'),
        ('101', '', 'Cuenta en blanco no permitida'),
    ])
    def test_valida_cuenta(self, num, nombre, msg):
        cuentas_dict = {
            'num': num,
            'nombre': nombre,
            'etiqueta': ['balance'],
        }
        cuentas_df = pd.DataFrame(cuentas_dict)
        result = valida_cuenta(cuentas_df.loc[0])
        assert result == msg
