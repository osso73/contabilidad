import pandas as pd
from django.core.files import File

from fixtures_functions import *
from main.functions import extraer_cuentas, crear_cuentas

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
        creadas = crear_cuentas(cuentas_df, sobreescribir)
        creadas_nombres = [ c.nombre for c in creadas ]

        # check cuentas exist in returned list
        for nombre in ['Cuenta1', 'Cuenta2']:
            if sobreescribir:
                assert nombre in creadas_nombres
            else:
                assert nombre not in creadas_nombres

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
        creadas = crear_cuentas(cuentas_df, False)
        lista_etiquetas = list()
        for cuenta in creadas:
            etiquetas = cuenta.etiqueta.all()
            for et in etiquetas:
                lista_etiquetas.append(et.id)
        assert 'balance' in lista_etiquetas
        assert 'wrong' not in lista_etiquetas
