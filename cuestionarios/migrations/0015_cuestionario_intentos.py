from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cuestionarios', '0014_migrar_estados_simplificados'),
    ]

    operations = [
        migrations.AddField(
            model_name='cuestionario',
            name='permite_reintentos',
            field=models.BooleanField(default=True, verbose_name='Permite reintentos'),
        ),
        migrations.AddField(
            model_name='cuestionario',
            name='intentos_maximos',
            field=models.IntegerField(
                blank=True,
                null=True,
                verbose_name='Intentos máximos',
                help_text='Número máximo de veces que un paciente puede responder este cuestionario. '
                          'Dejar vacío para ilimitado.',
            ),
        ),
    ]
