"""
Data migration: convierte registros con estados eliminados al nuevo esquema simplificado.
  en_revision → borrador  (vuelve al flujo de revisión pendiente)
  rechazado   → borrador  (el especialista puede corregir y volver a solicitar)
"""
from django.db import migrations


def simplificar_estados(apps, schema_editor):
    Cuestionario = apps.get_model('cuestionarios', 'Cuestionario')
    Cuestionario.objects.filter(estado='en_revision').update(estado='borrador')
    Cuestionario.objects.filter(estado='rechazado').update(estado='borrador')


def revertir_estados(apps, schema_editor):
    # No se puede saber cuáles eran en_revision vs rechazado originalmente;
    # la reversión deja todo en borrador (aceptable para rollback).
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('cuestionarios', '0013_rename_publico_to_es_publico_add_estados'),
    ]

    operations = [
        migrations.RunPython(simplificar_estados, revertir_estados),
    ]
