from django.contrib import admin

# Register your models here.
from .models import Cuenta, Movimiento, FiltroMovimientos,\
    FiltroCuentas, Etiqueta

class MovimientoAdmin(admin.ModelAdmin):
    list_display = ('num', 'fecha', 'descripcion', 'debe', 'haber', 'cuenta')
    list_filter = ['fecha', 'cuenta', 'num']

admin.site.register(Etiqueta)
admin.site.register(Cuenta)
admin.site.register(Movimiento, MovimientoAdmin)
admin.site.register(FiltroMovimientos)
admin.site.register(FiltroCuentas)
