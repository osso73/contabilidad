import openpyxl

from main.models import Cuenta


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
    excel_data.pop(0)

    return excel_data


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
