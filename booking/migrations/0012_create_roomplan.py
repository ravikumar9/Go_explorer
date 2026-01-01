from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0011_alter_roomtype_price_nullable'),
    ]

    operations = [
        migrations.CreateModel(
            name='RoomPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plan_type', models.CharField(max_length=20)),
                ('price', models.DecimalField(max_digits=10, decimal_places=2)),
                ('room_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='plans', to='booking.roomtype')),
            ],
        ),
    ]
