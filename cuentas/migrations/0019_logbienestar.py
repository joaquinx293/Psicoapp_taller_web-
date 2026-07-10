from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cuentas', '0018_loginiciosesion'),
    ]

    operations = [
        migrations.CreateModel(
            name='LogBienestar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('herramienta', models.CharField(
                    max_length=20,
                    choices=[
                        ('respiracion', 'Respiración guiada'),
                        ('musica',      'Música ambiental'),
                        ('dato_dia',    'Dato del día / Favoritos'),
                    ],
                )),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('duracion_segundos', models.PositiveIntegerField(
                    blank=True, null=True,
                    help_text='Solo para respiración: segundos de sesión completada.',
                )),
                ('usuario', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='logs_bienestar',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name': 'Log de bienestar',
                'verbose_name_plural': 'Logs de bienestar',
                'ordering': ['-fecha'],
            },
        ),
    ]
