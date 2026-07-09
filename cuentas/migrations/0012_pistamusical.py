from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cuentas', '0011_notificacion_solicitante_notificacion_tipo_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PistaMusical',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=100, verbose_name='Título')),
                ('archivo', models.FileField(upload_to='musica/', verbose_name='Archivo de audio')),
                ('orden', models.PositiveIntegerField(default=0, verbose_name='Orden')),
                ('activa', models.BooleanField(default=True, verbose_name='Activa')),
            ],
            options={
                'verbose_name': 'Pista musical',
                'verbose_name_plural': 'Pistas musicales',
                'ordering': ['orden', 'id'],
            },
        ),
    ]
