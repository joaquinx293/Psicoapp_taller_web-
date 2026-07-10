from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cuestionarios', '0017_asignacion_intentos'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='asignacioncuestionario',
            name='especialista',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='asignaciones_dadas',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='asignacionpendiente',
            name='especialista',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='asignaciones_pendientes_dadas',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
