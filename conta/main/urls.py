from django.urls import path

from . import views

app_name = 'main'
urlpatterns = [
#    path('', views.index, name='index'),
#    path('cuentas/', views.cuentas, name='cuentas'),
#    path('asientos/', views.asientos, name='asientos'),
    path('', views.IndexView.as_view(), name='index'),
    path('cuentas/', views.CuentasView.as_view(), name='cuentas'),
    path('asientos/', views.AsientosView.as_view(), name='asientos'),
    path('modificar/asiento/<int:num>/', views.ModificarAsientoView.as_view(), name='modificar_asiento'),
    path('modificar/cuenta/<int:num>/', views.ModificarCuentaView.as_view(), name='modificar_cuenta'),
    path('anadir/movimiento/<int:num>/<slug:fecha>/', views.anadir_movimiento, name='anadir_movimiento'),
    path('borrar/movimiento/<int:pk>/<slug:pagina>/', views.borrar_movimiento, name='borrar_movimiento'),
    path('borrar/movimiento/<int:pk>/<slug:pagina>/<int:num_asiento>/', views.borrar_movimiento, name='borrar_movimiento_complejo'),
    path('borrar/cuenta/<slug:pk>/', views.borrar_cuenta, name='borrar_cuenta'),
    path('cargar/cuentas/', views.CargarCuentas.as_view(), name='cargar_cuentas'),
    path('cargar/asientos/', views.CargarAsientos.as_view(), name='cargar_asientos'),
    path('filtro/cuentas/', views.FiltroCuentas.as_view(), name='filtro_cuentas'),
    path('cuentas/num-<str:fnum>/nombre-<str:fnombre>', views.CuentasView.as_view(), name='cuentas_filtro'),
    path('filtro/asientos/', views.FiltroAsientos.as_view(), name='filtro_asientos'),
    path('asientos/de-<slug:ffecha_ini>-a-<slug:ffecha_fin>/cuenta-<str:fcuenta>/descripcion-<str:fdescripcion>/asiento-<str:fasiento>', views.AsientosView.as_view(), name='asientos_filtro'),
]
