import datetime

from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models.deletion import ProtectedError

from main.models import Cuenta, Movimiento, FiltroMovimientos, FiltroCuentas
import main.functions as functions

# Create your views here.

class IndexView(View):
    """Página principal"""
    def get(self, request, *args, **kwargs):
        context = dict()
        return render(request, 'main/index.html', context)


class CuentasView(View):
    """Listado de cuentas. Permite añadir una cuenta nueva."""

    def get(self, request, *args, **kwargs):
        lista_cuentas = Cuenta.objects.all().order_by('num')

        # Si no existe el filtro lo crea, con los valores por defecto
        filtro = FiltroCuentas.objects.all()
        if len(filtro) == 0:
            filtro = FiltroCuentas()
            filtro.save()
        else:
            filtro = filtro[0]

        # aplica el filtro
        if filtro.num:
            lista_cuentas = lista_cuentas.filter(pk=filtro.num)
        if filtro.nombre:
            lista_cuentas = lista_cuentas.filter(nombre__contains=filtro.nombre)

        context = {
            'lista_cuentas': lista_cuentas,
            'filtro': filtro,
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

    def get(self, request, *args, **kwargs):
        lista_movimientos = Movimiento.objects.all().order_by('num')
        lista_cuentas = Cuenta.objects.all().order_by('num')

        # Si no existe el filtro lo crea, con los valores por defecto
        filtro = FiltroMovimientos.objects.all()
        if len(filtro) == 0:
            filtro = FiltroMovimientos()
            filtro.save()
        else:
            filtro = filtro[0]

        # aplicación del filtro
        if filtro.fecha_inicial:
            fecha = datetime.date.fromisoformat(filtro.fecha_inicial)
            lista_movimientos = lista_movimientos.filter(fecha__gte=fecha)
        if filtro.fecha_final:
            fecha = datetime.date.fromisoformat(filtro.fecha_final)
            lista_movimientos = lista_movimientos.filter(fecha__lte=fecha)
        if filtro.cuenta:
            lista_movimientos = lista_movimientos.filter(cuenta=filtro.cuenta)
        if filtro.descripcion:
            lista_movimientos = lista_movimientos.filter(descripcion__contains=filtro.descripcion)
        if filtro.asiento:
            lista_movimientos = lista_movimientos.filter(num=int(filtro.asiento))

        total_haber = total_debe = 0
        for m in lista_movimientos:
            total_debe += m.debe
            total_haber += m.haber

        total = total_haber - total_debe

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
        mensaje = "Esta cuenta no se puede borrar, porque tiene movimientos asociados."
        context = {
            'mensaje': mensaje,
            'nuevo_url': reverse('main:cuentas')
            }
        return render(request, 'main/cuentas.html', context)

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


class FiltroCuentasView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse('main:cuentas'))

    def post(self, request, *args, **kwargs):
        filtro = FiltroCuentas.objects.all()[0]
        filtro.num = request.POST['f_num']
        filtro.nombre = request.POST['f_nombre']

        filtro.save()

        return HttpResponseRedirect(reverse('main:cuentas'))


class FiltroAsientosView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse('main:asientos'))

    def post(self, request, *args, **kwargs):
        filtro = FiltroMovimientos.objects.all()[0]
        filtro.fecha_inicial = request.POST['f_fecha_inicial']
        filtro.fecha_final = request.POST['f_fecha_final']
        filtro.descripcion = request.POST['f_descripcion']
        filtro.cuenta = request.POST['f_cuenta'].split(':')[0]
        filtro.asiento = request.POST['f_asiento']

        filtro.save()

        return HttpResponseRedirect(reverse('main:asientos'))


def borrar_filtro_cuentas(request):
    filtro = FiltroCuentas.objects.all()[0]
    filtro.num = ''
    filtro.nombre = ''

    filtro.save()

    return HttpResponseRedirect(reverse('main:cuentas'))


def borrar_filtro_asientos(request):
    filtro = FiltroMovimientos.objects.all()[0]
    filtro.fecha_inicial = ''
    filtro.fecha_final = ''
    filtro.descripcion = ''
    filtro.cuenta = ''
    filtro.asiento = ''

    filtro.save()

    return HttpResponseRedirect(reverse('main:asientos'))
