from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect
from django.urls import reverse

from main.models import Cuenta, Movimiento
from main.functions import extraer_cuentas, crear_cuentas

# Create your views here.

class IndexView(View):
    def get(self, request, *args, **kwargs):
        context = dict()
        return render(request, 'main/index.html', context)


class CuentasView(View):
    def get(self, request, *args, **kwargs):
        lista_cuentas = Cuenta.objects.all().order_by('num')
        context = {'lista_cuentas': lista_cuentas}
        return render(request, 'main/cuentas.html', context)

    def post(self, request, *args, **kwargs):
        nueva_cuenta = Cuenta(
            num = request.POST['num'].strip(),
            nombre = request.POST['nombre']
        )
        nueva_cuenta.save()

        return HttpResponseRedirect(reverse('main:cuentas'))


class AsientosView(View):
    def get(self, request, *args, **kwargs):
        lista_movimientos = Movimiento.objects.all().order_by('num')
        lista_cuentas = Cuenta.objects.all().order_by('num')
        context = {
            'lista_movimientos': lista_movimientos,
            'lista_cuentas': lista_cuentas
            }
        return render(request, 'main/asientos.html', context)

    def post(self, request, *args, **kwargs):
        asientos_nums = [ movimiento.num for movimiento in Movimiento.objects.all() ]
        num = 0 if len(asientos_nums) == 0 else max(asientos_nums)

        pk_debe = request.POST['debe'].split(':')[0]
        pk_haber = request.POST['haber'].split(':')[0]
        cuenta_debe = Cuenta.objects.get(pk=pk_debe)
        cuenta_haber = Cuenta.objects.get(pk=pk_haber)

        nuevo_debe = Movimiento(
            num = num+1,
            fecha = request.POST['fecha'],
            descripcion = request.POST['descripcion'],
            debe = request.POST['valor'],
            haber = 0,
            cuenta = cuenta_debe,
            )
        nuevo_haber = Movimiento(
            num = num+1,
            fecha = request.POST['fecha'],
            descripcion = request.POST['descripcion'],
            debe = 0, haber = request.POST['valor'],
            cuenta = cuenta_haber,
            )
        nuevo_debe.save()
        nuevo_haber.save()

        print('type cuenta_debe:', type(cuenta_debe))

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
    cuenta.delete()

    return HttpResponseRedirect(reverse('main:cuentas'))


class CargarCuentas(View):
    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse('main:cuentas'))

    def post(self, request, *args, **kwargs):
        excel_data = extraer_cuentas(request.FILES['file'])
        sobreescribir = request.POST.get('sobreescribir', False)

        cuentas_anadidas = crear_cuentas(excel_data, sobreescribir)

        context = { 'cuentas_anadidas': cuentas_anadidas }

        return render(request, 'main/cargar_cuentas.html', context)
