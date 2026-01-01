from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0009_add_hotel_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='roomtype',
            name='base_price',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='roomtype',
            name='room_size_sqft',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
