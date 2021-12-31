from django.urls import path

from . import views

app_name = 'main'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('cuentas/', views.CuentasView.as_view(), name='cuentas'),
    path('modificar/cuenta/<int:num>/', views.ModificarCuentaView.as_view(), name='modificar_cuenta'),
    path('borrar/cuenta/<slug:pk>/', views.borrar_cuenta, name='borrar_cuenta'),
    path('cargar/cuentas/', views.CargarCuentas.as_view(), name='cargar_cuentas'),
    path('filtro/cuentas/', views.FiltroCuentasView.as_view(), name='filtro_cuentas'),
    path('cuentas/borrar/filtro/', views.borrar_filtro_cuentas, name='borrar_filtro_cuentas'),

    path('asientos/', views.AsientosView.as_view(), name='asientos'),
    path('modificar/asiento/<int:num>/', views.ModificarAsientoView.as_view(), name='modificar_asiento'),
    path('anadir/movimiento/<int:num>/<slug:fecha>/', views.anadir_movimiento, name='anadir_movimiento'),
    path('borrar/movimiento/<int:pk>/<slug:pagina>/', views.borrar_movimiento, name='borrar_movimiento'),
    path('borrar/movimiento/<int:pk>/<slug:pagina>/<int:num_asiento>/', views.borrar_movimiento, name='borrar_movimiento_complejo'),
    path('cargar/asientos/', views.CargarAsientos.as_view(), name='cargar_asientos'),
    path('filtro/asientos/', views.FiltroAsientosView.as_view(), name='filtro_asientos'),
    path('asientos/borrar/filtro/', views.borrar_filtro_asientos, name='borrar_filtro_asientos'),

    path('cambiar/orden/<str:tipo>/<str:campo>/', views.cambiar_orden, name='cambiar_orden'),
]
