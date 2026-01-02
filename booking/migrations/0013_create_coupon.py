from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0012_create_roomplan'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=(
                        "CREATE TABLE IF NOT EXISTS booking_coupon ("
                        "id integer PRIMARY KEY AUTOINCREMENT, "
                        "code varchar(20) NOT NULL, "
                        "discount_type varchar(10) NOT NULL, "
                        "discount_value integer NOT NULL, "
                        "is_active bool NOT NULL DEFAULT 1, "
                        "hotel_id integer NOT NULL REFERENCES booking_hotel(id) ON DELETE CASCADE"
                        ");"
                    ),
                    reverse_sql=("DROP TABLE IF EXISTS booking_coupon;"),
                ),
                migrations.RunSQL(
                    sql=(
                        "CREATE UNIQUE INDEX IF NOT EXISTS unique_coupon_per_hotel_idx ON booking_coupon(hotel_id, code);"
                    ),
                    reverse_sql=("DROP INDEX IF EXISTS unique_coupon_per_hotel_idx;"),
                ),
            ],
            state_operations=[
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
            ],
        ),
    ]
