from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0012_create_roomplan'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20)),
                ('discount_type', models.CharField(max_length=10)),
                ('discount_value', models.PositiveIntegerField()),
                ('is_active', models.BooleanField(default=True)),
                ('hotel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coupons', to='booking.hotel')),
            ],
        ),
        migrations.AddConstraint(
            model_name='coupon',
            constraint=models.UniqueConstraint(fields=['hotel', 'code'], name='unique_coupon_per_hotel'),
        ),
    ]
