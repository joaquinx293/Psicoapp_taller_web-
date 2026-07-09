from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cuestionarios', '0016_alter_cuestionario_es_publico_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='asignacioncuestionario',
            name='intentos_maximos',
            field=models.IntegerField(
                default=1,
                verbose_name='Intentos máximos',
                help_text='Número de veces que el paciente puede responder este cuestionario. 0 = ilimitado.',
            ),
        ),
    ]
