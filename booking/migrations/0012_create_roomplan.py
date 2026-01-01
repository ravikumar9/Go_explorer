from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0011_alter_roomtype_price_nullable'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=(
                        "CREATE TABLE IF NOT EXISTS booking_roomplan ("
                        "id integer PRIMARY KEY AUTOINCREMENT, "
                        "plan_type varchar(20) NOT NULL, "
                        "price numeric NOT NULL, "
                        "room_type_id integer NOT NULL REFERENCES booking_roomtype(id) ON DELETE CASCADE"
                        ");"
                    ),
                    reverse_sql=("DROP TABLE IF EXISTS booking_roomplan;"),
                )
            ],
            state_operations=[
                migrations.CreateModel(
                    name='RoomPlan',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('plan_type', models.CharField(max_length=20)),
                        ('price', models.DecimalField(max_digits=10, decimal_places=2)),
                        ('room_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='plans', to='booking.roomtype')),
                    ],
                ),
            ],
        ),
    ]
