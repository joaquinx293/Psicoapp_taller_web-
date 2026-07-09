from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cuentas', '0019_logbienestar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='preguntadiaria',
            name='especialista',
            field=models.ForeignKey(
                limit_choices_to={'rol': 'especialista'},
                on_delete=django.db.models.deletion.PROTECT,
                related_name='preguntas_diarias_configuradas',
                to='cuentas.usuario',
            ),
        ),
    ]
