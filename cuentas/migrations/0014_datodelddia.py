from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cuentas', '0013_logcambiomusica'),
    ]

    operations = [
        migrations.CreateModel(
            name='DatoDelDia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('texto',             models.TextField(verbose_name='Texto')),
                ('fuente',            models.CharField(max_length=200, verbose_name='Fuente')),
                ('activo',            models.BooleanField(default=True, verbose_name='Activo')),
                ('fecha_creacion',    models.DateTimeField(auto_now_add=True)),
                ('fecha_modificacion', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Dato del día',
                'verbose_name_plural': 'Datos del día',
                'ordering': ['-fecha_creacion'],
            },
        ),
    ]
