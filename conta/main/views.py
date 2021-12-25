import datetime

from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models.deletion import ProtectedError

from main.models import Cuenta, Movimiento
import main.functions as functions

# Create your views here.

class IndexView(View):
    """Página principal"""
    def get(self, request, *args, **kwargs):
        context = dict()
        return render(request, 'main/index.html', context)


class CuentasView(View):
    """Listado de cuentas. Permite añadir una cuenta nueva."""

    def get(self, request, fnum='', fnombre='', *args, **kwargs):
        lista_cuentas = Cuenta.objects.all().order_by('num')

        # los valores NULL son convertidos a cadenas vacías
        if fnum == 'NULL':
            fnum = ''
        if fnombre == 'NULL':
            fnombre = ''

        # aplica el filtro
        if fnum:
            lista_cuentas = lista_cuentas.filter(pk=fnum)
        if fnombre:
            lista_cuentas = lista_cuentas.filter(nombre__contains=fnombre)

        context = {
            'lista_cuentas': lista_cuentas,
            'fnum': fnum,
            'fnombre': fnombre,
            }
        return render(request, 'main/cuentas.html', context)


    def post(self, request, *args, **kwargs):
        nueva_cuenta = Cuenta(
            num = request.POST['num'].strip(),
            nombre = request.POST['nombre']
        )
        nueva_cuenta.save()

        return HttpResponseRedirect(reverse('main:cuentas'))


class AsientosView(View):
    """Listado de asientos (o movimientos). Permite añadir un asiento
    simple nuevo.
    """

    def get(self, request, ffecha_ini='', ffecha_fin='', fcuenta='', fdescripcion='', fasiento='', *args, **kwargs):
        lista_movimientos = Movimiento.objects.all().order_by('num')
        lista_cuentas = Cuenta.objects.all().order_by('num')

        # los valores NULL son convertidos a cadenas vacías
        if ffecha_ini == 'NULL':
            ffecha_ini = ''
        if ffecha_fin == 'NULL':
            ffecha_fin = ''
        if fcuenta == 'NULL':
            fcuenta = ''
        if fdescripcion == 'NULL':
            fdescripcion = ''
        if fasiento == 'NULL':
            fasiento = ''

        # aplicación del filtro
        if ffecha_ini:
            fecha = datetime.date.fromisoformat(ffecha_ini)
            lista_movimientos = lista_movimientos.filter(fecha__gt=fecha)
        if ffecha_fin:
            fecha = datetime.date.fromisoformat(ffecha_fin)
            lista_movimientos = lista_movimientos.filter(fecha__lt=fecha)
        if fcuenta:
            lista_movimientos = lista_movimientos.filter(cuenta=fcuenta)
        if fdescripcion:
            lista_movimientos = lista_movimientos.filter(descripcion__contains=fdescripcion)
        if fasiento:
            lista_movimientos = lista_movimientos.filter(num=fasiento)

        total_haber = total_debe = 0
        for m in lista_movimientos:
            total_debe += m.debe
            total_haber += m.haber

        total = total_haber - total_debe

        filtro = {
            'ffecha_ini': ffecha_ini,
            'ffecha_fin': ffecha_fin,
            'fcuenta': fcuenta,
            'fdescripcion': fdescripcion,
            'fasiento': fasiento,
        }

        context = {
            'lista_movimientos': lista_movimientos,
            'lista_cuentas': lista_cuentas,
            'filtro': filtro,
            'total_debe': total_debe,
            'total_haber': total_haber,
            'total': total,
            }
        return render(request, 'main/asientos.html', context)


    def post(self, request, *args, **kwargs):
        num = functions.max_num_asiento()
        pk_debe = request.POST['debe'].split(':')[0]
        pk_haber = request.POST['haber'].split(':')[0]

        functions.crea_asiento_simple(
            num+1,
            request.POST['fecha'],
            request.POST['descripcion'],
            request.POST['valor'],
            Cuenta.objects.get(pk=pk_debe),
            Cuenta.objects.get(pk=pk_haber)
            )

        return HttpResponseRedirect(reverse('main:asientos'))


class ModificarAsientoView(View):
    def get(self, request, num):
        lista_movimientos = [ a for a in Movimiento.objects.all() if a.num == num ]
        lista_cuentas = Cuenta.objects.all()

        for movimiento in lista_movimientos:
            fecha_movimiento = f'{movimiento.fecha.year}-{movimiento.fecha.month:02d}-{movimiento.fecha.day:02d}'
            movimiento.fecha = fecha_movimiento

        context = {
            'num_asiento': num,
            'lista_movimientos': lista_movimientos,
            'lista_cuentas': lista_cuentas
            }
        return render(request, 'main/modificar_asiento.html', context)


    def post(self, request, *args, **kwargs):
        num_items = int((len(request.POST) -1 )/ 7)
        for i in range(num_items):
            movimiento = Movimiento.objects.get(id=request.POST[f'id{i}'])
            movimiento.num = int(request.POST[f'num{i}'])
            movimiento.fecha = request.POST[f'fecha{i}']
            movimiento.descripcion = request.POST[f'descripcion{i}']
            movimiento.debe = float(request.POST[f'debe{i}'])
            movimiento.haber = float(request.POST[f'haber{i}'])
            num_cuenta = int(request.POST[f'cuenta{i}'].split(':')[0])
            cuenta = Cuenta.objects.get(num=num_cuenta)
            movimiento.cuenta = cuenta
            movimiento.save()

        return HttpResponseRedirect(reverse('main:asientos'))


class ModificarCuentaView(View):
    def get(self, request, num):
        context = { 'cuenta': Cuenta.objects.get(pk=num) }
        return render(request, 'main/modificar_cuenta.html', context)


    def post(self, request, *args, **kwargs):
        cuenta = Cuenta.objects.get(pk=request.POST['num'])
        cuenta.nombre = request.POST['nombre']
        cuenta.save()

        return HttpResponseRedirect(reverse('main:cuentas'))


def borrar_movimiento(request, pk, pagina, num_asiento=None):
    movimiento = Movimiento.objects.get(pk=pk)
    movimiento.delete()

    if num_asiento:
        return HttpResponseRedirect(reverse(f'main:{pagina}', args=[num_asiento]))
    else:
        return HttpResponseRedirect(reverse(f'main:{pagina}'))


def anadir_movimiento(request, num, fecha):
    movimiento = Movimiento(
        num = num,
        fecha = fecha,
        descripcion = '',
        debe = 0,
        haber = 0,
        cuenta = Cuenta.objects.all()[0]
    )
    movimiento.save()

    return HttpResponseRedirect(reverse(f'main:modificar_asiento', args=[num]))


def borrar_cuenta(request, pk):
    cuenta = Cuenta.objects.get(pk=pk)
    try:
        cuenta.delete()
    except ProtectedError as e:
        pass    # implementar alguna función para mostrar errores

    return HttpResponseRedirect(reverse('main:cuentas'))


class CargarCuentas(View):
    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse('main:cuentas'))

    def post(self, request, *args, **kwargs):
        datos_excel = functions.extraer_cuentas(request.FILES['file'])
        sobreescribir = request.POST.get('sobreescribir', False)

        cuentas_anadidas = functions.crear_cuentas(datos_excel, sobreescribir)

        context = { 'cuentas_anadidas': cuentas_anadidas }

        return render(request, 'main/cargar_cuentas.html', context)


class CargarAsientos(View):
    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse('main:asientos'))

    def post(self, request, *args, **kwargs):
        simple, compleja = functions.extraer_asientos(request.FILES['file'])

        movimientos_anadidos, errores_simple, errores_compleja = functions.crear_asientos(simple, compleja)

        context = {
            'movimientos_anadidos': movimientos_anadidos,
            'errores_simple': errores_simple,
            'errores_compleja': errores_compleja,
            'num_errores': len(errores_simple) + len(errores_compleja)
            }

        return render(request, 'main/cargar_asientos.html', context)


class FiltroCuentas(View):
    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse('main:cuentas'))

    def post(self, request, *args, **kwargs):
        fnum = request.POST['f_num']
        fnombre = request.POST['f_nombre']
        if not fnum:
            fnum = 'NULL'
        if not fnombre:
            fnombre = 'NULL'

        return HttpResponseRedirect(reverse('main:cuentas_filtro', kwargs={
            'fnum': fnum,
            'fnombre': fnombre
            }))


class FiltroAsientos(View):
    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse('main:asientos'))

    def post(self, request, *args, **kwargs):
        ffecha_ini = request.POST['f_fecha_inicial']
        ffecha_fin = request.POST['f_fecha_final']
        fdescripcion = request.POST['f_descripcion']
        fcuenta = request.POST['f_cuenta'].split(':')[0]
        fasiento = request.POST['f_asiento']

        if not ffecha_ini:
            ffecha_ini = 'NULL'
        if not ffecha_fin:
            ffecha_fin = 'NULL'
        if not fdescripcion:
            fdescripcion = 'NULL'
        if not fcuenta:
            fcuenta = 'NULL'
        if not fasiento:
            fasiento = 'NULL'

        return HttpResponseRedirect(reverse('main:asientos_filtro', kwargs={
            'ffecha_ini': ffecha_ini,
            'ffecha_fin': ffecha_fin,
            'fdescripcion': fdescripcion,
            'fcuenta': fcuenta,
            'fasiento': fasiento,
            }))
