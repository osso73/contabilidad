# Generated by Django 3.2.9 on 2021-12-26 12:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_alter_movimiento_cuenta'),
    ]

    operations = [
        migrations.CreateModel(
            name='FiltroMovimientos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_inicial', models.DateField(default=None, null=True)),
                ('fecha_final', models.DateField(default=None, null=True)),
                ('descripcion', models.CharField(default='', max_length=200)),
                ('cuenta', models.CharField(default='', max_length=10)),
                ('asiento', models.IntegerField(default=None, null=True)),
            ],
        ),
    ]
