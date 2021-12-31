# Generated by Django 3.2.10 on 2021-12-31 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_filtrocuentas'),
    ]

    operations = [
        migrations.AddField(
            model_name='filtrocuentas',
            name='ascendiente',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='filtrocuentas',
            name='campo',
            field=models.CharField(choices=[('num', 'num'), ('nombre', 'nombre')], default='NU', max_length=10),
        ),
        migrations.AddField(
            model_name='filtromovimientos',
            name='ascendiente',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='filtromovimientos',
            name='campo',
            field=models.CharField(choices=[('num', 'num'), ('fecha', 'fecha'), ('descripcion', 'descripcion'), ('debe', 'debe'), ('haber', 'haber'), ('cuenta', 'cuenta')], default='NU', max_length=15),
        ),
    ]
