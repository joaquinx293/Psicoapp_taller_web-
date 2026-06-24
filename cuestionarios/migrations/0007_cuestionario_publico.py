from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cuestionarios', '0006_nuevos_tipos_pregunta'),
    ]

    operations = [
        migrations.AddField(
            model_name='cuestionario',
            name='publico',
            field=models.BooleanField(
                default=False,
                help_text='Si está activo, todos los especialistas pueden verlo y copiarlo.'
            ),
        ),
    ]
