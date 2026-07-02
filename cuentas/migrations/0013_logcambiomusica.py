import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cuentas', '0012_pistamusical'),
    ]

    operations = [
        migrations.CreateModel(
            name='LogCambioMusica',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accion', models.CharField(
                    max_length=20,
                    choices=[
                        ('subir',      'Pista subida'),
                        ('eliminar',   'Pista eliminada'),
                        ('activar',    'Pista activada'),
                        ('desactivar', 'Pista desactivada'),
                        ('reordenar',  'Orden modificado'),
                    ],
                )),
                ('pista_titulo', models.CharField(max_length=100, verbose_name='Pista')),
                ('detalle',      models.CharField(max_length=200, blank=True, verbose_name='Detalle')),
                ('fecha',        models.DateTimeField(auto_now_add=True)),
                ('admin', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='logs_musica',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Administrador',
                )),
            ],
            options={
                'verbose_name': 'Log de música',
                'verbose_name_plural': 'Logs de música',
                'ordering': ['-fecha'],
            },
        ),
    ]
