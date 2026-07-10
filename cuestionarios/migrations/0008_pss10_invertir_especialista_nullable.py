import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cuestionarios', '0007_cuestionario_publico'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='cuestionario',
            name='especialista',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='cuestionarios',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        # 2. nuevo campo invertir en Pregunta para pss-10
        migrations.AddField(
            model_name='pregunta',
            name='invertir',
            field=models.BooleanField(
                default=False,
                help_text='Si está activo, el valor se invierte (4 - valor) antes de calcular el puntaje.'
            ),
        ),
    ]
