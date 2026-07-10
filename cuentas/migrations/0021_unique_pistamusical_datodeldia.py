from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cuentas', '0020_protect_especialista_fk'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pistamusical',
            name='titulo',
            field=models.CharField(max_length=100, unique=True, verbose_name='Título'),
        ),
        migrations.AlterField(
            model_name='datodeldia',
            name='texto',
            field=models.TextField(unique=True, verbose_name='Texto'),
        ),
    ]
