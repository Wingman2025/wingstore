from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('store', '0003_alter_product_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(),
        ),
    ]
