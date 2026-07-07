from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cuentas', '0016_preferenciasvisibilidad'),
    ]

    operations = [
        migrations.AddField(
            model_name='preferenciasvisibilidad',
            name='editar_datos_habilitado',
            field=models.BooleanField(
                default=True,
                verbose_name='Editar datos personales',
                help_text='Permite al paciente cambiar su nombre y correo.',
            ),
        ),
        migrations.AddField(
            model_name='preferenciasvisibilidad',
            name='cambiar_contrasena_habilitado',
            field=models.BooleanField(
                default=True,
                verbose_name='Cambiar contraseña',
                help_text='Permite al paciente actualizar su contraseña.',
            ),
        ),
        migrations.AddField(
            model_name='preferenciasvisibilidad',
            name='configurar_recordatorio_habilitado',
            field=models.BooleanField(
                default=True,
                verbose_name='Configurar recordatorio por correo',
                help_text='Permite al paciente activar o cambiar la hora del recordatorio.',
            ),
        ),
    ]
