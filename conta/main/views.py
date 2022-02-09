import datetime

from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models.deletion import ProtectedError
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from main.models import Etiqueta, Cuenta, Movimiento, FiltroMovimientos, FiltroCuentas
import main.functions as functions


class IndexView(View):
    """Página principal"""
    def get(self, request, *args, **kwargs):
        context = { 'tab': 'principal' }
        return render(request, 'main/index.html', context)


class CuentasView(LoginRequiredMixin, View):
    """Listado de cuentas. Permite añadir una cuenta nueva."""

    def get(self, request, pag=1, *args, **kwargs):
        lista_cuentas = Cuenta.objects.all()
        lista_etiquetas = Etiqueta.objects.all().order_by('id')

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
        if filtro.etiqueta:
            lista_cuentas = lista_cuentas.filter(etiqueta=filtro.etiqueta)

        # aplica orden
        orden = '-' if not filtro.ascendiente else ''
        lista_cuentas = lista_cuentas.order_by(orden+filtro.campo)

        # cálculo de paginación. 10 resultados por página
        paginacion, num_cuentas, pag, lista_cuentas = functions.get_pagination(pag, lista_cuentas)

        context = {
            'tab': 'cuentas',
            'lista_cuentas': lista_cuentas,
            'lista_etiquetas': lista_etiquetas,
            'filtro': filtro,
            'paginacion': paginacion,
            'pagina_actual': pag,
            'num_cuentas': num_cuentas,
            }
        return render(request, 'main/cuentas.html', context)


    def post(self, request, *args, **kwargs):
        nueva_cuenta = Cuenta(
            num = request.POST['num'].strip(),
            nombre = request.POST['nombre']
        )
        nueva_cuenta.save()

        e = request.POST['etiqueta']
        if len(e):
            nombres_etiquetas = e.split(', ')
            nueva_cuenta.etiqueta.set(nombres_etiquetas)
            nueva_cuenta.save()

        return HttpResponseRedirect(reverse('main:cuentas'))


class AsientosView(LoginRequiredMixin, View):
    """Listado de asientos (o movimientos). Permite añadir un asiento
    simple nuevo.
    """

    def get(self, request, pag=1, *args, **kwargs):
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

        # aplica orden
        orden = '-' if not filtro.ascendiente else ''
        lista_movimientos = lista_movimientos.order_by(orden+filtro.campo)

        # cálculo de paginación. 25 resultados por página
        paginacion, num_movimientos, pag, lista_movimientos = functions.get_pagination(pag, lista_movimientos)

        context = {
            'tab': 'asientos',
            'lista_movimientos': lista_movimientos,
            'lista_cuentas': lista_cuentas,
            'filtro': filtro,
            'total_debe': total_debe,
            'total_haber': total_haber,
            'total': total,
            'paginacion': paginacion,
            'pagina_actual': pag,
            'num_movimientos': num_movimientos,
            }
        return render(request, 'main/asientos.html', context)


    def post(self, request, *args, **kwargs):
        num = functions.max_num_asiento()
        pk_debe = request.POST['debe'].split(':')[0]
        pk_haber = request.POST['haber'].split(':')[0]
        simple = {
            'num': num+1,
            'fecha': request.POST['fecha'],
            'descripcion': request.POST['descripcion'],
            'valor': request.POST['valor'],
            'debe': Cuenta.objects.get(pk=pk_debe),
            'haber': Cuenta.objects.get(pk=pk_haber)
        }

        functions.crea_asiento_simple(simple)

        return HttpResponseRedirect(reverse('main:asientos'))


class ModificarAsientoView(LoginRequiredMixin, View):
    def get(self, request, num):
        lista_movimientos = [ a for a in Movimiento.objects.all() if a.num == num ]
        lista_cuentas = Cuenta.objects.all()

        for movimiento in lista_movimientos:
            fecha_movimiento = f'{movimiento.fecha.year}-{movimiento.fecha.month:02d}-{movimiento.fecha.day:02d}'
            movimiento.fecha = fecha_movimiento

        context = {
            'tab': 'asientos',
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


class ModificarCuentaView(LoginRequiredMixin, View):
    def get(self, request, num):
        context = {
            'tab': 'cuentas',
            'cuenta': Cuenta.objects.get(pk=num),
         }
        return render(request, 'main/modificar_cuenta.html', context)


    def post(self, request, *args, **kwargs):
        cuenta = Cuenta.objects.get(pk=request.POST['num'])
        cuenta.nombre = request.POST['nombre']
        etiquetas = request.POST['etiqueta'].split(', ')

        # validación etiquetas
        lista_etiquetas = Etiqueta.objects.all()
        etiquetas_sin_error = list()
        for e in etiquetas:
            if lista_etiquetas.filter(id=e):
                etiquetas_sin_error.append(e)
        cuenta.etiqueta.set(etiquetas_sin_error)
        cuenta.save()

        return HttpResponseRedirect(reverse('main:cuentas'))

@login_required
def borrar_movimiento(request, pk, pagina, num_asiento=None):
    movimiento = Movimiento.objects.get(pk=pk)
    movimiento.delete()

    if num_asiento:
        return HttpResponseRedirect(reverse(f'main:{pagina}', args=[num_asiento]))
    else:
        return HttpResponseRedirect(reverse(f'main:{pagina}'))


@login_required
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


@login_required
def borrar_cuenta(request, pk):
    cuenta = Cuenta.objects.get(pk=pk)
    try:
        cuenta.delete()

    except ProtectedError as e:
        aviso = {
            'mensaje': "Esta cuenta no se puede borrar, porque tiene movimientos asociados.",
            'nuevo_url': reverse('main:cuentas'),
        }

        context = {
            'tab': 'cuentas',
            'aviso': aviso,
            }
        return render(request, 'main/cuentas.html', context)

    return HttpResponseRedirect(reverse('main:cuentas'))


class CargarCuentas(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse('main:cuentas'))

    def post(self, request, *args, **kwargs):
        datos_excel = functions.extraer_cuentas(request.FILES['file'])
        sobreescribir = request.POST.get('sobreescribir', False)

        cuentas_anadidas, cuentas_error = functions.crear_cuentas(datos_excel, sobreescribir)

        context = {
            'tab': 'cuentas',
            'cuentas_anadidas': cuentas_anadidas,
            'cuentas_error': cuentas_error,
         }

        return render(request, 'main/cargar_cuentas.html', context)


class CargarAsientos(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse('main:asientos'))

    def post(self, request, *args, **kwargs):
        simple, compleja = functions.extraer_asientos(request.FILES['file'])

        movimientos_anadidos, errores_simple, errores_compleja = functions.crear_asientos(simple, compleja)

        context = {
            'tab': 'asientos',
            'movimientos_anadidos': movimientos_anadidos,
            'errores_simple': errores_simple,
            'errores_compleja': errores_compleja,
            'num_errores': len(errores_simple) + len(errores_compleja)
            }

        return render(request, 'main/cargar_asientos.html', context)


@login_required
def filtro_cuentas(request):
    if request.method == 'POST':
        filtro = FiltroCuentas.objects.all()[0]

        if request.POST['accion_filtro'] == 'aplicar':
            filtro.num = request.POST['f_num']
            filtro.nombre = request.POST['f_nombre']
            filtro.etiqueta = request.POST['f_etiqueta']
            filtro.save()
        elif request.POST['accion_filtro'] == 'borrar':
            filtro.num = ''
            filtro.nombre = ''
            filtro.etiqueta = ''
            filtro.save()
        else:
            pass

    return HttpResponseRedirect(reverse('main:cuentas'))


@login_required
def filtro_asientos(request):
    if request.method == 'POST':
        if request.POST['accion_filtro'] == 'aplicar':
            filtro = FiltroMovimientos.objects.all()[0]
            filtro.fecha_inicial = request.POST['f_fecha_inicial']
            filtro.fecha_final = request.POST['f_fecha_final']
            filtro.descripcion = request.POST['f_descripcion']
            filtro.cuenta = request.POST['f_cuenta'].split(':')[0]
            filtro.asiento = request.POST['f_asiento']
            filtro.save()
        elif request.POST['accion_filtro'] == 'borrar':
            filtro = FiltroMovimientos.objects.all()[0]
            filtro.fecha_inicial = ''
            filtro.fecha_final = ''
            filtro.descripcion = ''
            filtro.cuenta = ''
            filtro.asiento = ''
            filtro.save()
        else:
            pass

    return HttpResponseRedirect(reverse('main:asientos'))


@login_required
def cambiar_orden(request, tipo, campo):
    if tipo == 'asientos':
        filtro = FiltroMovimientos.objects.all()[0]
    elif tipo == 'cuentas':
        filtro = FiltroCuentas.objects.all()[0]
    else:
        return HttpResponseRedirect(reverse('main:index'))

    if filtro.campo == campo.lower():
        filtro.ascendiente = not filtro.ascendiente
    else:
        filtro.campo = campo.lower()
        filtro.ascendiente = True

    filtro.save()

    return HttpResponseRedirect(reverse('main:'+tipo))


@login_required
def gestionar_etiqueta(request):
    """Gestiona el formulario para añadir o borrar etiquetas, dentro de la
    vista de cuentas. Solo gestiona peticiones de tipo post.
    """
    if request.method == 'POST':
        accion = request.POST['accion_etiqueta']
        id = request.POST['e_id']
        nombre = request.POST['e_nombre']

        if accion == 'anadir':
            Etiqueta.objects.create(
                id = id,
                nombre = nombre,
            )
        elif accion == 'borrar':
            e = Etiqueta.objects.filter(id=id)
            if len(e):
                e[0].delete()
        else:
            pass

    return HttpResponseRedirect(reverse('main:cuentas'))


class InformesView(LoginRequiredMixin, View):
    """Página principal"""
    def get(self, request, *args, **kwargs):
        lista_cuentas = Cuenta.objects.all().order_by('num')
        lista_etiquetas = Etiqueta.objects.all().order_by('id')

        context = {
            'tab': 'informes',
            'lista_cuentas': lista_cuentas,
            'lista_etiquetas': lista_etiquetas,
            'df': {'empty': True },
            }
        return render(request, 'main/informes.html', context)

    def post(self, request):
        lista_cuentas = Cuenta.objects.all().order_by('num')
        lista_etiquetas = Etiqueta.objects.all().order_by('id')
        movimientos = Movimiento.objects.all()

        movimientos = functions.filtra_movimientos(request.POST, movimientos)
        df = functions.genera_informe(request.POST['f_tipo'], movimientos)
        titulo, subtitulo = functions.titulo_informe(request.POST)
        graph = functions.grafico_informe(df)
        context = {
            'tab': 'informes',
            'lista_cuentas': lista_cuentas,
            'lista_etiquetas': lista_etiquetas,
            'titulo': titulo,
            'subtitulo': subtitulo,
            'df': df,
            'filtro': request.POST,
            'graph': graph,
            }
        return render(request, 'main/informes.html', context)


@login_required
def borrar_multiples_cuentas(request):
    if request.method == 'POST':
        errors = list()
        for checked in request.POST.keys():
            if not checked.startswith('check'):
                continue
            cuenta = Cuenta.objects.get(pk=request.POST[checked])
            try:
                cuenta.delete()
            except ProtectedError as e:
                errors.append(cuenta)
        context = { 'tab': 'cuentas' }

        if errors:
            nombres = [ c.nombre for c in errors ]
            nombres = ", ".join(nombres)
            aviso = {
                'mensaje': f"La(s) siguiente(s) cuentas no se pueden borrar, porque tienen movimientos asociados: {nombres}.",
                'nuevo_url': reverse('main:cuentas'),
            }
            context['aviso'] = aviso
            return render(request, 'main/cuentas.html', context)

    return HttpResponseRedirect(reverse('main:cuentas'))


@login_required
def borrar_multiples_movimientos(request):
    if request.method == 'POST':
        errors = list()
        for checked in request.POST.keys():
            if not checked.startswith('check'):
                continue
            movimiento = Movimiento.objects.get(pk=request.POST[checked])
            movimiento.delete()

    return HttpResponseRedirect(reverse('main:asientos'))
