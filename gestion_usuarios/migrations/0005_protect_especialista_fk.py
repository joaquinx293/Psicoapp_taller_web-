from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_usuarios', '0004_alter_invitacionpaciente_id'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='invitacionpaciente',
            name='especialista',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='invitaciones_enviadas',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
