from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cuentas', '0015_datofavorito'),
    ]

    operations = [
        migrations.CreateModel(
            name='PreferenciasVisibilidad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ver_historial_animo_habilitado', models.BooleanField(default=True, verbose_name='Ver historial de ánimo')),
                ('ver_calendario_habilitado', models.BooleanField(default=True, verbose_name='Ver calendario emocional')),
                ('ver_promedio_animo_habilitado', models.BooleanField(default=True, verbose_name='Ver promedio de ánimo')),
                ('paciente', models.OneToOneField(
                    limit_choices_to={'rol': 'paciente'},
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='preferencias_visibilidad',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name': 'Preferencias de visibilidad',
                'verbose_name_plural': 'Preferencias de visibilidad',
            },
        ),
    ]
