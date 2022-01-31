import datetime
from io import StringIO

from fixtures_functions import *

from main.functions import filtra_movimientos, titulo_informe, genera_informe, grafico_informe


@pytest.fixture
def empty_filter():
    filtro = {
        'f_fecha_inicial': '',
        'f_fecha_final': '',
        'f_cuenta': '',
        'f_etiqueta': '',
        'f_tipo': 'diario',   # cannot be empty, so I put default value
    }
    return filtro


class TestFiltraMovimientos:
    def test_filtro_fecha_inicial(self, populate_database, empty_filter):
        populate_database
        movimientos = Movimiento.objects.all()
        filtro = empty_filter
        filtro['f_fecha_inicial'] = '2021-12-17'

        movimientos_final = filtra_movimientos(filtro, movimientos)
        descripciones = [ m.descripcion for m in movimientos_final ]
        for name in ['Compra del pan', 'Calcetines y calzoncillos', 'Abrigo de invierno']:
            assert name in descripciones
        assert 'Compra de fruta' not in descripciones

    def test_filtro_fecha_final(self, populate_database, empty_filter):
        populate_database
        movimientos = Movimiento.objects.all()
        filtro = empty_filter
        filtro['f_fecha_final'] = '2021-12-18'

        movimientos_final = filtra_movimientos(filtro, movimientos)
        descripciones = [ m.descripcion for m in movimientos_final ]
        for name in ['Compra de fruta', 'Calcetines y calzoncillos']:
            assert name in descripciones
        for name in ['Compra del pan', 'Abrigo de invierno']:
            assert name not in descripciones

    def test_filtro_cuenta(self, populate_database, empty_filter):
        populate_database
        movimientos = Movimiento.objects.all()
        filtro = empty_filter
        filtro['f_cuenta'] = '100'

        movimientos_final = filtra_movimientos(filtro, movimientos)
        descripciones = [ m.descripcion for m in movimientos_final ]
        for name in ['Compra del pan', 'Compra de fruta']:
            assert name in descripciones
        for name in ['Calcetines y calzoncillos', 'Abrigo de invierno']:
            assert name not in descripciones

    @pytest.mark.parametrize('etiqueta, expected', [
            ('casa', 0), ('balance', 8),
        ])
    def test_filtro_etiqueta(self, populate_database, empty_filter, etiqueta, expected):
        populate_database
        movimientos = Movimiento.objects.all()
        filtro = empty_filter
        filtro['f_etiqueta'] = etiqueta

        movimientos_final = filtra_movimientos(filtro, movimientos)
        assert len(movimientos_final) == expected


class TestGeneraInforme:
    @pytest.fixture
    def populate_db_informes(self, populate_database):
        _, cuentas, _ = populate_database
        adicionales = [
            [5, '2021-01-28', 'Compra del pan', 2.50, 0, cuentas[0]],
            [5, '2021-01-28', 'Compra del pan', 0, 2.50, cuentas[3]],
            [6, '2021-02-15', 'Compra de fruta', 10.75, 0, cuentas[0]],
            [6, '2021-02-15', 'Compra de fruta', 0, 10.75, cuentas[3]],
            [7, '2021-03-18', 'Calcetines y calzoncillos', 15.85, 0, cuentas[1]],
            [7, '2021-03-18', 'Calcetines y calzoncillos', 0, 15.85, cuentas[3]],
            [8, '2021-04-20', 'Abrigo de invierno', 54, 0, cuentas[1]],
            [8, '2021-04-20', 'Abrigo de invierno', 0, 54, cuentas[3]],
        ]
        for num, fecha, descripcion, debe, haber, cuenta in adicionales:
            Movimiento.objects.create(num=num, fecha=fecha,
                descripcion=descripcion, debe=debe, haber=haber, cuenta=cuenta)

    @pytest.mark.parametrize('tipo, length, fecha_col', [
        ('diario', 8, 'fecha'), ('semanal', 7, 'semana'), ('mensual', 5, 'mes'),
        ('trimestral', 3, 'trimestre'), ('anual', 1, 'año')
    ])
    def test_genera_informe(self, populate_db_informes, tipo, length, fecha_col):
        populate_db_informes
        movimientos = Movimiento.objects.all()
        informe = genera_informe(tipo, movimientos)
        assert len(informe) == length
        for col in [fecha_col, 'debe', 'haber', 'total']:
            assert col in informe.columns

    def test_empty_movimientos_list(self):
        movimientos = Movimiento.objects.all()
        informe = genera_informe('diario', movimientos)
        assert isinstance(informe, dict)
        assert informe['empty']

    def test_wrong_type(self, populate_db_informes):
        populate_db_informes
        movimientos = Movimiento.objects.all()
        informe = genera_informe('wrong', movimientos)
        assert informe is None


class TestTituloInforme:
    @pytest.mark.parametrize('tipo', ['diario', 'semanal', 'mensual', 'trimestral', 'anual', 'any string'])
    def test_filtro_empty(self, empty_filter, tipo):
        filtro = empty_filter
        filtro['f_tipo'] = tipo
        titulo, subtitulo = titulo_informe(filtro)
        assert titulo == 'Todas las cuentas'
        assert subtitulo == f'Informe {tipo}, todas las fechas'

    @pytest.mark.parametrize('fecha_ini, fecha_fin, expected_subtitle', [
        ('', '2022-01-29', 'Informe diario, desde el principio hasta 2022-01-29'),
        ('2022-01-29', '', 'Informe diario, desde 2022-01-29 hasta el final'),
        ('2022-01-01', '2022-01-31', 'Informe diario, desde 2022-01-01 hasta 2022-01-31'),
    ], ids=['fecha-inicial', 'fecha-final', 'ambas-fechas'])
    def test_filtro_fechas(self, empty_filter, fecha_ini, fecha_fin, expected_subtitle):
        filtro = empty_filter
        filtro['f_fecha_inicial'] = fecha_ini
        filtro['f_fecha_final'] = fecha_fin
        titulo, subtitulo = titulo_informe(filtro)
        assert titulo == 'Todas las cuentas'
        assert subtitulo == expected_subtitle

    @pytest.mark.parametrize('cuenta, etiqueta, expected_title', [
        ('100: Caja', '', 'Cuenta 100: Caja'),
        ('', 'gastos', 'Cuentas del tipo: Gastos corrientes'),
        ('100: Caja', 'gastos', 'Cuenta 100: Caja'),
    ], ids=['cuenta-solo', 'etiqueta-solo', 'cuenta-y-etiqueta'])
    def test_filtro_cuentas_etiquetas_ok(self, empty_filter, populate_database_cuentas, cuenta, etiqueta, expected_title):
        filtro = empty_filter
        etiquetas, cuentas = populate_database_cuentas
        filtro['f_cuenta'] = cuenta
        filtro['f_etiqueta'] = etiqueta
        titulo, subtitulo = titulo_informe(filtro)
        assert titulo == expected_title
        assert subtitulo == 'Informe diario, todas las fechas'

    @pytest.mark.parametrize('cuenta, etiqueta, expected_title, expected_subtitle', [
        ('500: Not existing', '', 'Cuenta no encontrada', 'Informe diario, todas las fechas'),
        ('', 'wrong', 'Etiqueta no encontrada', 'Informe diario, todas las fechas'),
        ('500: Not existing', 'wrong', 'Cuenta no encontrada', 'Informe diario, todas las fechas'),
    ], ids=['cuenta-solo', 'etiqueta-solo', 'cuenta-y-etiqueta'])
    def test_filtro_cuentas_etiquetas_errors(self, empty_filter, populate_database_cuentas, cuenta, etiqueta, expected_title, expected_subtitle):
        filtro = empty_filter
        etiquetas, cuentas = populate_database_cuentas
        filtro['f_cuenta'] = cuenta
        filtro['f_etiqueta'] = etiqueta
        titulo, subtitulo = titulo_informe(filtro)
        assert titulo == expected_title
        assert subtitulo == expected_subtitle

class TestGraficoInforme:
    def test_empty_df(self):
        df = {'empty': True}
        g = grafico_informe(df)
        assert g is None

    def test_return_graph(self, populate_database):
        populate_database
        movimientos = Movimiento.objects.all()
        informe = genera_informe('diario', movimientos)
        graph = grafico_informe(informe)
        assert isinstance(graph, str)


############################### BORRAR #########################################
def BORRAR_grafico_informe(df):
    if isinstance(df, dict) and df['empty']:
        return None

    periodo = df.columns[0]
    df.index = df[periodo]
    plt.style.use('seaborn')
    fig, ax = plt.subplots(figsize=(10,5))  # Create a figure and an axes.
    df.total.plot.bar()
    ax.set_ylabel('euros')

    imgdata = StringIO()

    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)

    data = imgdata.getvalue()

    return data
