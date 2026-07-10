from django.conf import settings
from django.db import migrations


def deduplicar_nombres(apps, schema_editor):
    """
    Renombra cuestionarios duplicados (mismo especialista + mismo nombre)
    añadiendo un sufijo numérico antes de aplicar el unique_together.
    Ej: "Ansiedad", "Ansiedad" → "Ansiedad", "Ansiedad (2)"
    """
    Cuestionario = apps.get_model('cuestionarios', 'Cuestionario')

    # Agrupar por (especialista_id, nombre)
    from collections import defaultdict
    grupos = defaultdict(list)
    for c in Cuestionario.objects.order_by('fecha_creacion', 'id'):
        grupos[(c.especialista_id, c.nombre)].append(c)

    for (esp_id, nombre), items in grupos.items():
        if len(items) > 1:
            # El primero mantiene el nombre; los siguientes reciben sufijo
            for i, cuestionario in enumerate(items[1:], start=2):
                nuevo_nombre = f'{nombre} ({i})'
                # Asegurar que el nuevo nombre tampoco exista
                while Cuestionario.objects.filter(
                    especialista_id=esp_id, nombre=nuevo_nombre
                ).exclude(pk=cuestionario.pk).exists():
                    i += 1
                    nuevo_nombre = f'{nombre} ({i})'
                cuestionario.nombre = nuevo_nombre
                cuestionario.save(update_fields=['nombre'])


class Migration(migrations.Migration):

    dependencies = [
        ('cuestionarios', '0018_protect_especialista_fk'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # 1. Primero limpiar duplicados en los datos existentes
        migrations.RunPython(deduplicar_nombres, migrations.RunPython.noop),
        # 2. Luego aplicar el constraint
        migrations.AlterUniqueTogether(
            name='cuestionario',
            unique_together={('especialista', 'nombre')},
        ),
    ]
