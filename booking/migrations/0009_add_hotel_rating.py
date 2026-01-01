from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0008_update_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='hotel',
            name='rating',
            field=models.PositiveSmallIntegerField(choices=[(3, '3 Star'), (4, '4 Star'), (5, '5 Star')], default=3),
        ),
    ]
