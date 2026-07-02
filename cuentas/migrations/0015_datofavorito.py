import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cuentas', '0014_datodelddia'),
    ]

    operations = [
        migrations.CreateModel(
            name='DatoFavorito',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_guardado', models.DateTimeField(auto_now_add=True)),
                ('dato', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='guardado_por',
                    to='cuentas.datodelddia',
                )),
                ('paciente', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='datos_favoritos',
                    limit_choices_to={'rol': 'paciente'},
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name': 'Dato favorito',
                'verbose_name_plural': 'Datos favoritos',
                'ordering': ['-fecha_guardado'],
            },
        ),
        migrations.AddConstraint(
            model_name='datofavorito',
            constraint=models.UniqueConstraint(
                fields=['paciente', 'dato'],
                name='favorito_unico_por_paciente',
            ),
        ),
    ]
