from django.db import migrations


POINTS = (
    ("terminal-central", "Terminal Central"),
    ("bairro-america", "Bairro América"),
    ("campus-univille", "Campus Univille"),
    ("terminal-norte", "Terminal Norte"),
)


def seed_points(apps, schema_editor):
    point = apps.get_model("rides", "RoutePoint")
    for code, name in POINTS:
        point.objects.using(schema_editor.connection.alias).get_or_create(code=code, defaults={"name": name})


def remove_points(apps, schema_editor):
    # A reversão não pode apagar pontos utilizados: a FK no banco recusará.
    point = apps.get_model("rides", "RoutePoint")
    point.objects.using(schema_editor.connection.alias).filter(code__in=[code for code, _ in POINTS]).delete()


class Migration(migrations.Migration):
    dependencies = [("rides", "0001_initial")]
    operations = [migrations.RunPython(seed_points, remove_points)]
