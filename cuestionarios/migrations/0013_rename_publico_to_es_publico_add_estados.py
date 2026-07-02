from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cuestionarios', '0012_cuestionario_id_cuestionario_pregunta_codigo_and_more'),
    ]

    operations = [
        # Renombrar columna publico → es_publico
        migrations.RenameField(
            model_name='cuestionario',
            old_name='publico',
            new_name='es_publico',
        ),
        # Los nuevos estados (publicado, archivado) son solo choices en un CharField;
        # no requieren cambio de esquema porque el campo `estado` ya es CharField(max_length=20).
    ]
