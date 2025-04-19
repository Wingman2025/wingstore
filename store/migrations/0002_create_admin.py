import os
from django.db import migrations
from django.contrib.auth import get_user_model

def create_admin(apps, schema_editor):
    User = get_user_model()
    username = os.getenv("DJANGO_SUPERUSER_USERNAME")
    email = os.getenv("DJANGO_SUPERUSER_EMAIL")
    password = os.getenv("DJANGO_SUPERUSER_PASSWORD")
    if username and not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)

class Migration(migrations.Migration):
    dependencies = [
        ("store", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_admin, reverse_code=migrations.RunPython.noop),
    ]
