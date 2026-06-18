from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mantenedores', '0001_initial'),
    ]

    operations = [
        # 1. Quitar unique de version (se recrea como unique_together)
        migrations.AlterField(
            model_name='terminoscondiciones',
            name='version',
            field=models.IntegerField(),
        ),
        # 2. Agregar campo rol
        migrations.AddField(
            model_name='terminoscondiciones',
            name='rol',
            field=models.CharField(
                choices=[('paciente', 'Paciente'), ('especialista', 'Especialista')],
                default='paciente',
                max_length=20,
            ),
        ),
        # 3. unique_together (rol, version)
        migrations.AlterUniqueTogether(
            name='terminoscondiciones',
            unique_together={('rol', 'version')},
        ),
    ]
