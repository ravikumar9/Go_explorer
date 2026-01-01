from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("booking", "0001_initial_squashed_0013_create_coupon"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=(
                        "CREATE TABLE IF NOT EXISTS booking_hotelimage ("
                        "id integer PRIMARY KEY AUTOINCREMENT, "
                        "hotel_id integer NOT NULL REFERENCES booking_hotel(id) ON DELETE CASCADE, "
                        "image varchar(100) NOT NULL, "
                        "is_primary bool NOT NULL DEFAULT 0"
                        ");"
                    ),
                    reverse_sql=("DROP TABLE IF EXISTS booking_hotelimage;"),
                )
            ],
            state_operations=[
                migrations.CreateModel(
                    name="HotelImage",
                    fields=[
                        (
                            "id",
                            models.BigAutoField(
                                auto_created=True,
                                primary_key=True,
                                serialize=False,
                                verbose_name="ID",
                            ),
                        ),
                        ("image", models.ImageField(upload_to="hotels/")),
                        ("is_primary", models.BooleanField(default=False)),
                        (
                            "hotel",
                            models.ForeignKey(
                                on_delete=django.db.models.deletion.CASCADE,
                                related_name="images",
                                to="booking.hotel",
                            ),
                        ),
                    ],
                )
            ],
        ),
    ]
