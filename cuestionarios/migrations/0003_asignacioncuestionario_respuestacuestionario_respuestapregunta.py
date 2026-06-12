from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cuestionarios', '0002_remove_cuestionario_escala_pregunta_escala_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AsignacionCuestionario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_asignacion', models.DateTimeField(auto_now_add=True)),
                ('activa', models.BooleanField(default=True)),
                ('cuestionario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='asignaciones', to='cuestionarios.cuestionario')),
                ('especialista', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='asignaciones_dadas', to=settings.AUTH_USER_MODEL)),
                ('paciente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cuestionarios_asignados', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('paciente', 'cuestionario')},
            },
        ),
        migrations.CreateModel(
            name='RespuestaCuestionario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_respuesta', models.DateTimeField(auto_now_add=True)),
                ('cuestionario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='respuestas', to='cuestionarios.cuestionario')),
                ('paciente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='respuestas', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-fecha_respuesta'],
            },
        ),
        migrations.CreateModel(
            name='RespuestaPregunta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor', models.IntegerField()),
                ('pregunta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cuestionarios.pregunta')),
                ('respuesta_cuestionario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='respuestas_preguntas', to='cuestionarios.respuestacuestionario')),
            ],
        ),
    ]
