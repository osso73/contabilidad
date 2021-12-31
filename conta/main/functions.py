import datetime
import openpyxl
import pandas as pd
import numpy as np

from django.core.exceptions import ObjectDoesNotExist

from main.models import Cuenta, Movimiento


def extraer_cuentas(file):
    """Extrae las cuentas del fichero excel cargado, y devuelve una lista
    de listas: cada cuenta es representada por una lista del número y la
    descripción.
    """

    cuenta = {}
    wb = openpyxl.load_workbook(file)
    worksheet = wb.active
    excel_data = list()
    for row in worksheet.iter_rows():
        row_data = list()
        for cell in row:
            row_data.append(str(cell.value))
        excel_data.append(row_data)

    # elimina la primera fila, ya que corresponde al título
    if len(excel_data):
        first_row = excel_data.pop(0)
    else:
        first_row = []

    # si el formato no es el esperado devuelve cadena vacía
    if first_row == ['Cuenta', 'Descripción']:
        return excel_data
    else:
        return []


def crear_cuentas(excel_data, sobreescribir):
    """Escribe las cuentas en la base de datos tomando en cuenta el valor de
    sobreescribir para determinar qué hacer en caso de duplicado.
    """

    lista_cuentas = Cuenta.objects.all()
    lista_nums = [ a.num for a in lista_cuentas ]
    cuentas_anadidas = list()

    for cuenta in excel_data:
        num, nombre = cuenta
        if num in lista_nums:
            if sobreescribir:
                cuenta_existente = lista_cuentas.get(pk=num)
                cuenta_existente.nombre = nombre
                cuenta_existente.save()
                cuentas_anadidas.append(cuenta_existente)

        else:
            nueva_cuenta = Cuenta(
                num = num,
                nombre = nombre
            )
            nueva_cuenta.save()
            cuentas_anadidas.append(nueva_cuenta)

    return cuentas_anadidas

def max_num_asiento():
    """Devuelve el número de asiento más alto"""

    asientos_nums = [ movimiento.num for movimiento in Movimiento.objects.all() ]
    num = 0 if len(asientos_nums) == 0 else max(asientos_nums)

    return num


def crea_asiento_simple(num, fecha, descripcion, valor, cuenta_debe, cuenta_haber):
    """Crea un asiento simple de dos movimientos, a partir de los
    datos proporcionados, y los añade a la base de datos. Calcula el
    número de asiento automáticamente.
    """

    nuevo_debe = Movimiento(
        num = num,
        fecha = fecha,
        descripcion = descripcion,
        debe = valor,
        haber = 0,
        cuenta = cuenta_debe,
        )
    nuevo_haber = Movimiento(
        num = num,
        fecha = fecha,
        descripcion = descripcion,
        debe = 0,
        haber = valor,
        cuenta = cuenta_haber,
        )
    nuevo_debe.save()
    nuevo_haber.save()

    return nuevo_debe, nuevo_haber


def extraer_asientos(file):
    """Extrae los datos de la plantilla. Existen dos pestañas: simple, para
    los asientos simples, y compleja para los asientos de 3 o más movimientos.
    La extracción se hace con un dataframe de pandas para cada pestaña, y
    los datos son devueltos como una tupla de dataframes, después de hacer
    comporbaciones y limpieza por si hay errores.

    Retorna dos dataframes de pandas, uno para la plantilla simple y otro
    para la compleja.
    """
    # carga la información del excel. Si la hoja no existe, crea dt en blanco
    try:
        fichero = pd.ExcelFile(file)

        if 'simple' in fichero.sheet_names:
            simple = fichero.parse(sheet_name='simple', usecols='b:f',
                parse_dates=[1], header=2, dtype={'Debe': str, 'Haber': str})
        else:
            simple = pd.DataFrame(columns=['Fecha', 'Descripción', 'Valor', 'Debe', 'Haber'])

        if 'compleja' in fichero.sheet_names:
            compleja = fichero.parse(sheet_name='compleja', usecols='b:g',
                parse_dates=[2], header=2, dtype={'Cuenta': str})
        else:
            compleja = pd.DataFrame(columns=['id', 'Fecha', 'Descripción', 'Debe', 'Haber', 'Cuenta'])


        # elimina los datos incorrectos / incompletos
        for n in simple.index:
            if simple.loc[n].isnull().all():
                simple.drop(labels=n, axis=0, inplace=True)

        for n in compleja.index:
            if compleja.loc[n].isnull().all():
                compleja.drop(labels=n, axis=0, inplace=True)

    except ValueError:
        simple = pd.DataFrame(columns=['Fecha', 'Descripción', 'Valor', 'Debe', 'Haber'])
        compleja = pd.DataFrame(columns=['id', 'Fecha', 'Descripción', 'Debe', 'Haber', 'Cuenta'])

    return simple, compleja


def crear_asientos(simple, compleja):
    """Crea los asientos en la base de datos, a partir de los dataframes
    recibidos. El simple contiene asientos simples, y el compleja contiene
    asientos de 3 o más movimientos. Calcula el número de asiento correcto
    en función de los asientos existentes

    Devuelve una lista de asientos correctos cargados, y dos listas de
    errores, una para cada plantilla.
    """

    max_asiento = max_num_asiento()
    cuentas = Cuenta.objects.all()
    movimientos_anadidos = []
    errores_simple = []
    errores_compleja = []

    for n in simple.index:
        movimiento_simple = {
            'fecha': simple.loc[n]['Fecha'],
            'descripcion': simple.loc[n]['Descripción'],
            'valor': simple.loc[n]['Valor'],
            'debe': simple.loc[n]['Debe'],
            'haber': simple.loc[n]['Haber'],
        }
        check = valida_simple(movimiento_simple, cuentas)
        if check == 'ok':
            max_asiento += 1
            mov_debe, mov_haber = crea_asiento_simple(
                num = max_asiento,
                fecha = movimiento_simple['fecha'],
                descripcion = movimiento_simple['descripcion'],
                valor = movimiento_simple['valor'],
                cuenta_debe = movimiento_simple['debe'],
                cuenta_haber = movimiento_simple['haber'],
                )
            movimientos_anadidos.append(mov_debe)
            movimientos_anadidos.append(mov_haber)

        else:
            movimiento_simple['error'] = check
            errores_simple.append(movimiento_simple)


    for n in compleja.index:
        movimiento_complejo = {
            'num': compleja.loc[n]['id'],
            'fecha': compleja.loc[n]['Fecha'],
            'descripcion': compleja.loc[n]['Descripción'],
            'debe': compleja.loc[n]['Debe'],
            'haber': compleja.loc[n]['Haber'],
            'cuenta': compleja.loc[n]['Cuenta'],
        }
        result_compleja = valida_compleja(movimiento_complejo, cuentas)
        if result_compleja == 'ok':
            movimiento = Movimiento(
                num = max_asiento + movimiento_complejo['num'],
                fecha = movimiento_complejo['fecha'],
                descripcion = movimiento_complejo['descripcion'],
                debe = movimiento_complejo['debe'],
                haber = movimiento_complejo['haber'],
                cuenta = movimiento_complejo['cuenta'],
                )
            movimiento.save()
            movimientos_anadidos.append(movimiento)

        else:
            movimiento_complejo['error'] = result_compleja
            errores_compleja.append(movimiento_complejo)


    return movimientos_anadidos, errores_simple, errores_compleja


def valida_simple(movimiento_simple, cuentas):
    """Valida el movimiento simple, que los campos sean todos correctos.
    En aso de encontrar errores devuelve el error que ha encontrado;
    si todo es correcto devuelve 'ok'
    """

    try:
        movimiento_simple['debe'] = cuentas.get(pk=movimiento_simple['debe'])
        movimiento_simple['haber'] = cuentas.get(pk=movimiento_simple['haber'])
    except ObjectDoesNotExist:
        return 'Cuenta no existe'

    if pd.isnull(movimiento_simple['fecha']) or not isinstance(movimiento_simple['fecha'], (pd.Timestamp, datetime.datetime, datetime.date)):
        return 'Fecha incorrecta'

    if pd.isnull(movimiento_simple['valor']) or not isinstance(movimiento_simple['valor'], (int, float, np.float64, np.int64)):
        return 'Valor es incorrecto'

    movimiento_simple['descripcion'] = str(movimiento_simple['descripcion'])
    movimiento_simple['valor'] = float(movimiento_simple['valor'])

    return 'ok'


def valida_compleja(movimiento_complejo, cuentas):
    """Valida el movimiento complejo, que los campos sean todos correctos.
    En aso de encontrar errores devuelve el error que ha encontrado;
    si todo es correcto devuelve 'ok'
    """

    try:
        movimiento_complejo['cuenta'] = cuentas.get(pk=movimiento_complejo['cuenta'])
    except ObjectDoesNotExist:
        return 'Cuenta no existe'

    if pd.isnull(movimiento_complejo['num']) or not isinstance(movimiento_complejo['num'], (int, np.int64, np.float64)):
        return f'El número de asiento es incorrecto ({type(movimiento_complejo["num"])})'

    if pd.isnull(movimiento_complejo['fecha']) or not isinstance(movimiento_complejo['fecha'], (pd.Timestamp, datetime.datetime, datetime.date)):
        return 'Fecha incorrecta'

    if pd.isnull(movimiento_complejo['debe']) or not isinstance(movimiento_complejo['debe'], (int, float, np.float64, np.int64)):
        return 'Debe es incorrecto'

    if pd.isnull(movimiento_complejo['haber']) or not isinstance(movimiento_complejo['haber'], (int, float, np.float64, np.int64)):
        return 'Haber es incorrecto'

    movimiento_complejo['num'] = int(movimiento_complejo['num'])
    movimiento_complejo['descripcion'] = str(movimiento_complejo['descripcion'])
    movimiento_complejo['debe'] = float(movimiento_complejo['debe'])
    movimiento_complejo['haber'] = float(movimiento_complejo['haber'])

    return 'ok'
