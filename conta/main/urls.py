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
    path('borrar/cuenta/<int:pk>/', views.borrar_cuenta, name='borrar_cuenta'),
]
