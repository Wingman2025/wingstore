from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('store', '0002_create_admin'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]
