# Generated by Django 3.2.9 on 2021-12-08 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Asiento',
            new_name='Movimiento',
        ),
        migrations.AlterField(
            model_name='cuenta',
            name='nombre',
            field=models.CharField(help_text='Nombre de la cuenta', max_length=50),
        ),
    ]
