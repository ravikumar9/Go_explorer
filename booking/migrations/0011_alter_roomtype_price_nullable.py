from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0010_add_roomtype_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='roomtype',
            name='price',
            field=models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True),
        ),
    ]
